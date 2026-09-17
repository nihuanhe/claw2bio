"""Stage 00.5 — input inspection & auto-repair for scRNA-seq.

Scans the user-provided input and builds an *ingest plan* (JSON) that the R
stages execute. Every repair is recorded in sample['fixes'] and printed as
[fixed] by the driver.

Handled input zoo (v1):
  1. 10X mtx dir, new format (matrix.mtx[.gz] + barcodes.tsv[.gz] + features.tsv[.gz])
  2. 10X mtx dir, old format (genes.tsv 2 columns)
  3. the above wrapped in .tar/.tar.gz, possibly nested (e.g. .../mm10/...)
  4. 10X h5
  5. h5ad (exported to a 10X-style triplet via anndata into .staging/)
  6. rds / RData (validated later in R stage 01)
  7. plain text matrix .txt/.tsv/.csv (+ .gz) — orientation auto-detected
  8. BGI variant of (1): features columns swapped (symbol in col1) -> gene.column=1
  9. multi-sample mixtures of all the above
"""
import csv
import gzip
import io
import os
import re
import tarfile

ENSEMBL_RE = re.compile(r"^ENS[A-Z]{0,6}\d{6,}(\.\d+)?$")
BARCODE_RE = re.compile(r"^[ACGT]{8,}(-\d+)?$")
MT_PATTERNS = ["^MT-", "^Mt-", "^mt-", "^MT\\."]
TRIPLET = ("matrix.mtx", "barcodes.tsv")
FEATURE_FILES = ("features.tsv", "genes.tsv")
TAR_EXT = (".tar", ".tar.gz", ".tgz")
H5_EXT = (".h5", ".hdf5")
TEXT_EXT = (".txt", ".tsv", ".csv", ".txt.gz", ".tsv.gz", ".csv.gz")
RDS_EXT = (".rds", ".rdata", ".rda")
H5AD_EXT = (".h5ad",)


# ---------------------------------------------------------------- helpers

def _open(path):
    return gzip.open(path, "rt", errors="replace") if path.endswith(".gz") \
        else open(path, "r", errors="replace")


def _base_variant(path):
    """path without .gz, lower-cased basename."""
    b = os.path.basename(path).lower()
    return b[:-3] if b.endswith(".gz") else b


def strip_sample_ext(name):
    for ext in TAR_EXT + H5_EXT + TEXT_EXT + RDS_EXT + H5AD_EXT:
        if name.lower().endswith(ext):
            return name[: -len(ext)]
    return name


def norm_sample_key(name):
    """fuzzy key for metadata matching: no ext, no GSM prefix, lowercase."""
    n = strip_sample_ext(name)
    n = re.sub(r"^GSM\d+_?", "", n, flags=re.I)
    return n.lower()


def _sniff_columns(path, n=2000):
    """Return (n_cols, col1_values, col2_values) from a tsv (gz aware)."""
    col1, col2, ncol = [], [], 0
    with _open(path) as fh:
        for i, line in enumerate(fh):
            if i >= n:
                break
            parts = line.rstrip("\n").split("\t")
            ncol = max(ncol, len(parts))
            col1.append(parts[0])
            if len(parts) > 1:
                col2.append(parts[1])
    return ncol, col1, col2


def _ensembl_frac(values):
    vals = [v for v in values if v]
    if not vals:
        return 0.0
    return sum(1 for v in vals if ENSEMBL_RE.match(v)) / len(vals)


def detect_gene_column(feature_path):
    """Decide which column holds gene symbols. Returns (gene_column, fix_msg|None)."""
    ncol, col1, col2 = _sniff_columns(feature_path)
    if ncol < 2:
        return 1, f"feature file has 1 column -> gene.column=1 ({os.path.basename(feature_path)})"
    f1, f2 = _ensembl_frac(col1), _ensembl_frac(col2)
    if f1 >= 0.5 and f2 < 0.5:
        return 2, None                      # standard 10X: col1=ID, col2=symbol
    if f2 >= 0.5 and f1 < 0.5:
        return 1, (f"feature columns swapped (symbol in col1, ID in col2) "
                   f"-> gene.column=1, BGI-style ({os.path.basename(feature_path)})")
    # both non-ensembl: col1 is usually the safer symbol column (BGI exports)
    return 1, (f"no Ensembl IDs detected in feature file; assuming col1=symbol "
               f"(gene.column=1) ({os.path.basename(feature_path)})")


