#!/usr/bin/env python3
"""Build example fixtures (dev-only, not shipped to users).

fixture 1: GSE234527 downsampled (5 samples x ~400 cells x ~2000 genes, 10X mtx.gz)
fixture 4: synthetic BGI (features.tsv.gz with symbol in col1 + MT. genes)

Run:  python examples/_dev/make_fixtures.py
"""
import gzip
import os

import numpy as np
import scipy.io
import scipy.sparse as sp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = r"D:\single_cell_1\GSE234527_RAW"
SAMPLES = ["GSM7470392_352", "GSM7470393_354", "GSM7470394_356",
           "GSM7470395_363", "GSM7470396_365"]
N_CELLS, N_GENES = 400, 2000
rng = np.random.default_rng(42)


def gz_write(path, text):
    with gzip.open(path, "wt") as fh:
        fh.write(text)


def _mmwrite(path, mat):
    """scipy mmwrite silently fails on non-ASCII (Chinese) paths; pass a handle."""
    with open(path, "wb") as fh:
        scipy.io.mmwrite(fh, mat)


def make_fixture_1():
    for s in SAMPLES:
        src = os.path.join(SRC, s)
        dst = os.path.join(ROOT, "1_example_GSE234527_downsampled-10x-mtx",
                           "input", s)
        os.makedirs(dst, exist_ok=True)
        mat = scipy.io.mmread(os.path.join(src, "matrix.mtx.gz")).tocsc()
        with gzip.open(os.path.join(src, "features.tsv.gz"), "rt") as fh:
            feats = [ln.rstrip("\n").split("\t") for ln in fh]
        with gzip.open(os.path.join(src, "barcodes.tsv.gz"), "rt") as fh:
            bcs = [ln.strip() for ln in fh]
        # source is a RAW matrix (mostly empty droplets): keep the REAL cells,
        # i.e. top-N barcodes by detected genes, not random ones
        nfeat = np.asarray((mat > 0).sum(axis=0)).ravel()
        cidx = np.sort(np.argsort(nfeat)[-N_CELLS:])
        # keep all MT- genes + the most-expressed genes
        ncount_g = np.asarray(mat.sum(axis=1)).ravel()
        mt_idx = [i for i, f in enumerate(feats) if f[1].startswith("MT-")]
        top = np.argsort(ncount_g)[-(N_GENES - len(mt_idx)):]
        gidx = np.sort(np.concatenate([mt_idx, top]))
        sub = mat[gidx][:, cidx].tocoo()
        nfeat_sub = np.asarray((sub > 0).sum(axis=0)).ravel()
        print(f"fixture1 {s}: {sub.shape[0]} genes x {sub.shape[1]} cells, "
              f"min nFeature={nfeat_sub.min()}")
        _mmwrite(os.path.join(dst, "matrix.mtx"), sub)
        for f in ("matrix.mtx",):
            with open(os.path.join(dst, f), "rb") as i_, \
                 gzip.open(os.path.join(dst, f + ".gz"), "wb") as o_:
                o_.writelines(i_)
            os.remove(os.path.join(dst, f))
        gz_write(os.path.join(dst, "features.tsv.gz"),
                 "".join("\t".join(feats[i][:3]) + "\n" for i in gidx))
        gz_write(os.path.join(dst, "barcodes.tsv.gz"),
                 "".join(bcs[j] + "\n" for j in cidx))


def make_fixture_4():
    """Synthetic BGI: features col1=symbol col2=id (swapped), MT. mito prefix."""
    dst = os.path.join(ROOT, "4_example_synthetic-BGI", "input", "BGI_sampleA")
    os.makedirs(dst, exist_ok=True)
    n_genes, n_cells = 60, 40
    genes = ([f"MT.{g}" for g in ["ND1", "ND2", "CO1", "CO2", "ATP6", "ATP8"]] +
             [f"GENE{i:03d}" for i in range(1, n_genes - 5)])
    ids = [f"BGI{i:06d}" for i in range(1, n_genes + 1)]
    m = sp.random(n_genes, n_cells, density=0.15, format="coo",
                  random_state=rng, data_rvs=lambda n: rng.integers(1, 50, n))
    _mmwrite(os.path.join(dst, "matrix.mtx"), m)
    for f in ("matrix.mtx",):
        with open(os.path.join(dst, f), "rb") as i_, \
             gzip.open(os.path.join(dst, f + ".gz"), "wb") as o_:
            o_.writelines(i_)
        os.remove(os.path.join(dst, f))
    gz_write(os.path.join(dst, "features.tsv.gz"),
             "".join(f"{g}\t{i}\n" for g, i in zip(genes, ids)))
    gz_write(os.path.join(dst, "barcodes.tsv.gz"),
             "".join(f"BGICELL{j:04d}\n" for j in range(1, n_cells + 1)))
    print(f"fixture4: {n_genes} genes x {n_cells} cells, MT. prefix, col1=symbol")


if __name__ == "__main__":
    make_fixture_1()
    make_fixture_4()
