#!/usr/bin/env python3
"""
OFT (Open Field Test) 轨迹图生成脚本
从 Tracker 导出的数据生成论文级 Arena 轨迹图，并计算行为指标。

用法:
    python plot_oft.py 6.csv --px-per-cm 7.22 --dpi 300
    python plot_oft.py data.txt --dpi 300
    python plot_oft.py 6.csv 7.csv --px-per-cm 7.22
"""

import csv
import math
import os
import statistics
import sys
from argparse import ArgumentParser

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# ─────────────────────────────────────────────
# S1: 数据读取与解析
# ─────────────────────────────────────────────

def parse_oft_data(filepath: str, total_duration: float = None) -> dict:
    """
    解析 Tracker 导出的 CSV 数据。

    支持格式:
        格式 A (物理坐标):  t,x,y[,v[,L]]  (第2行为表头)
        格式 B (像素坐标):  step,X,Y           (无 t 列，需要 total_duration)

    Args:
        filepath: 数据文件路径
        total_duration: 总录制时长（秒），格式 B 必填，用于生成均匀 t 列

    Returns:
        dict with keys: ts, xs, ys, vs, filepath, filename, is_pixel
    """
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # 自动检测表头行：找第一个包含关键字（step/t/x/y）的行
    header_row_idx = 0
    for idx, row in enumerate(rows[:6]):
        row_lower = [c.strip().lower() for c in row]
        if "step" in row_lower or "t" in row_lower or "x" in row_lower:
            header_row_idx = idx
            break

    header = [h.strip() for h in rows[header_row_idx]]
    data_rows = rows[header_row_idx + 1:]

    ts, xs, ys, vs = [], [], [], []

    # 判断格式
    has_t = "t" in header or "T" in header
    has_step = "step" in header or "Step" in header
    has_x = "x" in header or "X" in header
    has_y = "y" in header or "Y" in header

    is_pixel = (has_step and has_x and has_y and not has_t)

    if is_pixel:
        # 格式 B: step, X, Y —— 需要 total_duration 生成 t 列
        if total_duration is None:
            raise ValueError("像素坐标模式需要提供 --total-duration 参数（总录制时长，秒）")

        step_idx = header.index("step") if "step" in header else header.index("Step")
        x_idx = header.index("X") if "X" in header else header.index("x")
        y_idx = header.index("Y") if "Y" in header else header.index("y")

        valid_xs, valid_ys, valid_steps = [], [], []
        for row in data_rows:
            if len(row) <= max(step_idx, x_idx, y_idx):
                continue
            try:
                step = int(row[step_idx])
                x = float(row[x_idx])
                y = float(row[y_idx])
            except (ValueError, IndexError):
                continue
            valid_xs.append(x)
            valid_ys.append(y)
            valid_steps.append(step)

        n = len(valid_xs)
        if n < 2:
            raise ValueError(f"文件 {filepath} 中有效数据点不足（需要 ≥ 2）")

        dt = total_duration / (n - 1)
        ts = [i * dt for i in range(n)]
        xs = valid_xs
        ys = valid_ys
        vs = [None] * n
    else:
        # 格式 A: t, x, y[, v[, L]]
        t_idx = header.index("t") if "t" in header else 0
        x_idx = header.index("x") if "x" in header else 1
        y_idx = header.index("y") if "y" in header else 2
        v_idx = header.index("v") if "v" in header else None

        for row in data_rows:
            if len(row) <= max(t_idx, x_idx, y_idx):
                continue
            try:
                t = float(row[t_idx])
                x = float(row[x_idx])
                y = float(row[y_idx])
            except (ValueError, IndexError):
                continue
            ts.append(t)
            xs.append(x)
            ys.append(y)

            if v_idx is not None and len(row) > v_idx and row[v_idx].strip():
                try:
                    vs.append(float(row[v_idx]))
                except ValueError:
                    vs.append(None)
            else:
                vs.append(None)

    if not ts:
        raise ValueError(f"文件 {filepath} 中没有有效数据行")

    return {
        "ts": ts,
        "xs": xs,
        "ys": ys,
        "vs": vs,
        "is_pixel": is_pixel,
        "filepath": filepath,
        "filename": os.path.basename(filepath),
    }


