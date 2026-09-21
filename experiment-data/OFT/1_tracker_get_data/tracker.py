import csv
import os
import tkinter as tk
from datetime import datetime
from pynput import mouse, keyboard

MAX_CLICKS = 1000     # 测试用，正式使用改回 100
TRAIL_LENGTH = 50     # 轨迹窗口显示最近 N 次点击
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "record.csv")

click_records = []          # [[step, x, y], ...]
mouse_controller = mouse.Controller()
recording = False

# ---- tkinter 轨迹窗口 ----
root = tk.Tk()
root.title("点击轨迹（全部记录）")
root.attributes('-topmost', True)
root.attributes('-alpha', 0.75)

# 窗口大小
win_w, win_h = 420, 380
# 放在屏幕右上角（基于主屏尺寸计算，避免跑到屏幕外）
sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()
pos_x = sw - win_w - 30   # 右边留 30px
pos_y = 60                 # 顶部留 60px
# 兜底：如果屏幕比窗口还小（极端情况），贴左上角
if pos_x < 0:
    pos_x = 0
if pos_y < 0:
    pos_y = 0
root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
root.protocol("WM_DELETE_WINDOW", lambda: do_save_and_exit())  # 点 × 也保存退出

canvas = tk.Canvas(root, bg='#f5f5f5', highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)


def draw_trajectory():
    """在 tkinter 画布上绘制最近 TRAIL_LENGTH 次点击的轨迹"""
    canvas.delete("all")
    if not click_records:
        canvas.create_text(win_w / 2, win_h / 2, text="暂无记录\n按 F2 开启录制后点击",
                           font=("Microsoft YaHei", 11), fill="#999", justify=tk.CENTER)
        return

    recent = click_records[:]  # 显示全部记录

    # 计算边界，留 padding
    xs = [r[1] for r in recent]
    ys = [r[2] for r in recent]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    # 至少给 100px 范围避免除零
    if x_max - x_min < 100:
        cx = (x_min + x_max) / 2
        x_min, x_max = cx - 50, cx + 50
    if y_max - y_min < 100:
        cy = (y_min + y_max) / 2
        y_min, y_max = cy - 50, cy + 50

    # 画布内边距
    pad = 35
    cw = win_w
    ch = win_h

    def tx(x):
        return pad + (x - x_min) / (x_max - x_min) * (cw - 2 * pad)

    def ty(y):
        return pad + (y - y_min) / (y_max - y_min) * (ch - 2 * pad)

    # 连线
    points = []
    for r in recent:
        points.extend([tx(r[1]), ty(r[2])])
    if len(points) >= 4:
        canvas.create_line(*points, fill="#bbb", width=1.2, smooth=False)

    # 圆点 + 编号（点数多时只标注每 5 个）
    n = len(recent)
    label_step = 5 if n > 20 else 1
    for i, r in enumerate(recent):
        px, py = tx(r[1]), ty(r[2])
        step = r[0]
        r_size = 4 if n > 30 else 6
        canvas.create_oval(px - r_size, py - r_size, px + r_size, py + r_size,
                           fill="#D55E00", outline="#fff", width=1)
        # 只标注部分编号，避免重叠
        if step % label_step == 0 or step == 1 or step == MAX_CLICKS:
            canvas.create_text(px + 8, py - 5, text=str(step),
                               font=("Consolas", 7, "bold"), fill="#333", anchor=tk.W)

    # 坐标范围标注
    canvas.create_text(cw / 2, ch - 12,
                       text=f"X: [{x_min}, {x_max}]  Y: [{y_min}, {y_max}]",
                       font=("Consolas", 8), fill="#aaa")


# ---- pynput 回调 ----
def on_press(key):
    global recording
    try:
        if key == keyboard.Key.f2:
            if not recording:
                recording = True
                print(f"\n>>> 录制模式已开启，单击鼠标左键记录坐标（上限 {MAX_CLICKS} 次）")
            else:
                recording = False
                print(f"\n>>> 录制模式已暂停。已有 {len(click_records)} 条记录")
                print("    按 F2 恢复录制，按 Esc 保存退出")

        elif key == keyboard.Key.esc:
            print("\n手动停止，正在保存数据...")
            do_save_and_exit()

    except AttributeError:
        pass


def on_click(x, y, button, pressed):
    if not pressed:
        return
    if not recording:
        return
    if button != mouse.Button.left:
        return

    step = len(click_records) + 1
    click_records.append([step, x, y])
    remaining = MAX_CLICKS - step
    print(f"[{step}/{MAX_CLICKS}] X={x}, Y={y}  |  剩余 {remaining} 次")

    # 更新轨迹窗口（线程安全）
    root.after(0, draw_trajectory)

    if step >= MAX_CLICKS:
        print(f"\n{MAX_CLICKS} 个坐标全部记录完毕，正在保存...")
        do_save_and_exit()


def save_csv():
    """保存 CSV，若目标文件被占用则自动加时间戳后缀"""
    path = OUTPUT_PATH
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["step", "X", "Y"])
            writer.writerows(click_records)
        print(f"已保存 {len(click_records)} 个坐标到 {path}")
        return True
    except PermissionError:
        # 文件被占用（如 Excel 打开了），换个文件名
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base, ext = os.path.splitext(path)
        alt = f"{base}_{ts}{ext}"
        with open(alt, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["step", "X", "Y"])
            writer.writerows(click_records)
        print(f"[警告] record.csv 被占用，已另存为 {alt}")
        print(f"[提示] 请关闭 Excel 等程序后再试，或将 {os.path.basename(alt)} 重命名为 record.csv")
        return True
    except Exception as e:
        print(f"[错误] 保存失败: {e}")
        return False


def do_save_and_exit():
    save_csv()
    root.after(0, root.destroy)  # 无论保存成功与否都关闭窗口


# ---- 启动 ----
print("坐标记录器已启动")
print("按 [F2] 开启录制 → 单击鼠标左键记录坐标")
print("再按 [F2] 暂停录制，按 [Esc] 保存退出")
print(f"上限：{MAX_CLICKS} 次")
print("轨迹窗口显示全部点击记录")
print()

# 预绘制空白画布
draw_trajectory()

# 启动 pynput 监听器（后台线程）
k_listener = keyboard.Listener(on_press=on_press)
m_listener = mouse.Listener(on_click=on_click)
k_listener.start()
m_listener.start()

# tkinter 主循环（阻塞，直到 root.destroy()）
root.mainloop()

# 清理
k_listener.stop()
m_listener.stop()
