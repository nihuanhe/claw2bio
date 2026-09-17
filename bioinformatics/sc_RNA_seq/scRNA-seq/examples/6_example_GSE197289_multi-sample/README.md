# Example 6 — GSE197289: 6-group complex design + SingleR + presto

> 踩坑档案（case file）。数据不进仓库：GEO 下载见 `../manifest.csv`。

## 症状

- 6 个样本目录（CSD/IS/Naive/PBS × 时间 × 性别混杂设计），每组目录结构一致
  但组间比较需求复杂；
- FindAllMarkers 全基因跑非常慢；
- SingleR 安装/参考下载在国内网络下容易卡住。

## 诊断与处理

1. 6 组各为一个样本进 `sample_metadata.csv`，常规流程只到注释为止——
   **组间比例/差异比较是 `scRNA-seq-compare`（规划中）的事**；
2. marker 计算走 presto（本流程默认），比 Seurat wilcox 快一个量级；
   presto 只有 GitHub 源，stage 00 会检查，`--install-deps` 可代装；
3. SingleR 参考（celldex）体积大，国内建议从 COS 镜像安装（见 Download 页）；
4. 组多细胞多时先 `--downsample` 探索聚类结构，再全量跑。

## 运行

```bash
python scripts/run_scrnaseq.py GSE197289/data output_GSE197289 \
  --metadata metadata_GSE197289.csv --organism mouse --overwrite
```
