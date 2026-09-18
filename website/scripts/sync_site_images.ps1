# sync_site_images.ps1 — copy selected REAL example-output images from each
# skill's examples/output into website/public/skills/<skill>/ for the site.
# The selection list below is the single source of truth for "which figure
# types represent each skill on the website". Re-run after re-running a
# skill's examples. Copies only; never modifies the source files.
#
# Usage (from repo root):  powershell -File website/scripts/sync_site_images.ps1

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))   # repo root
$dest = Join-Path $root 'website\public\skills'

# skill => @( ,@( source relpath, dest filename ) )  — leading comma keeps
# single-entry lists nested (PowerShell would otherwise flatten them)
$map = [ordered]@{
  'qpcr-mrna' = @(
    ,@('experiment-data/qpcr-mrna/examples/output/Figure1_IL6_barplot.png', 'Figure1_IL6_barplot.png')
  )
  'qpcr-mtdna' = @(
    ,@('experiment-data/qpcr-mtdna/examples/output/Figure18B.png', 'Figure18B.png')
  )
  'barplot' = @(
    @('figure-generation/barplot/examples/output/data_barplot.png', 'data_barplot.png'),
    @('figure-generation/barplot/examples/output/data_4col_barplot.png', 'data_4col_barplot.png')
  )
  'scRNA-seq' = @(
    @('bioinformatics/sc_RNA_seq/scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/UMAP_by_annotation.png', 'UMAP_by_annotation.png'),
    @('bioinformatics/sc_RNA_seq/scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/UMAP_by_group.png', 'UMAP_by_group.png'),
    @('bioinformatics/sc_RNA_seq/scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/marker_dotplot.png', 'marker_dotplot.png'),
    @('bioinformatics/sc_RNA_seq/scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/marker_heatmap.png', 'marker_heatmap.png'),
    @('bioinformatics/sc_RNA_seq/scRNA-seq/examples/1_example_GSE234527_downsampled-10x-mtx/output/QC_violin_after.png', 'QC_violin_after.png')
  )
  'scRNA-seq-pseudotime' = @(
    @('bioinformatics/sc_RNA_seq/scRNA-seq-pseudotime/examples/2_real_GSE234527/output/trajectory_by_pseudotime.png', 'trajectory_by_pseudotime.png'),
    @('bioinformatics/sc_RNA_seq/scRNA-seq-pseudotime/examples/2_real_GSE234527/output/trajectory_by_cluster.png', 'trajectory_by_cluster.png'),
    @('bioinformatics/sc_RNA_seq/scRNA-seq-pseudotime/examples/2_real_GSE234527/output/gene_HES4_on_trajectory.png', 'gene_HES4_on_trajectory.png')
  )
  'scRNA-seq-virtual-ko' = @(
    @('bioinformatics/sc_RNA_seq/scRNA-seq-virtual-ko/examples/2_real_GSE234527/output/ACTA2_barplot_top20.png', 'ACTA2_barplot_top20.png'),
    @('bioinformatics/sc_RNA_seq/scRNA-seq-virtual-ko/examples/2_real_GSE234527/output/ACTA2_zscore_scatter.png', 'ACTA2_zscore_scatter.png')
  )
  'bulk-RNA-seq' = @(
    @('bioinformatics/bulk_RNA_seq/bulk-RNA-seq/examples/1_example_GSE270189_clean-mouse-3groups/output/Volcano_Mutant_vs_Control.png', 'Volcano.png'),
    @('bioinformatics/bulk_RNA_seq/bulk-RNA-seq/examples/1_example_GSE270189_clean-mouse-3groups/output/MA_Mutant_vs_Control.png', 'MA.png'),
    @('bioinformatics/bulk_RNA_seq/bulk-RNA-seq/examples/1_example_GSE270189_clean-mouse-3groups/output/QC_PCA_plot.png', 'QC_PCA.png'),
    @('bioinformatics/bulk_RNA_seq/bulk-RNA-seq/examples/1_example_GSE270189_clean-mouse-3groups/output/QC_sample_correlation_heatmap.png', 'QC_correlation_heatmap.png'),
    @('bioinformatics/bulk_RNA_seq/bulk-RNA-seq/examples/1_example_GSE270189_clean-mouse-3groups/output/DEG_heatmap.png', 'DEG_heatmap.png')
  )
  'RNA-seq-enrichment' = @(
    @('bioinformatics/bulk_RNA_seq/RNA-seq-enrichment/examples/output/GO_DEG_Mutant_vs_Control_up_BP_dotplot.png', 'GO_BP_dotplot.png'),
    @('bioinformatics/bulk_RNA_seq/RNA-seq-enrichment/examples/output/KEGG_DEG_Mutant_vs_Control_up_dotplot.png', 'KEGG_dotplot.png'),
    @('bioinformatics/bulk_RNA_seq/RNA-seq-enrichment/examples/output/Reactome_DEG_Mutant_vs_Control_up_dotplot.png', 'Reactome_dotplot.png')
  )
  'RNA-seq-gene-plot' = @(
    @('bioinformatics/bulk_RNA_seq/RNA-seq-gene-plot/examples/output/GeneExpr_Trp53_by_group.png', 'GeneExpr_Trp53_by_group.png'),
    @('bioinformatics/bulk_RNA_seq/RNA-seq-gene-plot/examples/output/GeneExpr_compare_Trp53_vs_Gapdh_within_group.png', 'GeneExpr_compare_within_group.png')
  )
  'RNA-seq-GSEA' = @(
    @('bioinformatics/bulk_RNA_seq/RNA-seq-GSEA/examples/output/GSEA_DEG_Mutant_vs_Control_reactome_demo_mmu_top_curve.png', 'GSEA_top_curve.png'),
    @('bioinformatics/bulk_RNA_seq/RNA-seq-GSEA/examples/output/GSEA_DEG_Mutant_vs_Control_reactome_demo_mmu_dotplot.png', 'GSEA_dotplot.png')
  )
  'phylo-tree-build' = @(
    ,@('bioinformatics/phylo-tree/phylo-tree-plot/examples/output/phylo_tree.png', 'phylo_tree.png')
  )
  'phylo-tree-plot' = @(
    ,@('bioinformatics/phylo-tree/phylo-tree-plot/examples/output/phylo_tree.png', 'phylo_tree.png')
  )
  'survival-curve' = @(
    @('figure-generation/survival-curve/examples/output/KM_curve.png', 'KM_curve.png'),
    @('figure-generation/survival-curve/examples/output/cox_forest.png', 'cox_forest.png')
  )
  # clinical-table: table PNG produced separately (Step 2), not synced here.
}

$ok = 0; $miss = 0
foreach ($skill in $map.Keys) {
  $dir = Join-Path $dest $skill
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  foreach ($pair in $map[$skill]) {
    $src = Join-Path $root $pair[0]
    if (Test-Path $src) {
      Copy-Item $src (Join-Path $dir $pair[1]) -Force
      $ok++
    } else {
      Write-Warning "MISSING: $src"
      $miss++
    }
  }
}
Write-Output "synced $ok images -> $dest ($miss missing)"