def convert_pixel_to_cm(data: dict, px_per_cm: float,
                       arena_x0_px: float, arena_x1_px: float,
                       arena_y0_px: float, arena_y1_px: float) -> dict:
    """
    将 Tracker 像素坐标转换为 Arena 物理坐标（cm）。

    映射逻辑（基于 Arena 真实四角像素坐标）:
        x_cm = (x_px - arena_x0_px) / px_per_cm
        y_cm = (arena_y1_px - y_px) / px_per_cm  (翻转 Y 轴: 像素Y↓ → 物理Y↑)

    Args:
        data: parse_oft_data() 返回的字典（像素坐标）
        px_per_cm: 像素/厘米换算比例
        arena_x0_px: Arena 左边界像素 X
        arena_x1_px: Arena 右边界像素 X
        arena_y0_px: Arena 上边界像素 Y（像素坐标系中较小的 Y 值 = 顶部）
        arena_y1_px: Arena 下边界像素 Y（像素坐标系中较大的 Y 值 = 底部）

    Returns:
        新的 data 字典（x,y 已转为 cm）
    """
    xs_px = data["xs"]
    ys_px = data["ys"]

    xs_cm = [(x - arena_x0_px) / px_per_cm for x in xs_px]
    ys_cm = [(arena_y1_px - y) / px_per_cm for y in ys_px]

    return {
        "ts": data["ts"],
        "xs": xs_cm,
        "ys": ys_cm,
        "vs": data["vs"],
        "is_pixel": False,
        "filepath": data["filepath"],
        "filename": data["filename"],
    }


# ─────────────────────────────────────────────
# S2: Arena 边界计算（正方形约束 + padding）
# ─────────────────────────────────────────────

def compute_arena_bounds(xs: list, ys: list, padding: float = 0.02, arena_size_cm: float = None) -> dict:
    """
    计算 Arena 的显示边界。

    当 arena_size_cm 提供时（已知 Arena 真实尺寸），返回固定坐标系；
    否则从轨迹数据推算（物理坐标模式的后备方案）。

    Args:
        xs, ys: 物理坐标列表（cm）
        padding: 外扩比例（0.02 = 2%）
        arena_size_cm: Arena 真实边长（cm），如提供则返回固定边界

    Returns:
        dict with x_min, x_max, y_min, y_max, side, center_x, center_y
    """
    if arena_size_cm is not None:
        margin = arena_size_cm * padding
        display_side = arena_size_cm + 2 * margin
        return {
            "x_min": -margin,
            "x_max": arena_size_cm + margin,
            "y_min": -margin,
            "y_max": arena_size_cm + margin,
            "side": display_side,           # 红色边框用的显示边长
            "arena_size": arena_size_cm,    # Arena 真实边长（用于中心区计算）
            "center_x": arena_size_cm / 2.0,
            "center_y": arena_size_cm / 2.0,
        }

    # 后备：从轨迹数据推算
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    x_span = x_max - x_min
    y_span = y_max - y_min

    max_span = max(x_span, y_span)
    side = max_span * (1.0 + padding) if max_span > 0 else 1.0

    cx = (x_min + x_max) / 2.0
    cy = (y_min + y_max) / 2.0

    half = side / 2.0

    return {
        "x_min": cx - half,
        "x_max": cx + half,
        "y_min": cy - half,
        "y_max": cy + half,
        "side": side,
        "arena_size": side / (1.0 + padding),  # 反推 Arena 真实边长
        "center_x": cx,
        "center_y": cy,
    }


# ─────────────────────────────────────────────
# S3: 行为指标计算
# ─────────────────────────────────────────────

def compute_total_distance(data: dict, px_per_cm: float = None) -> float:
    """
    计算 Total distance (cm)。

    逐帧累加相邻点的欧氏距离，转成 cm。

    Args:
        data: parse_oft_data() 返回的字典
        px_per_cm: 如果是像素坐标需要提供，用于换算

    Returns:
        总距离（cm）
    """
    xs = data["xs"]
    ys = data["ys"]
    is_pixel = data["is_pixel"]

    total_px = 0.0
    for i in range(len(xs) - 1):
        dx = xs[i + 1] - xs[i]
        dy = ys[i + 1] - ys[i]
        total_px += math.sqrt(dx * dx + dy * dy)

    if is_pixel:
        if px_per_cm is None:
            raise ValueError("像素坐标需要提供 px_per_cm 参数")
        return total_px / px_per_cm
    else:
        return total_px  # 已经是 cm


def compute_entries_in_center(data: dict, bounds: dict, center_ratio: float = 0.40) -> int:
    """
    计算 Entries in center（进入中心区的次数）。

    判定: 第 i 帧在框外，第 i+1 帧在框内 → 算 1 次。
    第一帧在框内不算（不知道之前是否在框内）。

    Args:
        data: parse_oft_data() 返回的字典
        bounds: compute_arena_bounds() 返回的字典
        center_ratio: 中心区占 Arena 边长的比例

    Returns:
        进入次数（整数）
    """
    xs = data["xs"]
    ys = data["ys"]

    arena_sz = bounds.get("arena_size", bounds["side"])
    cz_half = arena_sz * center_ratio / 2.0
    cz_xmin = bounds["center_x"] - cz_half
    cz_xmax = bounds["center_x"] + cz_half
    cz_ymin = bounds["center_y"] - cz_half
    cz_ymax = bounds["center_y"] + cz_half

    entries = 0
    n = len(xs)

    for i in range(n - 1):
        x_curr, y_curr = xs[i], ys[i]
        x_next, y_next = xs[i + 1], ys[i + 1]

        curr_in = cz_xmin <= x_curr <= cz_xmax and cz_ymin <= y_curr <= cz_ymax
        next_in = cz_xmin <= x_next <= cz_xmax and cz_ymin <= y_next <= cz_ymax

        if not curr_in and next_in:
            entries += 1

    return entries


