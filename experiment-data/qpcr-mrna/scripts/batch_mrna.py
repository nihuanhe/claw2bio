"""
mRNA qPCR 批量处理脚本
======================
遍历指定目录下所有 CSV，按文件夹名作为 Figure 名，自动调用 run_mrna.py 中的处理逻辑。

用法：
    python batch_mrna.py "D:/data/mrna-qpcr" --ref-targets GAPDH --overwrite
"""

import argparse
import sys
from pathlib import Path

from run_mrna import process_one, Y_LABEL_DEFAULT, DPI_DEFAULT


def main():
    parser = argparse.ArgumentParser(
        description="批量处理 mRNA qPCR CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python batch_mrna.py "D:/data/mrna-qpcr" --overwrite
  python batch_mrna.py "D:/data/mrna-qpcr" --ref-targets ACTB,TUBB --control Ctrl
""",
    )
    parser.add_argument("root_dir", help="包含各 Figure 子目录的根目录")
    parser.add_argument("--ref-targets", default="GAPDH", help="参考基因 Target 名，多个用逗号分隔")
    parser.add_argument("--control", default=None, help="对照组 Sample 名")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已存在的输出文件")
    parser.add_argument(
        "--y-label", default=Y_LABEL_DEFAULT, help=f"Y 轴标签（默认: {Y_LABEL_DEFAULT}）"
    )
    parser.add_argument("--dpi", type=int, default=DPI_DEFAULT, help="PNG 分辨率（默认 300）")
    args = parser.parse_args()

    root = Path(args.root_dir).resolve()
    if not root.is_dir():
        print(f"错误: 目录不存在: {root}", file=sys.stderr)
        sys.exit(1)

    csv_files = sorted(root.rglob("*.csv"))
    print(f"发现 {len(csv_files)} 个 CSV 文件\n")

    success = 0
    skipped = 0
    for csv_path in csv_files:
        output_dir = csv_path.parent
        figure_name = output_dir.name
        print(f"处理: {figure_name} ({csv_path})")
        try:
            process_one(
                input_csv=csv_path,
                output_dir=output_dir,
                name=figure_name,
                ref_targets=[x.strip() for x in args.ref_targets.split(",") if x.strip()],
                control_sample=args.control,
                y_label=args.y_label,
                dpi=args.dpi,
                overwrite=args.overwrite,
            )
            success += 1
        except FileExistsError as e:
            print(f"  [跳过] {e}")
            skipped += 1
        except Exception as e:
            print(f"  [错误] {e}", file=sys.stderr)

    print(f"\n完成: {success} 个成功, {skipped} 个跳过/存在, {len(csv_files) - success - skipped} 个失败")


if __name__ == "__main__":
    main()
