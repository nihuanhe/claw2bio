# 1_多通道批量对比度调整

**多色免疫荧光（mIF）批量对比度调整——将 16-bit 灰度 TIFF 转为伪彩 RGB，所有视野统一亮度参数。**

---

## 依赖

| 软件 | 路径/版本 | 用途 |
|------|----------|------|
| **ImageJ** (NIH ImageJ 1.x) | `C:\Users\A\Desktop\ImageJ\ImageJ.exe` | 运行宏、手动校准、批量处理 |
| 输入文件 | 16-bit 单通道灰度 TIFF | 扫描仪原始数据 |
| 无需额外插件 | — | 使用 ImageJ 内置 LUT / Merge Channels / Save 命令 |

---

## 目录结构

```
1_多通道批量对比度调整/
├── README.md                         ← 本文件（操作手册）
├── scripts/
│   └── batch_adjust_mif.ijm          ← ImageJ 宏（核心脚本）
└── examples/                         ← 小 fixture（×4 降采样，共 ~4 MB）
    ├── input/                        ← 示例输入（16-bit 灰度 tif）
    │   ├── sample1/
    │   │   ├── DAPI/FOV 00872_TG440.tif
    │   │   ├── CD8-AF488/FOV 00872_TG520.tif
    │   │   ├── PDL1-AF594/FOV 00872_TG570.tif
    │   │   └── PD1-AF647/FOV 00872_TG650.tif
    │   └── sample2/
    │       └── ...（同样 4 通道结构）
    └── output/                       ← 参考输出（Python 模拟的伪彩 PNG，仅供目检）
        ├── README.txt                ← 说明：真机宏输出为 *-adjusted.tif
        ├── sample1/
        │   ├── DAPI/FOV 00872_TG440-adjusted.png
        │   ├── CD8-AF488/FOV 00872_TG520-adjusted.png
        │   ├── PDL1-AF594/FOV 00872_TG570-adjusted.png
        │   ├── PD1-AF647/FOV 00872_TG650-adjusted.png
        │   └── FOV sample1-Merge-adjusted.png        ← 四通道合成图
        └── sample2/
            └── ...（同上，5 个文件）
```

> **全尺寸示例数据（181 MB：原始 16-bit 输入 + 宏真实输出 `*-adjusted.tif`）走 COS 分发：**
> `https://my-website-1358159656.cos.ap-guangzhou.myqcloud.com/if-contrast/data/if-contrast-examples.zip`
> 真机运行宏时，输出为与输入同目录的 `*-adjusted.tif`（伪彩 RGB）和
> `FOV {样本名}-Merge-adjusted.tif`（合成图）；仓库内的小 PNG 只是降采样的视觉参考。

---

## 完整操作流程

### 第一步：准备数据

将原始单通道灰度 TIFF 按以下规则组织目录：

```
{工作目录}/
├── {样本A}/              ← 样本名任意（如患者ID、FOV编号）
│   ├── DAPI/             ← 文件夹名必须与脚本 CHANNELS 数组对应
│   │   └── xxx_TG440.tif
│   ├── CD8-AF488/        ← 文件夹名必须与脚本 CHANNELS 数组对应
│   │   └── xxx_TG520.tif
│   ├── PDL1-AF594/
│   │   └── xxx_TG570.tif
│   └── PD1-AF647/
│       └── xxx_TG650.tif
├── {样本B}/
│   └── ...（同样 4 个通道子文件夹）
└── ...
```

**命名铁律：子文件夹名必须与脚本 `CHANNELS` 数组的元素完全一致（大小写、连字符全部匹配）。**

---

### 第二步：打开 ImageJ 并加载宏

1. 双击 `C:\Users\A\Desktop\ImageJ\ImageJ.exe` 启动 ImageJ
2. 菜单栏：**Plugins → Macros → Run...**
3. 在弹出的文件选择框中，导航到本目录下的 `scripts/batch_adjust_mif.ijm`
4. 点击 Open

此时 ImageJ 会弹出 Log 窗口，宏开始运行。

---

### 第三步：选择工作目录