def compute_rest_time(data: dict, bounds: dict, center_ratio: float = 0.40,
                     rest_threshold_cm_s: float = 2.0) -> dict:
    """
    计算 Rest times（静止时间）。

    判定: 瞬时速度 < threshold 的帧累计时间。
    瞬时速度用相邻帧距离 / Δt 计算（与 v 列无关）。

    Args:
        data: parse_oft_data() 返回的字典
        bounds: compute_arena_bounds() 返回的字典（未使用，保留接口）
        center_ratio: 未使用，保留接口
        rest_threshold_cm_s: 静止速度阈值（cm/s），默认 2.0 cm/s

    Returns:
        dict with rest_time_s, rest_frames, total_frames
    """
    xs = data["xs"]
    ys = data["ys"]
    ts = data["ts"]
    n = len(xs)

    rest_frames = 0
    rest_time = 0.0

    for i in range(n - 1):
        dx = xs[i + 1] - xs[i]
        dy = ys[i + 1] - ys[i]
        dist = math.sqrt(dx * dx + dy * dy)
        dt = ts[i + 1] - ts[i]

        if dt <= 0:
            continue

        v = dist / dt  # cm/s
        if v < rest_threshold_cm_s:
            rest_frames += 1
            rest_time += dt

    return {
        "rest_time_s": rest_time,
        "rest_frames": rest_frames,
        "total_frames": n,
    }


def compute_time_in_center(data: dict, bounds: dict, center_ratio: float = 0.40) -> dict:
    """
    计算 Time in center (%) —— 帧计数法。

    判定: 第 i 帧的 (x_i, y_i) 落入绿色中心区 → 该帧完整 Δt_i 算入中心时间。
    分母: 总录制时长 t_last − t_first。

    Args:
        data: parse_oft_data() 返回的字典
        bounds: compute_arena_bounds() 返回的字典
        center_ratio: 中心区占 Arena 边长的比例

    Returns:
        dict with center_time_s, total_time_s, pct (0-100)
    """
    ts = data["ts"]
    xs = data["xs"]
    ys = data["ys"]

    cz_half = bounds.get("arena_size", bounds["side"]) * center_ratio / 2.0
    cz_xmin = bounds["center_x"] - cz_half
    cz_xmax = bounds["center_x"] + cz_half
    cz_ymin = bounds["center_y"] - cz_half
    cz_ymax = bounds["center_y"] + cz_half

    center_time = 0.0
    n = len(ts)

    for i in range(n - 1):
        x, y = xs[i], ys[i]
        if cz_xmin <= x <= cz_xmax and cz_ymin <= y <= cz_ymax:
            center_time += ts[i + 1] - ts[i]

    total_time = ts[-1] - ts[0]
    pct = (center_time / total_time) * 100.0 if total_time > 0 else 0.0

    return {
        "center_time_s": center_time,
        "total_time_s": total_time,
        "pct": pct,
    }


# ─────────────────────────────────────────────
# S3b: 数据质量验证（文献基准）
# ─────────────────────────────────────────────
#
# 阈值来源:
#   - MouseMove (srep16171, 2015): Sham vs MCAo 速度分布
#   - MouseActivity (PMC6990588, 2020): C57BL/6J WT 10min 总距 26-31 m
#   - 小鼠运动生理学共识: 行走 5-15, 小跑 15-30, 奔跑 30-50, 冲刺 50-80 cm/s
#
# 所有检查为 WARNING 级别 —— 不拦截运行，仅提示用户核查。

