# resources/

Offline installation assets for this skill. Too large for git — archives are
gitignored and are not distributed online yet.

## 1. OrgDb gene-ID conversion packages

| File | Package | R version | Platform |
|---|---|---|---|
| `org.Mm.eg.db_3.22.0_R4.5_win-binary.zip` | org.Mm.eg.db (mouse) | 4.5 | Windows binary |
| `org.Hs.eg.db_3.22.0_R4.5_win-binary.zip` | org.Hs.eg.db (human) | 4.5 | Windows binary |
| `org.Hs.eg.db_3.22.0.tar.gz` | org.Hs.eg.db (human) | >=4.5 | source, cross-platform |

Install from a downloaded archive (R version must match the archive's R version):

```r
install.packages("org.Mm.eg.db_3.22.0_R4.5_win-binary.zip",
                 repos = NULL, type = "win.binary")
```

## 2. r-deps/ — full offline dependency repo (139 packages, ~425 MB)

A complete Windows-binary mini-repository of the skill's entire R dependency
closure (DESeq2, edgeR, limma, clusterProfiler, org.*.eg.db, ggplot2, … —
exact versions battle-tested with these scripts, R 4.5). Use it when
Bioconductor/CRAN is slow or unreachable:

```r
# after downloading and unzipping r-deps:
install.packages(c("DESeq2", "edgeR", "limma", "clusterProfiler", "DOSE",
                   "enrichplot", "org.Mm.eg.db", "org.Hs.eg.db",
                   "pheatmap", "ggplot2", "ggrepel"),
                 repos = "file:///<path-to>/r-deps", type = "win.binary")
```

R resolves the dependency order automatically from the bundled PACKAGES index.

如果 R 版本不是 4.5.x，请改用 `BiocManager::install(...)` 在线安装。
