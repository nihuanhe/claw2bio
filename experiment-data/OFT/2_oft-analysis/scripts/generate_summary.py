#!/usr/bin/env python3
"""
OFT 汇总表生成器
扫描目录树中所有 arena_*.csv，按实验组和时间点自动汇总。

用法:
    python generate_summary.py <results_dir> [--output summary.csv]

输入:
    results_dir: 包含 arena_*.csv 的目录树根

输出:
    汇总 CSV，列：实验组,时间点,文件名,数据点,总距离(cm),中心进入次数,中心时间(%),静止时间(s),WARNING数量,备注

目录结构推断规则:
    - 文件名: arena_{样本名}.csv → 样本名
    - 父目录: 时间点（如 Day7, Day14）
    - 父父目录/同级目录名包含"Day"的: 实验组（如 CT26原位癌, 脑区注射）
"""

import csv
import os
import re
from argparse import ArgumentParser
from collections import defaultdict


def parse_arena_csv(filepath):
    """
    解析 arena_*.csv，提取主指标、验证警告数、速度分布数据点。

    Returns:
        dict or None if parse fails
    """
    result = {
        "total_distance": "",
        "entries_in_center": "",
        "rest_time": "",
        "time_in_center": "",
        "n_data_points": "",
        "n_warnings": 0,
        "warning_details": [],
    }

    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)

    section = None
    for row in rows:
        if not row or all(c.strip() == "" for c in row):
            continue

        first = row[0].strip() if row[0] else ""

        # 检测 Section 切换
        if first.startswith("[Primary Metrics]"):
            section = "primary"
            continue
        elif first.startswith("[Validation Checks]"):
            section = "validation"
            continue
        elif first.startswith("[Speed Distribution]"):
            section = "speed"
            continue
        elif first.startswith("[WARNINGS]"):
            section = "warnings"
            continue
        elif first.startswith("[Run Parameters]"):
            section = None
            continue

        if section == "primary":
            if first == "Total distance":
                result["total_distance"] = row[1].strip() if len(row) > 1 else ""
            elif first == "Entries in center":
                result["entries_in_center"] = row[1].strip() if len(row) > 1 else ""
            elif first == "Rest time":
                result["rest_time"] = row[1].strip() if len(row) > 1 else ""
            elif first == "Time in center":
                result["time_in_center"] = row[1].strip() if len(row) > 1 else ""

        elif section == "validation":
            if first != "Check Item" and len(row) >= 6:
                status = row[5].strip() if len(row) > 5 else ""
                if status == "WARN":
                    result["n_warnings"] += 1
                    try:
                        check_name = row[0].strip()
                        result["warning_details"].append(check_name)
                    except (IndexError, ValueError):
                        pass

        elif section == "speed":
            if first == "Sample count (speeds)":
                result["n_data_points"] = row[1].strip() if len(row) > 1 else ""

        elif section == "warnings":
            pass  # 已从 Validation Checks 节计数，此处跳过

    return result


def detect_experiment_group(parent_dir, grandparent_dir, arena_basename):
    """
    从目录结构推断实验组。

    规则:
    1. 如果父目录名不含 "Day" → 父目录可能是实验组，父父目录是更上级
    2. 否则 → 父父目录名是实验组

    特殊处理：脑区注射目录下子目录名为"脑区注射-Day7"等，
    其父目录"脑区注射"就是实验组。
    """
    gp = os.path.basename(grandparent_dir)
    pt = os.path.basename(parent_dir)

    # 如果第3级（grandparent）有有意义的名字，用它作为实验组
    # 排除 "results" 等泛用名
    if gp.lower() in ("results", "result", "output", "data", ""):
        return "Unknown", pt

    return gp, pt