宏首先弹出一个文件夹选择对话框：
- 提示文字：`Choose the selected_images folder`
- 选择包含样本子文件夹的目录（例如 `D:\...\1_多通道批量对比度调整\examples\input\`）
- 点击 Select

---

### 第四步：逐个通道手动校准亮度/对比度

宏会按通道顺序弹出 **4 次校准对话框**。每次操作流程相同：

1. 宏自动打开当前通道下的一张 TIFF，并应用伪彩色 LUT
2. 弹出 **Brightness & Contrast (B&C)** 窗口，显示当前图像的直方图和 Min/Max 滑块
3. 弹出 **Action Required** 对话框，等待你确认

**操作步骤（每个通道重复 4 次）：**

| 通道顺序 | 通道名 | 伪彩色 | 你要做什么 |
|---------|--------|--------|-----------|
| 第 1 次 | DAPI | 蓝色 (Blue) | 拖动 Min/Max 滑块，使细胞核清晰可见，背景不过曝 |
| 第 2 次 | CD8-AF488 | 绿色 (Green) | 拖动 Min/Max 滑块，使阳性信号可见且不饱和 |
| 第 3 次 | PDL1-AF594 | 红色 (Red) | 拖动 Min/Max 滑块，同上 |
| 第 4 次 | PD1-AF647 | 紫红 (Magenta) | 拖动 Min/Max 滑块，同上 |

**⚠️ 关键注意：**

- **只拖动 Min 和 Max 滑块**，调整显示范围
- **绝对不要点击 B&C 窗口的 Apply 按钮！** Apply 会永久改变像素值，我们只需要记录显示范围
- 调整满意后，点击 Action Required 对话框的 **OK** 按钮
- 宏会自动记录当前通道的 (min, max) 参数，然后关闭该图像

**为什么只调一张图？** 你在参考样本上调好的参数会原封不动应用到所有样本的同一通道，保证所有图片风格一致。

---

### 第五步：等待批量处理完成

校准完成后，宏自动进入批处理模式（图像窗口会隐藏以加速）：

1. **逐个通道**：打开原始灰度图 → 应用你校准的 min/max → 伪彩 LUT → 转 RGB → 另存为 `*-adjusted.tif`
2. **合成 Merge 图**：重新打开 4 个通道 → Merge Channels → 转 RGB → 另存为 `FOV {样本名}-Merge-adjusted.tif`
3. 每个样本处理完后，宏自动关闭所有图像，继续下一个

处理进度会打印在 **ImageJ Log 窗口**中。完成后弹出 "Done" 提示框。

---

### 第六步：验证输出

随机抽查 2-3 个样本的输出：

1. **单通道检查**：在资源管理器中打开 `*-adjusted.tif`，确认颜色正确：
   - DAPI → 蓝色
   - CD8 → 绿色
   - PDL1 → 红色
   - PD1 → 紫红色
2. **Merge 检查**：打开 `*-Merge-adjusted.tif`，确认四个通道叠加清晰可辨、无明显过曝或欠曝
3. **一致性检查**：对比不同样本的同一通道，确认亮度风格一致
4. **Scale bar 检查**：确认原始图中烧录的 scale bar 仍然存在且清晰

如果某个通道效果不满意，删除所有 `*-adjusted.tif` 和 `*-Merge-adjusted.tif`，重新从第二步开始运行宏。

---

## 文件夹命名适配规则（换实验数据时的核心操作）

脚本 `scripts/batch_adjust_mif.ijm` 第 25 行定义了四个通道名：

```javascript
CHANNELS = newArray("DAPI", "CD8-AF488", "PDL1-AF594", "PD1-AF647");
```

**这条数组的每个元素 = 你必须创建的文件夹名。**

### 当前示例数据（Panel 1：CD8 / PDL1 / PD1）

| CHANNELS 元素 | 文件夹名 | 伪彩色 | 荧光染料 |
|-------------|---------|--------|---------|
| `"DAPI"` | `DAPI/` | 蓝 | DAPI |
| `"CD8-AF488"` | `CD8-AF488/` | 绿 | AF488 |
| `"PDL1-AF594"` | `PDL1-AF594/` | 红 | AF594 |
| `"PD1-AF647"` | `PD1-AF647/` | 紫红 | AF647 |

### 换到 Panel 2（FOXP3 / NOXA / CD4）时

**步骤 1**：修改 `scripts/batch_adjust_mif.ijm`，把第 25 行改成：

```javascript
CHANNELS = newArray("DAPI", "FOXP3-AF488", "NOXA-AF594", "CD4-AF647");
```

**步骤 2**：把数据按新文件夹名组织：

```
examples/
├── input/
│   └── patient_01/
│       ├── DAPI/              ← "DAPI"
│       ├── FOXP3-AF488/       ← "FOXP3-AF488"
│       ├── NOXA-AF594/        ← "NOXA-AF594"
│       └── CD4-AF647/         ← "CD4-AF647"
```

**常见错误：**

| 错误 | 后果 |
|------|------|
| 文件夹名写 `CD8` 但脚本写 `CD8-AF488` | 脚本找不到文件，报错退出 |
| 文件夹名写 `Dapi`（小写）但脚本写 `DAPI` | 大小写不匹配，找不到文件 |
| 少建了一个通道文件夹 | 该样本的该通道被跳过，不生成 Merge 图 |
| 多建了不相关的文件夹 | 不影响，脚本只找 CHANNELS 中列出的 |

---

## 脚本逻辑说明（了解即可，不需要改代码）

`batch_adjust_mif.ijm` 内部执行顺序：

```
main()
 ├── chooseRoot()           → 弹出文件夹选择框
 ├── calibrateParameters()  → 弹出 4 次 B&C 校准对话框，记录 min/max
 │     └── 每个通道：打开TIFF → LUT伪彩 → 等用户调B&C → 记录参数 → 关闭
 └── processAll()           → 批量遍历所有样本子文件夹
       └── processFov()     → 对每个样本：
             ├── 循环4通道：打开 → setMinAndMax() → LUT → RGB → 另存 -adjusted.tif
             └── 重新打开4通道 → Merge Channels → RGB → 另存 Merge-adjusted.tif
```

---

## 注意事项

1. **ImageJ 宏中不能出现中文字符**：脚本内的注释、提示窗口文字均为英文
2. **原始文件不被修改**：所有输出以 `-adjusted.tif` 结尾，存放在原始文件同目录
3. **重新校准**：如果校准不满意，删除所有 `*-adjusted.tif` 和 `*-Merge-*.tif`，重新运行宏
4. **Scale bar** 已在原始图中烧录，宏不会添加新的
5. **16-bit 推荐**：8-bit TIFF 也可用，但灰度级别少可能导致色阶不平滑

---

## 数据来源

| 文件 | 原始路径 |
|------|---------|
| 宏脚本 | `D:\小文章\data\临床-IHC-IF图片\batch_adjust_mif.ijm` |
| 工作流文档 | `D:\小文章\data\临床-IHC-IF图片\IHC-figure.md` |
| 方案文档 | `D:\小文章\data\临床-IHC-IF图片\plan-IHC-Fig.md` |
| 示例输入 | `D:\小文章\data\临床-IHC-IF图片\CRC_prospective\` |