def sniff_mt_pattern(gene_names):
    """Pick the mt prefix matching the most genes. Returns (pattern, n) or (None, 0)."""
    best, bestn = None, 0
    for pat in MT_PATTERNS:
        n = sum(1 for g in gene_names if re.match(pat, g))
        if n > bestn:
            best, bestn = pat, n
    return best, bestn


def find_triplet_dirs(root):
    """Recursively find dirs containing matrix.mtx(.gz)+barcodes.tsv(.gz)."""
    hits = []
    for dirpath, _dirnames, filenames in os.walk(root):
        bases = {_base_variant(f) for f in filenames}
        if all(any(b == t for b in bases) for t in TRIPLET):
            hits.append(dirpath)
    return hits


def unpack_tar(tar_path, staging):
    dest = os.path.join(staging, "tar_" + strip_sample_ext(os.path.basename(tar_path)))
    if not os.path.exists(dest):
        os.makedirs(dest, exist_ok=True)
        with tarfile.open(tar_path) as tf:
            tf.extractall(dest, filter="data")
    return dest


def export_h5ad(h5ad_path, staging, fixes=None):
    """Export h5ad -> 10X-style triplet via anndata. Returns triplet dir."""
    dest = os.path.join(staging, "h5ad_" + strip_sample_ext(os.path.basename(h5ad_path)))
    done = os.path.join(dest, "matrix.mtx.gz")
    if os.path.exists(done):
        return dest
    os.makedirs(dest, exist_ok=True)
    import anndata  # noqa: driver guarantees availability
    import pandas as pd
    import scipy.io
    adata = anndata.read_h5ad(h5ad_path)
    # scanpy-processed h5ad files usually keep log-normalized values in X and
    # the raw counts in a layer. Exporting X would make R normalize a second
    # time and turn QC (nCount_RNA / percent.mt) into nonsense.
    x, x_from = adata.X, "X"
    for key in ("counts", "count", "raw_counts", "umi_counts"):
        if key in adata.layers:
            x, x_from = adata.layers[key], f"layers['{key}']"
            break
    if fixes is not None and x_from != "X":
        fixes.append(f"h5ad: X was not counts -> exported raw counts from {x_from}")
    # Seurat 5's Read10X only accepts the *new* 10X layout when it is gzipped
    # ("Barcode file missing. Expecting barcodes.tsv.gz"), so write .gz.
    with gzip.open(os.path.join(dest, "matrix.mtx.gz"), "wb") as fh:
        scipy.io.mmwrite(fh, x.T)
    pd.Series(adata.obs.index).to_csv(os.path.join(dest, "barcodes.tsv.gz"),
                                      index=False, header=False, compression="gzip")
    var = adata.var
    gene_id = var["gene_ids"] if "gene_ids" in var.columns else var.index
    feat = pd.DataFrame({"id": gene_id, "symbol": var.index})
    feat.to_csv(os.path.join(dest, "features.tsv.gz"), sep="\t",
                index=False, header=False, compression="gzip")
    return dest


def sniff_text_matrix(path):
    """Detect delimiter + orientation of a plain text matrix.

    Returns (delimiter, transpose, fix_msg|None). transpose=True means genes
    are in columns and the matrix must be transposed in R.
    """
    with _open(path) as fh:
        head = [next(fh) for _ in range(6)]
    first = head[0].rstrip("\n")
    delim = "," if first.count(",") > first.count("\t") else "\t"
    cols = first.split(delim)
    # header row: are its fields (after the first) barcodes or gene names?
    header_fields = cols[1:50]
    bc_frac = sum(1 for v in header_fields if BARCODE_RE.match(v)) / max(len(header_fields), 1)
    ens_frac = sum(1 for v in header_fields if ENSEMBL_RE.match(v)) / max(len(header_fields), 1)
    # first column of data rows
    firstcol = [ln.rstrip("\n").split(delim)[0] for ln in head[1:]]
    fc_ens = sum(1 for v in firstcol if ENSEMBL_RE.match(v)) / len(firstcol)
    fc_bc = sum(1 for v in firstcol if BARCODE_RE.match(v)) / len(firstcol)
    genes_in_rows = (fc_ens > 0.5 or fc_bc < 0.2) and bc_frac < 0.5
    if genes_in_rows:
        return delim, False, None
    return delim, True, ("text matrix appears transposed (genes in columns) "
                         "-> will transpose after read")


