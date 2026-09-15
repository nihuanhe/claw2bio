# resources/

Prebuilt Bioconductor **OrgDb annotation packages** (gene-ID conversion assets for
this skill). Too large for git — this directory is gitignored; at public launch the
archives are served from Tencent COS (see the Download page).

| File | Package | R version | Platform |
|---|---|---|---|
| `org.Mm.eg.db_3.22.0_R4.5_win-binary.zip` | org.Mm.eg.db (mouse) | 4.5 | Windows binary |
| ` org.Hs.eg.db_3.22.0_R4.5_win-binary.zip`（另有源版 `org.Hs.eg.db_3.22.0.tar.gz`，跨平台 R≥4.5 可源码安装）| org.Hs.eg.db (human) | 4.5 | Windows binary |

Install from a downloaded archive (R version must match the archive's R version):

```r
install.packages("org.Mm.eg.db_3.22.0_R4.5_win-binary.zip",
                 repos = NULL, type = "win.binary")
```

如果 R 版本不一致，请改用 `BiocManager::install("org.Mm.eg.db")` 在线安装。
