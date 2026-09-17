"""Stage 05 — REPORT.md + run_metadata.json writer."""
import datetime
import json
import os
import platform
import subprocess
import sys


def _load(path, default=None):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _r_version(rscript):
    try:
        out = subprocess.run([rscript, "--version"], capture_output=True,
                             text=True, timeout=60)
        return out.stdout.split("\n")[0].strip()
    except Exception:
        return "unknown"


def write_report(out_dir, plan_path, params):
    ck = os.path.join(out_dir, ".checkpoints")
    plan = _load(plan_path, {})
    ingest = _load(os.path.join(ck, "ingest_summary.json"), {})
    qc = _load(os.path.join(ck, "qc_summary.json"), {})
    clu = _load(os.path.join(ck, "cluster_summary.json"), {})
    ann = _load(os.path.join(ck, "annotation_summary.json"), {})
    deps = _load(os.path.join(ck, "deps.json"), {})

    # ---- run_metadata.json
    meta = {
        "skill": "scRNA-seq",
        "version": "0.1.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "platform": platform.platform(),
        "r_version": _r_version(params.get("rscript") or "Rscript"),
        "r_packages": deps,
        "parameters": {k: v for k, v in params.items()
                       if k not in ("input", "output")},
        "input": plan.get("input"),
        "mode": plan.get("mode"),
        "samples": [{"name": s["name"], "type": s["type"],
                     "group": s.get("group"), "fixes": s.get("fixes", [])}
                    for s in plan.get("samples", [])],
        "cells_after_qc": clu.get("n_cells"),
        "n_clusters": clu.get("n_clusters"),
    }
    with open(os.path.join(out_dir, "run_metadata.json"), "w",
              encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)

    # ---- REPORT.md
    L = []
    L.append("# scRNA-seq pipeline REPORT\n")
    L.append(f"- date: {meta['timestamp']}")
    L.append(f"- mode: **{meta['mode']}** "
             f"({'grouped' if any(s.get('group') for s in meta['samples']) else 'exploratory, no group info'})")
    L.append(f"- samples: {len(meta['samples'])} | cells after QC: "
             f"{meta['cells_after_qc']} | clusters: {meta['n_clusters']}\n")

    L.append("\n## Memory notes / 内存提示\n")
    L.append("> merge/integration (and downstream pseudotime) are the "
             "memory-peak steps. All checkpoints live in `.checkpoints/`; "
             "rerun with `--resume` after a crash. 大数据量时合并/整合（以及后续"
             "拟时序）可能爆内存——崩了用 --resume 续跑，或加 --downsample N 先探索。\n")

    L.append("\n## Stage 00.5 — input inspection / 输入体检\n")
    for s in meta["samples"]:
        L.append(f"- **{s['name']}** ({s['type']}"
                 + (f", group={s['group']}" if s.get("group") else "") + ")")
        for fx in s["fixes"]:
            L.append(f"  - [fixed] {fx}")
    for w in plan.get("warnings", []):
        L.append(f"- WARNING: {w}")

    L.append("\n## Stage 02 — QC\n")
    th = qc.get("thresholds", {})
    L.append(f"- thresholds: percent.mt < {th.get('mt_max')}%, "
             f"{th.get('min_features')} < nFeature < {th.get('max_features')}")
    for s, info in (qc.get("samples") or {}).items():
        L.append(f"- {s}: {info.get('cells_before')} -> "
                 f"{info.get('cells_after')} cells "
                 f"({info.get('retention_pct')}%)")
        adv = info.get("advice", [])
        if isinstance(adv, str):  # jsonlite auto_unbox turns 1-elem list into str
            adv = [adv]
        for a in adv:
            L.append(f"  - **advice**: {a}")
    if qc.get("doublet_rate_pct"):
        L.append(f"- doublet rate per sample (%): {qc['doublet_rate_pct']}")

    L.append("\n## Stage 03 — clustering\n")
    L.append(f"- normalization: {clu.get('normalization')} | integration: "
             f"{clu.get('integration')} | resolution: {clu.get('resolution')}")
    L.append("- see `clustree_resolution_scan.png` to tune `--resolution`")

    L.append("\n## Stage 04 — annotation\n")
    if ann.get("mode") == "SingleR":
        # stage04 writes annotation_summary.json with auto_unbox=TRUE, so a
        # single-element JSON array arrives here as a plain str/int. Wrap it
        # back, otherwise join() iterates the characters ("MouseRNAseqData"
        # -> "M, o, u, s, e, ...") and a lone cluster 12 -> "1, 2".
        refs = ann.get("references", [])
        if isinstance(refs, str):
            refs = [refs]
        L.append(f"- SingleR references: {', '.join(refs)}")
        dis = ann.get("refs_disagree_clusters") or []
        if isinstance(dis, (str, int, float)):
            dis = [dis]
        if dis:
            L.append(f"- **clusters where the two references disagree "
                     f"(manual review advised)**: {', '.join(map(str, dis))}")
    else:
        L.append("- annotation skipped; `cell_type_final` falls back to "
                 "`Cluster_N` labels")

    L.append("\n## Manual annotation / 手动注释\n")
    L.append("SingleR is a baseline. To apply your own labels:\n"
             "1. copy `top10_markers.csv` -> `manual_annotation.csv`, keep/make "
             "two columns: `cluster,cell_type` (one row per cluster, your "
             "expert call per cluster).\n"
             "2. run: `Rscript scripts/apply_manual_annotation.R "
             "<output>/annotated_seurat.rds manual_annotation.csv <output>`\n"
             "   (or ask your AI agent: \"用 apply_manual_annotation.R 把我的手动注释 "
             "CSV 应用到 annotated_seurat.rds\")\n"
             "3. `cell_type_final` will be overwritten and the annotated UMAP "
             "regenerated. 优先级：手动注释 > SingleR consensus > Cluster_N。")

    L.append("\n## Output files / 产出文件\n")
    L.append("| file | content |")
    L.append("|---|---|")
    L.append("| `annotated_seurat.rds` | THE deliverable: QC'd, clustered, annotated Seurat v5 object (meta.data: orig.ident/group/seurat_clusters/SingleR_*/cell_type_final) |")
    L.append("| `markers_all.csv`, `top10_markers.csv` | marker tables (presto) |")
    L.append("| `annotation_per_cluster.csv` | per-cluster labels from each reference + agreement flag |")
    L.append("| `QC_violin_before/after.png/pdf` | QC violins |")
    L.append("| `UMAP_*.png/pdf`, `TSNE_*.png/pdf` | embeddings by cluster/sample/group |")
    L.append("| `UMAP_before/after_integration.*` | integration sanity check (multi-sample) |")
    L.append("| `marker_heatmap/dotplot.*` | top markers |")
    L.append("| `run_metadata.json` | machine-readable run record |")
    L.append("| `.checkpoints/` | per-stage rds for `--resume` |")

    L.append("\n## Next steps / 下游 skill\n")
    L.append("- `scRNA-seq-pseudotime` (monocle3): input = `annotated_seurat.rds`")
    L.append("- `scRNA-seq-virtual-ko` (scTenifoldKnk): input = `annotated_seurat.rds` + target gene")
    L.append("- `scRNA-seq-compare` (planned): group comparison on `annotated_seurat.rds`")

    with open(os.path.join(out_dir, "REPORT.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