# ---------------------------------------------------------------- plan builder

def _classify_10x_dir(dirpath, fixes):
    files = { _base_variant(f): os.path.join(dirpath, f) for f in os.listdir(dirpath) }
    # a 10X dir is only usable with a matrix AND barcodes; checking just the
    # feature file let a half-written export pass as valid input and fail much
    # later inside Read10X with a misleading message
    missing = [n for n in TRIPLET if n not in files]
    if missing:
        raise SystemExit(
            f"ERROR: {dirpath} is not a usable 10X dir: missing {', '.join(missing)} "
            f"(partial/failed export? delete the output .staging/ and rerun)")
    feat = next((files[f] for f in FEATURE_FILES if f in files), None)
    if feat is None:
        return None
    gene_col, msg = detect_gene_column(feat)
    if msg:
        fixes.append(msg)
    # mt sniff on the symbol column (full scan: MT genes sit at the file end)
    _, c1, c2 = _sniff_columns(feat, n=1_000_000)
    symbols = c1 if gene_col == 1 else c2
    mt_pat, mt_n = sniff_mt_pattern(symbols)
    if mt_pat and mt_pat != "^MT-":
        fixes.append(f"mitochondrial prefix looks like {mt_pat} ({mt_n} genes); "
                     f"will auto-select unless --mt-pattern overrides")
    return {"type": "10x_mtx", "path": dirpath, "gene_column": gene_col,
            "mt_hint": mt_pat, "feature_file": feat}


def _classify_file(path, staging, fixes):
    low = path.lower()
    base = os.path.basename(path)
    if low.endswith(TAR_EXT):
        dest = unpack_tar(path, staging)
        hits = find_triplet_dirs(dest)
        if hits:
            if len(hits) > 1:
                fixes.append(f"tar contains {len(hits)} triplet dirs; using {hits[0]}")
            fixes.append(f"unpacked tar -> {dest}")
            info = _classify_10x_dir(hits[0], fixes)
            info["type"] = "10x_mtx"
            return info
        # series-level tar: a bundle of sample FILES (h5/h5ad/rds/text/...)
        items = []
        for f in sorted(os.listdir(dest)):
            fp = os.path.join(dest, f)
            if os.path.isfile(fp) and f.lower().endswith(
                    H5_EXT + H5AD_EXT + RDS_EXT + TEXT_EXT):
                sub_fixes = []
                sub = _classify_file(fp, staging, sub_fixes)
                sub["name"] = strip_sample_ext(f)
                sub["fixes"] = [f"from tar bundle {os.path.basename(path)}"] + sub_fixes
                items.append(sub)
        if items:
            fixes.append(f"tar is a bundle of {len(items)} sample files -> {dest}")
            return {"type": "bundle", "items": items, "fixes": fixes}
        return {"type": "unsupported", "path": path,
                "error": "tar contains no 10X triplet nor recognisable sample files"}
    if low.endswith(H5_EXT):
        return {"type": "10x_h5", "path": path}
    if low.endswith(H5AD_EXT):
        dest = export_h5ad(path, staging, fixes)
        fixes.append(f"h5ad exported via anndata -> {dest} "
                     f"(features written WITHOUT index, gene ids kept in col1)")
        info = _classify_10x_dir(dest, fixes)
        return info
    if low.endswith(RDS_EXT):
        return {"type": "rds", "path": path}
    if any(low.endswith(e) for e in TEXT_EXT):
        delim, transpose, msg = sniff_text_matrix(path)
        if msg:
            fixes.append(msg)
        return {"type": "text", "path": path, "delimiter": delim,
                "transpose": transpose}
    return {"type": "unsupported", "path": path, "error": f"unrecognised extension: {base}"}