def validate_oft_metrics(data: dict, total_duration: float) -> dict:
    """
    基于文献参考值验证 OFT 指标合理性。

    Args:
        data: 坐标已转为 cm 的 data dict（ts, xs, ys）
        total_duration: 总录制时长（秒）

    Returns:
        dict with warnings (list of str) and stats (dict with derived metrics)
    """
    xs = data["xs"]
    ys = data["ys"]
    ts = data["ts"]
    n = len(xs)

    # ── 逐帧计算瞬时速度 ──
    speeds = []
    for i in range(n - 1):
        dx = xs[i + 1] - xs[i]
        dy = ys[i + 1] - ys[i]
        dt = ts[i + 1] - ts[i]
        if dt <= 0:
            continue
        dist = math.sqrt(dx * dx + dy * dy)
        speeds.append(dist / dt)

    if len(speeds) < 2:
        return {"warnings": ["数据点不足，无法计算速度分布。"], "stats": {}}

    # ── 逐帧加速度 ──
    accels = []
    for i in range(len(speeds) - 1):
        dt = ts[i + 1] - ts[i]
        if dt <= 0:
            continue
        accels.append(abs(speeds[i + 1] - speeds[i]) / dt)

    mean_speed = statistics.mean(speeds)
    median_speed = statistics.median(speeds)
    max_speed = max(speeds)

    sorted_speeds = sorted(speeds)
    ns = len(sorted_speeds)
    p5  = sorted_speeds[int(ns * 0.05)]
    p25 = sorted_speeds[int(ns * 0.25)]
    p75 = sorted_speeds[int(ns * 0.75)]
    p95 = sorted_speeds[int(ns * 0.95)]
    p99 = sorted_speeds[int(ns * 0.99)]

    burst_30_pct = sum(1 for s in speeds if s > 30) / ns * 100.0
    burst_50_pct = sum(1 for s in speeds if s > 50) / ns * 100.0
    rest_1_pct   = sum(1 for s in speeds if s < 1)  / ns * 100.0
    max_accel = max(accels) if accels else 0
    mean_accel = statistics.mean(accels) if accels else 0
    p95_accel = sorted(accels)[int(len(accels) * 0.95)] if len(accels) > 0 else 0

    p99_p95_ratio = p99 / p95 if p95 > 0 else float("inf")

    total_dist = sum(math.sqrt((xs[i+1]-xs[i])**2 + (ys[i+1]-ys[i])**2) for i in range(n-1))

    # ── 阈值检查 ──
    warnings = []

    if mean_speed > 20:
        warnings.append(
            f"Mean speed {mean_speed:.1f} cm/s > 20 cm/s -- "
            f"C57BL/6 OFT 通常 3-8 cm/s (文献: MouseActivity 2020)。核实 total_duration 是否偏小。"
        )

    if max_speed > 80:
        warnings.append(
            f"Max instantaneous speed {max_speed:.1f} cm/s > 80 cm/s -- "
            f"小鼠冲刺生理上限 ~80 cm/s。可能是追踪噪声或时间标尺错误。"
        )

    if max_accel > 500:
        warnings.append(
            f"Max acceleration {max_accel:.0f} cm/s^2 > 500 cm/s^2 -- "
            f"正常启动 <200 cm/s^2，>500 通常为追踪伪影。"
        )

    if burst_30_pct > 10:
        warnings.append(
            f"Burst ratio (>30 cm/s) {burst_30_pct:.1f}% > 10% -- "
            f"持续高速奔跑不符合 OFT 正常探索模式。"
        )

    if rest_1_pct > 50:
        warnings.append(
            f"Rest ratio (<1 cm/s) {rest_1_pct:.1f}% > 50% -- "
            f"动物可能处于镇静/疾病状态。核实动物状态。"
        )

    if rest_1_pct < 2:
        warnings.append(
            f"Rest ratio (<1 cm/s) {rest_1_pct:.1f}% < 2% -- "
            f"几乎无静止，可能数据全是噪声。核实追踪质量。"
        )

    if p95 > 0 and p99_p95_ratio > 3.0:
        warnings.append(
            f"P99/P95 speed ratio {p99_p95_ratio:.1f} > 3.0 -- "
            f"速度极值分布过宽，可能有异常跳跃点。"
        )

    stats = {
        "mean_speed": mean_speed,
        "median_speed": median_speed,
        "max_speed": max_speed,
        "p5_speed": p5,
        "p25_speed": p25,
        "p75_speed": p75,
        "p95_speed": p95,
        "p99_speed": p99,
        "burst_30_pct": burst_30_pct,
        "burst_50_pct": burst_50_pct,
        "rest_1_pct": rest_1_pct,
        "mean_accel": mean_accel,
        "max_accel": max_accel,
        "p95_accel": p95_accel,
        "p99_p95_ratio": p99_p95_ratio,
        "n_speeds": ns,
    }

    return {"warnings": warnings, "stats": stats}


# ─────────────────────────────────────────────
# S3c: 验证阈值定义 + CSV 输出
# ─────────────────────────────────────────────