def generate_summary(results_dir, output_path):
    """
    主函数：扫描 → 解析 → 汇总 → 输出
    """
    records = []

    for dirpath, _, filenames in os.walk(results_dir):
        for fname in filenames:
            if not fname.startswith("arena_") or not fname.endswith(".csv"):
                continue

            filepath = os.path.join(dirpath, fname)
            data = parse_arena_csv(filepath)

            # 样本名：去掉 "arena_" 前缀和 ".csv" 后缀
            sample_name = fname[6:-4]

            # 目录结构推断
            parent_dir = dirpath
            grandparent_dir = os.path.dirname(dirpath)

            # 实验组和时间点
            gp_name = os.path.basename(grandparent_dir)
            pt_name = os.path.basename(parent_dir)

            # 处理"脑区注射"这种嵌套情况
            # gp_name 可能是 "脑区注射"，pt_name 可能是 "脑区注射-Day7"
            if gp_name.lower() in ("results", "result", "", "."):
                gp_name = pt_name  # 父目录就是实验组
                pt_name = "—"

            # 如果父目录名包含实验组名+连字符，分离
            # e.g. "脑区注射-Day7" → 实验组="脑区注射", 时间点="Day7"
            if gp_name and pt_name.startswith(gp_name + "-"):
                pt_suffix = pt_name[len(gp_name) + 1:]
                pt_name = pt_suffix
            elif gp_name and pt_name.startswith(gp_name):
                pass  # 保持原样

            # 生成备注
            warning_details = data.get("warning_details", [])
            if warning_details:
                # 简化 WARNING 名为简短备注
                short_map = {
                    "Mean speed": "均速",
                    "Max instantaneous speed": "速度",
                    "Max acceleration": "加速度",
                    "Burst ratio (>30 cm/s)": "burst",
                    "Rest ratio (<1 cm/s)": "rest",
                    "P99/P95 speed ratio": "P99/P95",
                }
                short_notes = []
                for w in warning_details:
                    short_notes.append(short_map.get(w, w))
                note = "/".join(short_notes) + "超标" if short_notes else ""
            else:
                note = ""

            records.append({
                "实验组": gp_name,
                "时间点": pt_name,
                "文件名": sample_name,
                "数据点": data.get("n_data_points", ""),
                "总距离(cm)": data.get("total_distance", ""),
                "中心进入次数": data.get("entries_in_center", ""),
                "中心时间(%)": data.get("time_in_center", ""),
                "静止时间(s)": data.get("rest_time", ""),
                "WARNING数量": data.get("n_warnings", 0),
                "备注": note,
            })

    if not records:
        print(f"[警告] 在 {results_dir} 中未找到任何 arena_*.csv 文件")
        return

    # 排序：按实验组 → 时间点 → 文件名
    def sort_key(r):
        # 尝试将时间点中的数字提取出来排序
        pt = r["时间点"]
        nums = re.findall(r"\d+", pt)
        pt_order = int(nums[0]) if nums else 0
        return (r["实验组"], pt_order, r["文件名"])

    records.sort(key=sort_key)

    # 写入 CSV
    fieldnames = [
        "实验组", "时间点", "文件名", "数据点",
        "总距离(cm)", "中心进入次数", "中心时间(%)", "静止时间(s)",
        "WARNING数量", "备注",
    ]

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"汇总表已保存: {output_path}")
    print(f"共 {len(records)} 条记录")

    # 按实验组统计
    groups = defaultdict(int)
    for r in records:
        groups[r["实验组"]] += 1
    for g, count in groups.items():
        print(f"  {g}: {count} 只")


def main():
    parser = ArgumentParser(description="OFT 汇总表生成器")
    parser.add_argument("results_dir", help="包含 arena_*.csv 的目录树根路径")
    parser.add_argument("-o", "--output", default="OFT_results_summary.csv",
                        help="输出 CSV 路径（默认 OFT_results_summary.csv）")
    args = parser.parse_args()

    if not os.path.isdir(args.results_dir):
        print(f"[错误] 目录不存在: {args.results_dir}")
        return

    generate_summary(args.results_dir, args.output)


if __name__ == "__main__":
    main()
