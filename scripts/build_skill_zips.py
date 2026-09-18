#!/usr/bin/env python3
"""build_skill_zips.py — package every Claw2Bio skill into a downloadable zip.

Outputs under .build/skill-zips/:
  <slug>.zip             mode B: SKILL.md + README.md + scripts/ + examples/
  <slug>-examples.zip    mode C: the full examples/ tree (only for split skills)

Rules (see plan-skill-packages.md):
  - a `resources/` subtree is dropped only when it exceeds FILE_IN_B (that is the
    R/Python binary dependency mirror); small resource folders stay in the package
  - skills whose examples/ exceed BIG_EXAMPLES are split: mode B keeps code +
    examples/input (+ example files <= FILE_IN_B) plus a generated DATA.md that
    points at the full dataset on COS; mode C carries the whole examples/ tree
  - zips are deterministic (fixed entry timestamps, sorted entries), so unchanged
    sources produce byte-identical output -> stable md5 -> idempotent uploads
  - re-runnable: a per-package source fingerprint lives in .build/skill-zips/.state.json

Usage:
  python scripts/build_skill_zips.py            # build, skip unchanged packages
  python scripts/build_skill_zips.py --force    # rebuild everything
  python scripts/build_skill_zips.py --stage-cos  # also stage COS-bound packages
                                                  # into cos-staging/<skill>/packages/
"""

import csv
import hashlib
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / ".build" / "skill-zips"
STATE = OUT / ".state.json"
MANIFEST = OUT / "manifest.csv"

BIG_EXAMPLES = 50 * 1024 * 1024   # examples above this get split into a mode C package
FILE_IN_B = 20 * 1024 * 1024      # single example/resource file kept in mode B
SERVER_LIMIT = 50 * 1024 * 1024   # packages <= this are served from the website
COS_BASE = "https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com"
SITE_BASE = "https://claw2bio.site/downloads"

SKILLS = {
    "qpcr-mrna": "experiment-data/qpcr-mrna",
    "qpcr-mtdna": "experiment-data/qpcr-mtdna",
    "scRNA-seq": "bioinformatics/sc_RNA_seq/scRNA-seq",
    "scRNA-seq-pseudotime": "bioinformatics/sc_RNA_seq/scRNA-seq-pseudotime",
    "scRNA-seq-virtual-ko": "bioinformatics/sc_RNA_seq/scRNA-seq-virtual-ko",
    "bulk-RNA-seq": "bioinformatics/bulk_RNA_seq/bulk-RNA-seq",
    "RNA-seq-enrichment": "bioinformatics/bulk_RNA_seq/RNA-seq-enrichment",
    "RNA-seq-gene-plot": "bioinformatics/bulk_RNA_seq/RNA-seq-gene-plot",
    "RNA-seq-GSEA": "bioinformatics/bulk_RNA_seq/RNA-seq-GSEA",
    "phylo-tree-build": "bioinformatics/phylo-tree/phylo-tree-build",
    "phylo-tree-plot": "bioinformatics/phylo-tree/phylo-tree-plot",
    "barplot": "figure-generation/barplot",
    "clinical-table": "figure-generation/clinical-table",
    "survival-curve": "figure-generation/survival-curve",
}