THRESHOLDS = [
    {
        "check": "Mean speed",
        "unit": "cm/s",
        "threshold": "≤ 20",
        "reference": "MouseActivity (PMC6990588, 2020): C57BL/6J WT 10min mean ~4-5 cm/s",
        "measure": lambda v: v.get("mean_speed", 0),
        "warn_if": lambda val: val > 20,
    },
    {
        "check": "Max instantaneous speed",
        "unit": "cm/s",
        "threshold": "≤ 80",
        "reference": "Mouse physiology consensus: sprint ceiling ~80 cm/s",
        "measure": lambda v: v.get("max_speed", 0),
        "warn_if": lambda val: val > 80,
    },
    {
        "check": "Max acceleration",
        "unit": "cm/s²",
        "threshold": "≤ 500",
        "reference": "Tracking artifacts typical: normal start <200, >500 likely noise",
        "measure": lambda v: v.get("max_accel", 0),
        "warn_if": lambda val: val > 500,
    },
    {
        "check": "Burst ratio (>30 cm/s)",
        "unit": "%",
        "threshold": "≤ 10",
        "reference": "OFT normal exploration pattern: sustained high-speed running atypical",
        "measure": lambda v: v.get("burst_30_pct", 0),
        "warn_if": lambda val: val > 10,
    },
    {
        "check": "Rest ratio (<1 cm/s)",
        "unit": "%",
        "threshold": "≥ 2 且 ≤ 50",
        "reference": "Animal state check: >50% sedation/disease, <2% tracking noise",
        "measure": lambda v: v.get("rest_1_pct", 0),
        "warn_if": lambda val: val > 50 or val < 2,
    },
    {
        "check": "P99/P95 speed ratio",
        "unit": "—",
        "threshold": "≤ 3.0",
        "reference": "Jump artifact detection: wide tail suggests spurious jumps",
        "measure": lambda v: v.get("p99_p95_ratio", 0),
        "warn_if": lambda val: val > 3.0,
    },
]


def write_oft_csv(
    csv_path: str,
    metrics: dict,
    validation_stats: dict,
    validation_warnings: list,
    total_duration: float,
    arena_bounds_str: str,
    arena_size_cm: float,
    px_per_cm: float,
    padding: float,
    center_ratio: float,
    rest_threshold_cm_s: float,
    input_file: str,
):
    """
    将 4 个主要指标 + 验证检查 + 速度分布写入结构化 CSV 文件。

    编码 UTF-8，Excel 可直接打开。
    """
    rows = []

    # ── Section 1: Primary Metrics ──
    rows.append(["[Primary Metrics]", "", ""])
    rows.append(["Metric", "Value", "Unit"])
    rows.append(["Total distance", f"{metrics['total_distance_cm']:.1f}", "cm"])
    rows.append(["Entries in center", f"{metrics['entries_in_center']}", "times"])
    rows.append(["Rest time", f"{metrics['rest_time_s']:.1f}", "s"])
    rows.append(["Time in center", f"{metrics['time_in_center_pct']:.2f}", "%"])
    rows.append([])

    # ── Section 2: Validation Checks ──
    rows.append(["[Validation Checks]", "", "", "", "", ""])
    rows.append(["Check Item", "Measured Value", "Threshold", "Unit", "Reference", "Status"])
    stats = validation_stats
    for t in THRESHOLDS:
        val = t["measure"](stats)
        unit = t["unit"]
        if unit == "%":
            measured_str = f"{val:.1f}"
        elif unit == "—":
            measured_str = f"{val:.2f}"
        else:
            measured_str = f"{val:.2f}"
        warns = t["warn_if"](val)
        status = "WARN" if warns else "PASS"
        rows.append([t["check"], measured_str, t["threshold"], t["unit"], t["reference"], status])
    rows.append([])

    # ── Section 3: Speed Distribution ──
    rows.append(["[Speed Distribution]", "", ""])
    rows.append(["Statistic", "Value", "Unit"])
    rows.append(["Mean speed", f"{stats.get('mean_speed', 0):.2f}", "cm/s"])
    rows.append(["Median speed", f"{stats.get('median_speed', 0):.2f}", "cm/s"])
    rows.append(["Max speed", f"{stats.get('max_speed', 0):.2f}", "cm/s"])
    rows.append(["P5 speed", f"{stats.get('p5_speed', 0):.2f}", "cm/s"])
    rows.append(["P25 speed", f"{stats.get('p25_speed', 0):.2f}", "cm/s"])
    rows.append(["P75 speed", f"{stats.get('p75_speed', 0):.2f}", "cm/s"])
    rows.append(["P95 speed", f"{stats.get('p95_speed', 0):.2f}", "cm/s"])
    rows.append(["P99 speed", f"{stats.get('p99_speed', 0):.2f}", "cm/s"])
    rows.append(["Burst >30 cm/s", f"{stats.get('burst_30_pct', 0):.1f}", "%"])
    rows.append(["Burst >50 cm/s", f"{stats.get('burst_50_pct', 0):.1f}", "%"])
    rows.append(["Rest <1 cm/s", f"{stats.get('rest_1_pct', 0):.1f}", "%"])
    rows.append(["Mean acceleration", f"{stats.get('mean_accel', 0):.1f}", "cm/s²"])
    rows.append(["Max acceleration", f"{stats.get('max_accel', 0):.1f}", "cm/s²"])
    rows.append(["P95 acceleration", f"{stats.get('p95_accel', 0):.1f}", "cm/s²"])
    rows.append(["P99/P95 speed ratio", f"{stats.get('p99_p95_ratio', 0):.2f}", "—"])
    rows.append(["Sample count (speeds)", f"{stats.get('n_speeds', 0)}", "frames"])
    rows.append([])

    # ── Section 4: Run Parameters ──
    rows.append(["[Run Parameters]", "", ""])
    rows.append(["Parameter", "Value", ""])
    rows.append(["Total duration", f"{total_duration:.2f} s", ""])
    rows.append(["Arena bounds (px)", arena_bounds_str, ""])
    rows.append(["Arena size", f"{arena_size_cm} cm", ""])
    rows.append(["px_per_cm", f"{px_per_cm:.2f}", ""])
    rows.append(["Padding", f"{padding}", ""])
    rows.append(["Center ratio", f"{center_ratio}", ""])
    rows.append(["Rest threshold", f"{rest_threshold_cm_s} cm/s", ""])
    rows.append(["Input file", input_file, ""])

    if validation_warnings:
        rows.append([])
        rows.append(["[WARNINGS]", "", ""])
        for w in validation_warnings:
            rows.append(["WARNING", w, ""])

    # ── 写入文件 ──
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)