def build_plan(input_path, metadata_path, staging):
    """Return the ingest plan dict."""
    samples = []
    warnings = []
    input_path = os.path.abspath(input_path)

    # ---- discover raw sample sources
    sources = []  # (name, path_or_dir, kind)  kind: dir10x|file
    if os.path.isfile(input_path):
        sources.append((strip_sample_ext(os.path.basename(input_path)), input_path, "file"))
    else:
        if find_triplet_dirs_shallow(input_path):
            sources.append((os.path.basename(input_path.rstrip("/\\")), input_path, "dir10x"))
        else:
            subdirs = [os.path.join(input_path, d) for d in sorted(os.listdir(input_path))
                       if os.path.isdir(os.path.join(input_path, d))]
            files = [os.path.join(input_path, f) for f in sorted(os.listdir(input_path))
                     if os.path.isfile(os.path.join(input_path, f))]
            triplet_subdirs = [d for d in subdirs if find_triplet_dirs_shallow(d)]
            if triplet_subdirs:
                for d in triplet_subdirs:
                    sources.append((os.path.basename(d), d, "dir10x"))
            meta_abs = os.path.abspath(metadata_path) if metadata_path else None
            for f in files:
                if meta_abs and os.path.abspath(f) == meta_abs:
                    continue  # the metadata CSV is not a sample
                if "metadata" in os.path.basename(f).lower():
                    continue  # obvious metadata sidecar files
                if f.lower().endswith(TAR_EXT + H5_EXT + TEXT_EXT + RDS_EXT + H5AD_EXT):
                    sources.append((strip_sample_ext(os.path.basename(f)), f, "file"))
            if not sources:
                raise SystemExit(f"ERROR: no recognisable scRNA input under {input_path}")

    # ---- classify each source (bundles expand to multiple samples)
    expanded = []
    for name, path, kind in sources:
        fixes = []
        info = _classify_10x_dir(path, fixes) if kind == "dir10x" \
            else _classify_file(path, staging, fixes)
        if info["type"] == "bundle":
            expanded.extend(info["items"])
            continue
        info["name"] = name
        info["fixes"] = fixes
        expanded.append(info)
    samples = expanded

    # ---- metadata (optional)
    meta = {}
    if metadata_path:
        with open(metadata_path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            cols = {c.lower(): c for c in (reader.fieldnames or [])}
            scol = cols.get("sample") or cols.get("sample_id") or cols.get("id")
            gcol = cols.get("group") or cols.get("condition")
            if not scol or not gcol:
                raise SystemExit("ERROR: metadata CSV needs sample,group columns")
            for row in reader:
                meta[row[scol]] = row[gcol]
        # fuzzy attach
        meta_keys = {norm_sample_key(k): k for k in meta}
        for s in samples:
            key = norm_sample_key(s["name"])
            if key in meta_keys:
                s["group"] = meta[meta_keys[key]]
                if meta_keys[key] != s["name"]:
                    s["fixes"].append(
                        f"metadata sample '{meta_keys[key]}' matched to '{s['name']}'")
        matched = {norm_sample_key(s["name"]) for s in samples if "group" in s}
        unmatched_meta = [k for k in meta_keys if k not in matched]
        if unmatched_meta:
            warnings.append(f"metadata rows with no matching sample: {unmatched_meta}")
        nogroup = [s["name"] for s in samples if "group" not in s]
        if nogroup:
            warnings.append(f"samples without group (exploratory): {nogroup}")

    bad = [s for s in samples if s["type"] == "unsupported"]
    if bad:
        raise SystemExit("ERROR: unsupported inputs: " +
                         "; ".join(f"{s['name']} ({s.get('error','?')})" for s in bad))

    mode = "multi" if len(samples) > 1 else "single"
    if mode == "single" and not metadata_path:
        warnings.append("single-sample exploratory mode (no metadata given)")
    return {"input": input_path, "mode": mode, "samples": samples,
            "warnings": warnings}


def find_triplet_dirs_shallow(dirpath):
    try:
        bases = {_base_variant(f) for f in os.listdir(dirpath)}
    except OSError:
        return False
    return all(any(b == t for b in bases) for t in TRIPLET)