EXCLUDE_DIRS = {"__pycache__", ".git", ".ipynb_checkpoints", ".mpl-cache",
                ".checkpoints", ".staging"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db", "markers_all.csv"}
# Regenerable per-run artefacts are never distributed (mirrors root .gitignore:
# examples/**/output/*.rds, *.log, markers_all.csv stay out of git AND out of zips)
EXCLUDE_SUFFIXES = (".rds", ".log")
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def dir_size(path: Path) -> int:
    total = 0
    for dp, _, fs in os.walk(path):
        for f in fs:
            try:
                total += os.path.getsize(os.path.join(dp, f))
            except OSError:
                pass
    return total


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(skill_dir: Path, slug: str, examples_split: bool, drop_resources: bool):
    """Return (entries, skipped) where entries = [(arcname, path)]."""
    entries, skipped = [], []
    for dirpath, dirnames, filenames in os.walk(skill_dir):
        rel_dir = Path(dirpath).relative_to(skill_dir).as_posix()
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        if drop_resources and rel_dir == ".":
            dirnames[:] = [d for d in dirnames if d != "resources"]
        for fn in filenames:
            p = Path(dirpath) / fn
            rel = p.relative_to(skill_dir).as_posix()
            if (fn in EXCLUDE_FILES or fn.startswith(".git") or fn.endswith(".pyc")
                    or fn.endswith(EXCLUDE_SUFFIXES)):
                continue
            if drop_resources and rel.startswith("resources/"):
                skipped.append(rel)
                continue
            if examples_split and rel.startswith("examples/"):
                keep = rel.startswith("examples/input/") or p.stat().st_size <= FILE_IN_B
                if not keep:
                    skipped.append(rel)
                    continue
            entries.append((f"{slug}/{rel}", p))
    entries.sort(key=lambda e: e[0])
    return entries, skipped


def fingerprint(entries, texts=None) -> str:
    h = hashlib.md5()
    for arc, p in entries:
        st = p.stat()
        h.update(f"{arc}:{st.st_size}:{st.st_mtime_ns}\n".encode())
    # generated files (e.g. DATA.md) are part of the package content: a change in
    # the template or in the split result must invalidate the cached package
    for arc, text in sorted((texts or {}).items()):
        h.update(f"{arc}:{len(text)}:{hashlib.md5(text.encode()).hexdigest()}\n".encode())
    return h.hexdigest()


def pkg_url(slug: str, name: str, size: int) -> str:
    """Where a package will be served from: website for small, COS for large."""
    if size <= SERVER_LIMIT:
        return f"{SITE_BASE}/{name}"
    subdir = "data" if name.endswith("-examples.zip") else "zip"
    return f"{COS_BASE}/{slug}/{subdir}/{name}"


def data_md(slug: str, c_name: str, c_size: int) -> str:
    return (
        "# Example data — where is the rest?\n\n"
        f"`{slug}.zip` (this package) carries the skill code plus the small examples:\n"
        "SKILL.md, README.md, scripts/, examples/ (trimmed — example files larger\n"
        "than the per-file limit are not included).\n\n"
        "The complete example dataset (mode C) is a separate archive:\n\n"
        f"  size: ~{c_size / 1048576:.1f} MB\n"
        f"  url : {pkg_url(slug, c_name, c_size)}\n\n"
        "R / Python dependencies are not bundled here — see the skill's README\n"
        "for installation instructions.\n"
    )


def write_zip(zip_path: Path, entries, texts=None) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for arc, p in entries:
            info = zipfile.ZipInfo(arc, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with p.open("rb") as src, zf.open(info, "w") as dst:
                shutil.copyfileobj(src, dst, 1024 * 1024)
        for arc, text in (texts or {}).items():
            info = zipfile.ZipInfo(arc, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, text)


def emit(zip_name: str, entries, texts, force: bool, state: dict):
    """Write one package unless its cached fingerprint still matches.

    Returns (size, md5, action)."""
    fp = fingerprint(entries, texts)
    zip_path = OUT / zip_name
    cached = state.get(zip_name, {})
    if not force and zip_path.exists() and cached.get("fingerprint") == fp:
        return zip_path.stat().st_size, md5_file(zip_path), "unchanged"
    write_zip(zip_path, entries, texts)
    size = zip_path.stat().st_size
    digest = md5_file(zip_path)
    state[zip_name] = {"fingerprint": fp, "md5": digest, "size": size}
    return size, digest, "rebuilt"


def build_one(slug: str, rel_dir: str, force: bool, state: dict):
    skill_dir = REPO / rel_dir
    if not skill_dir.is_dir():
        print(f"[SKIP] {slug}: directory not found ({rel_dir})")
        return []
    examples = skill_dir / "examples"
    examples_bytes = dir_size(examples) if examples.is_dir() else 0
    examples_split = examples_bytes > BIG_EXAMPLES
    resources = skill_dir / "resources"
    drop_resources = resources.is_dir() and dir_size(resources) > FILE_IN_B

    results = []
    # mode C is built first: DATA.md inside the mode B package quotes its real
    # size and final URL, so the split result must be known before B is written.
    if examples_split:
        entries, _ = collect(examples, slug, False, False)
        entries = [(f"{slug}/examples/{Path(arc).relative_to(slug).as_posix()}", p)
                   for arc, p in entries]
        entries.sort(key=lambda e: e[0])
        c_name = f"{slug}-examples.zip"
        c_size, c_md5, c_action = emit(c_name, entries, None, force, state)
        results.append((c_name, c_size, c_md5, "c", c_action))

    entries, skipped = collect(skill_dir, slug, examples_split, drop_resources)
    texts = None
    if examples_split:
        texts = {f"{slug}/DATA.md": data_md(slug, f"{slug}-examples.zip", c_size)}
    b_size, b_md5, b_action = emit(f"{slug}.zip", entries, texts, force, state)
    if skipped:
        b_action = f"{b_action} skipped {len(skipped)} large file(s)"
    results.insert(0, (f"{slug}.zip", b_size, b_md5, "b", b_action))
    return results


def stage_cos(rows) -> list:
    """Copy COS-bound packages into cos-staging/<slug>/{zip,data}/ and register them
    in that skill's manifest.csv (rows already there, e.g. deps, are preserved).

    Directory names follow the convention documented in cos-staging/README.md:
      zip/   per-skill package (mode B)
      data/  full example dataset (mode C)
    """
    staged = []
    for row in rows:
        if int(row["size"]) <= SERVER_LIMIT:
            continue
        name = row["file"]
        subdir = "data" if name.endswith("-examples.zip") else "zip"
        slug = name[:-4].replace("-examples", "")
        dest_dir = REPO / "cos-staging" / slug / subdir
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / name
        if not (dest.exists() and dest.stat().st_size == int(row["size"])
                and md5_file(dest) == row["md5"]):
            shutil.copy2(OUT / name, dest)

        manifest = dest_dir.parent / "manifest.csv"
        rel = f"{subdir}/{name}"
        entries = []
        if manifest.exists():
            with manifest.open(newline="", encoding="utf-8") as f:
                entries = [r for r in csv.DictReader(f) if r.get("file") != rel]
        entries.append({"file": rel, "md5": row["md5"], "size": row["size"],
                        "example": row["example"], "note": row["note"]})
        entries.sort(key=lambda r: r["file"])
        with manifest.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["file", "md5", "size", "example", "note"])
            writer.writeheader()
            writer.writerows(entries)
        staged.append(f"cos-staging/{slug}/{rel}")
    return staged


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    force = "--force" in sys.argv
    stage = "--stage-cos" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    state = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            state = {}

    rows = []
    print(f"{'package':<38}{'MB':>9}  {'target':<8}{'action'}")
    print("-" * 78)
    for slug, rel_dir in SKILLS.items():
        for zip_name, size, digest, mode, action in build_one(slug, rel_dir, force, state):
            target = "server" if size <= SERVER_LIMIT else "COS"
            rows.append({
                "file": zip_name,
                "md5": digest,
                "size": size,
                "example": "yes" if mode == "c" else "no",
                "note": f"mode {'C full examples' if mode == 'c' else 'B package'} -> {target}",
            })
            print(f"{zip_name:<38}{size / 1048576:9.2f}  {target:<8}{action}")

    with MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "md5", "size", "example", "note"])
        w.writeheader()
        w.writerows(rows)
    STATE.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    n_server = sum(1 for r in rows if r["size"] <= SERVER_LIMIT)
    total = sum(r["size"] for r in rows)
    print("-" * 78)
    print(f"{len(rows)} packages, {total / 1048576:.2f} MB total "
          f"({n_server} -> server, {len(rows) - n_server} -> COS)")
    print(f"[manifest] {MANIFEST}")
    if stage:
        staged = stage_cos(rows)
        for s in staged:
            print(f"[staged] {s}")
        print(f"[stage] {len(staged)} package(s) registered for COS")


if __name__ == "__main__":
    main()