# ─────────────────────────────────────────────
# S4: 绘图主函数
# ─────────────────────────────────────────────

def plot_oft_arena(
    data: dict,
    output_path: str,
    dpi: int = 300,
    padding: float = 0.02,
    center_ratio: float = 0.40,
    arena_title: str = None,
    fig_size_inches: float = 6.0,
    rest_threshold_cm_s: float = 2.0,
    total_duration: float = None,
    px_per_cm: float = None,
    arena_x0_px: float = None,
    arena_x1_px: float = None,
    arena_y0_px: float = None,
    arena_y1_px: float = None,
    arena_size_cm: float = None,
) -> tuple:
    """
    绘制单个 Arena 的 OFT 轨迹图，并在图下方标注 4 个行为指标。

    Args:
        data: parse_oft_data() 返回的字典
        output_path: 输出 PNG 路径
        dpi: 图片分辨率
        padding: Arena 边界外扩比例（默认 2%）
        center_ratio: 中心区占 Arena 边长的比例（默认 40%）
        arena_title: 标题（默认不显示）
        fig_size_inches: 图片物理尺寸（英寸），正方形
        rest_threshold_cm_s: 静止速度阈值（cm/s）
        total_duration: 总录制时长（秒），用于计算 Δt
        px_per_cm: 像素/厘米换算比例
        arena_x0_px, arena_x1_px: Arena 左右边界像素 X
        arena_y0_px, arena_y1_px: Arena 上下边界像素 Y
        arena_size_cm: Arena 真实边长（cm），用于中心区计算

    Returns:
        (output_path, metrics_dict)
    """
    # ── 坐标转换（如果是像素坐标） ──
    if data["is_pixel"]:
        if px_per_cm is None:
            raise ValueError("像素坐标需要提供 px_per_cm 参数")
        if None in (arena_x0_px, arena_x1_px, arena_y0_px, arena_y1_px):
            raise ValueError("像素坐标需要提供 Arena 四角像素边界参数")
        data = convert_pixel_to_cm(data, px_per_cm,
                                   arena_x0_px, arena_x1_px,
                                   arena_y0_px, arena_y1_px)

    xs = data["xs"]
    ys = data["ys"]

    # ── Arena 边界 ──
    bounds = compute_arena_bounds(xs, ys, padding=padding, arena_size_cm=arena_size_cm)

    # ── 中心区计算（基于 Arena 真实边长） ──
    arena_sz = bounds.get("arena_size", bounds["side"])

    # ── 计算 4 个指标 ──
    total_dist = compute_total_distance(data, px_per_cm=px_per_cm)
    entries = compute_entries_in_center(data, bounds, center_ratio=center_ratio)
    rest = compute_rest_time(data, bounds, center_ratio=center_ratio,
                            rest_threshold_cm_s=rest_threshold_cm_s)
    tic = compute_time_in_center(data, bounds, center_ratio=center_ratio)

    # ── 数据质量验证 ──
    validation = validate_oft_metrics(data, total_duration=total_duration)

    # ── 中心区几何 ──
    cz_half = arena_sz * center_ratio / 2.0
    cx_cz = bounds["center_x"] - cz_half
    cy_cz = bounds["center_y"] - cz_half
    cz_size = cz_half * 2.0

    # ── 绘图 ──
    fig, ax = plt.subplots(figsize=(fig_size_inches, fig_size_inches + 0.5), dpi=dpi)

    ax.set_xlim(bounds["x_min"], bounds["x_max"])
    ax.set_ylim(bounds["y_min"], bounds["y_max"])
    ax.set_aspect("equal")
    ax.axis("off")

    # ── 中心区（仅绿色外框，无填充） ──
    cz_rect = patches.Rectangle(
        (cx_cz, cy_cz),
        cz_size,
        cz_size,
        linewidth=2.0,
        edgecolor="#5FFF5F",
        facecolor="none",
        zorder=1,
    )
    ax.add_patch(cz_rect)

    # ── 轨迹（黑色） ──
    ax.plot(xs, ys, color="black", linewidth=1.0, zorder=2, antialiased=False)

    # ── 红色边框（Arena 边界） ──
    border = patches.Rectangle(
        (bounds["x_min"], bounds["y_min"]),
        bounds["side"],
        bounds["side"],
        linewidth=3.0,
        edgecolor="#FF2F2F",
        facecolor="none",
        zorder=3,
    )
    ax.add_patch(border)

    # ── 标题（仅当显式指定时绘制） ──
    if arena_title:
        title_x = bounds["x_min"] + bounds["side"] * 0.03
        title_y = bounds["y_max"] - bounds["side"] * 0.06
        ax.text(
            title_x,
            title_y,
            arena_title,
            fontsize=14,
            fontweight="bold",
            color="black",
            ha="left",
            va="top",
            zorder=4,
        )

    # ── 4 个指标标注（画布正下方） ──
    metrics_text = (
        f"Total distance: {total_dist:.1f} cm    "
        f"Entries in center: {entries}    "
        f"Rest time: {rest['rest_time_s']:.1f} s (v < {rest_threshold_cm_s} cm/s)    "
        f"Time in center: {tic['pct']:.2f}%"
    )
    fig.text(
        0.5, 0.01,
        metrics_text,
        ha="center", va="bottom", fontsize=8, color="black",
    )

    # ── 保存 ──
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", pad_inches=0.1,
                facecolor="white", edgecolor="none")
    plt.close(fig)

    metrics = {
        "total_distance_cm": total_dist,
        "entries_in_center": entries,
        "rest_time_s": rest["rest_time_s"],
        "rest_frames": rest["rest_frames"],
        "time_in_center_pct": tic["pct"],
        "time_in_center_s": tic["center_time_s"],
        "total_time_s": tic["total_time_s"],
        "validation_warnings": validation["warnings"],
        "validation_stats": validation["stats"],
    }

    return output_path, metrics


def _extract_arena_title(filename: str) -> str:
    """从文件名提取 Arena 标题，如 '6.csv' → 'Arena 6'"""
    name_no_ext = os.path.splitext(filename)[0]
    return f"Arena {name_no_ext}"


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = ArgumentParser(description="OFT Arena 轨迹图生成器（支持像素/物理坐标，支持 Arena 固定边界校准）")
    parser.add_argument("input", nargs="+", help="输入数据文件 (.csv/.txt)")
    parser.add_argument("-o", "--output", default=None,
                        help="输出图片路径（默认 arena_{输入名}.png）")
    parser.add_argument("--dpi", type=int, default=300,
                        help="图片 DPI（默认 300）")
    parser.add_argument("--padding", type=float, default=0.02,
                        help="Arena 边界外扩比例（默认 0.02 = 2%%）")
    parser.add_argument("--center-ratio", type=float, default=0.40,
                        help="中心区占 Arena 边长的比例（默认 0.40 = 40%%）")
    parser.add_argument("--title", default=None,
                        help="自定义标题（默认无标题）")
    parser.add_argument("--figsize", type=float, default=6.0,
                        help="图片物理尺寸 inches（默认 6.0）")
    parser.add_argument("--px-per-cm", type=float, default=None,
                        help="像素/厘米换算比例（默认基于 Arena 边界自动推算，约 7.22）")
    parser.add_argument("--total-duration", type=float, default=120.0,
                        help="总录制时长（秒），默认 120 s（2 min）。可通过 --total-duration 覆盖。")
    parser.add_argument("--rest-threshold", type=float, default=2.0,
                        help="静止速度阈值 cm/s（默认 2.0）")
    parser.add_argument("--arena-bounds", type=str, default="908,384,1270,745",
                        help="Arena 四角像素坐标: x0,y0,x1,y1（默认 908,384,1270,745）")
    parser.add_argument("--arena-size", type=float, default=50,
                        help="Arena 真实边长 cm（默认 50）")

    args = parser.parse_args()

    # ── 解析 Arena 边界 ──
    arena_x0 = arena_x1 = arena_y0 = arena_y1 = None
    if args.arena_bounds:
        parts = args.arena_bounds.replace(",", " ").split()
        if len(parts) == 4:
            arena_x0, arena_y0, arena_x1, arena_y1 = map(float, parts)

    # ── 自动推算 px_per_cm ──
    if args.px_per_cm is None and arena_x0 is not None:
        args.px_per_cm = (arena_x1 - arena_x0) / args.arena_size

    if args.px_per_cm is not None:
        print(f"[像素坐标模式] Arena 边界: ({arena_x0}, {arena_y0}) → ({arena_x1}, {arena_y1})")
        print(f"               px_per_cm = {args.px_per_cm:.2f} | Arena = {args.arena_size} cm × {args.arena_size} cm")
        print(f"               [!!] 总录制时长: {args.total_duration:.2f} s  <- 请核实此值!")
        print()

    for i, infile in enumerate(args.input):
        print(f"[{i+1}/{len(args.input)}] 处理: {infile}")

        # 解析数据
        data = parse_oft_data(infile, total_duration=args.total_duration)
        print(f"  数据点: {len(data['xs'])}")
        print(f"  格式: {'像素坐标' if data['is_pixel'] else '物理坐标（cm）'}")
        if data["is_pixel"]:
            n_pts = len(data['xs'])
            if n_pts > 1:
                print(f"  Δt: {args.total_duration / (n_pts - 1):.4f} s/帧")

        if data["is_pixel"] and args.px_per_cm is None:
            print("  [!!] 警告: 像素坐标需要提供 --px-per-cm 或 --arena-bounds 参数")
            continue

        # 输出路径
        if args.output and len(args.input) == 1:
            out = args.output
        else:
            base = os.path.splitext(os.path.basename(infile))[0]
            out = f"arena_{base}.png"

        # 标题
        title = args.title if args.title else None

        # 绘图 + 计算指标
        out_path, metrics = plot_oft_arena(
            data=data,
            output_path=out,
            dpi=args.dpi,
            padding=args.padding,
            center_ratio=args.center_ratio,
            arena_title=title,
            fig_size_inches=args.figsize,
            rest_threshold_cm_s=args.rest_threshold,
            total_duration=args.total_duration,
            px_per_cm=args.px_per_cm,
            arena_x0_px=arena_x0,
            arena_x1_px=arena_x1,
            arena_y0_px=arena_y0,
            arena_y1_px=arena_y1,
            arena_size_cm=args.arena_size,
        )

        print(f"  → {out_path}")
        print(f"  Total distance:    {metrics['total_distance_cm']:.1f} cm")
        print(f"  Entries in center: {metrics['entries_in_center']}")
        print(f"  Rest time:         {metrics['rest_time_s']:.1f} s")
        print(f"  Time in center:    {metrics['time_in_center_pct']:.2f}%")

        # ── 验证报告 ──
        stats = metrics.get("validation_stats", {})
        warnings = metrics.get("validation_warnings", [])
        if stats:
            print()
            print(f"  ── 速度分布验证 ──")
            print(f"  瞬时速度 (cm/s):  Mean={stats['mean_speed']:.2f}  Median={stats['median_speed']:.2f}  Max={stats['max_speed']:.2f}")
            print(f"    P5={stats['p5_speed']:.2f}  P25={stats['p25_speed']:.2f}  P75={stats['p75_speed']:.2f}  P95={stats['p95_speed']:.2f}  P99={stats['p99_speed']:.2f}")
            print(f"    Burst>30 cm/s: {stats['burst_30_pct']:.1f}%  Burst>50 cm/s: {stats['burst_50_pct']:.1f}%  Rest<1 cm/s: {stats['rest_1_pct']:.1f}%")
            print(f"    P99/P95 ratio: {stats['p99_p95_ratio']:.2f}")
            print(f"  加速度 (cm/s^2):  Mean={stats['mean_accel']:.1f}  Max={stats['max_accel']:.1f}  P95={stats['p95_accel']:.1f}")
        if warnings:
            print(f"  ── WARNINGS ({len(warnings)}) ──")
            for w in warnings:
                print(f"  [!!] {w}")

        # ── 输出 CSV ──
        csv_path = out_path.replace(".png", ".csv")
        write_oft_csv(
            csv_path=csv_path,
            metrics=metrics,
            validation_stats=stats if stats else {},
            validation_warnings=warnings,
            total_duration=args.total_duration,
            arena_bounds_str=args.arena_bounds,
            arena_size_cm=args.arena_size,
            px_per_cm=args.px_per_cm,
            padding=args.padding,
            center_ratio=args.center_ratio,
            rest_threshold_cm_s=args.rest_threshold,
            input_file=infile,
        )
        print(f"  → {csv_path}")
        print()


if __name__ == "__main__":
    main()
