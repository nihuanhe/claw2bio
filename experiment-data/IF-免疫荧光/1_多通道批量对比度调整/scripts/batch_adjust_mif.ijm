// ============================================================
// 多色免疫荧光批量对比度调整宏
// ============================================================
// 功能：交互式校准 + 批量将 16-bit 单通道灰度 TIFF 转为伪彩 RGB TIFF
// 输入：{FOV编号}/{通道名}/*.tif  ← 原始单通道灰度TIFF（16-bit）
// 输出：每通道一个 *-adjusted.tif（伪彩色RGB） + 一个 Merge-adjusted.tif
//
// 通道映射：DAPI=蓝, FOXP3-AF488=绿, NOXA-AF594=红, CD4-AF647=紫红
// 所有FOV 同一通道使用完全相同的 min/max 对比度参数
// 原始文件不会被修改或覆盖
//
// 使用方法：
//   1. ImageJ → Plugins → Macros → Run
//   2. 选择包含 {FOV编号}/{通道名}/*.tif 结构的根目录
//   3. 逐个通道手动调整亮度/对比度（只调显示范围，不要点Apply）
//   4. 脚本自动批量处理所有FOV
// ============================================================

// -------------------- 用户可修改配置 --------------------
// 输出文件后缀：原文件名后附加此标记
OUTPUT_SUFFIX = "-adjusted";

// 通道名称数组（必须与输入目录下的子文件夹名一致）
// 索引 0/1/2/3 分别对应伪彩色 LUT 数组的对应位置
// ★ 换实验数据时只需改这一行 ★
CHANNELS = newArray("DAPI", "CD8-AF488", "PDL1-AF594", "PD1-AF647");

// 伪彩色查找表（ImageJ 内置 LUT 名称）
// DAPI=Blue(蓝), FOXP3=Green(绿), NOXA=Red(红), CD4=Magenta(紫红)
LUTS = newArray("Blue", "Green", "Red", "Magenta");
// --------------------------------------------------------

// ---- 全局变量 ----
// ROOT: 用户选择的根目录路径
// gMins[4]: 四个通道校准后的显示最小值
// gMaxs[4]: 四个通道校准后的显示最大值
var ROOT = "";
var gMins = newArray(4);
var gMaxs = newArray(4);


// ============================================================
// 工具函数
// ============================================================

// ---- 在目录中找到第一个 TIFF 文件（跳过已处理过的 *-adjusted.tif）----
// 参数: dir - 搜索的目录路径（以 / 结尾）
// 返回: 完整文件路径，未找到则返回空字符串
function findFirstTiff(dir) {
    list = getFileList(dir);
    for (i = 0; i < list.length; i++) {
        name = list[i];
        lower = toLowerCase(name);
        // 跳过已处理的输出文件，避免重复处理
        if ((endsWith(lower, ".tif") || endsWith(lower, ".tiff"))
                && indexOf(lower, OUTPUT_SUFFIX) < 0) {
            return dir + name;
        }
    }
    return "";
}


// ---- 关闭所有已打开的图像 ----
// 用途：批次处理时清空 ImageJ 的打开窗口，防止内存不足
function closeAllImages() {
    while (nImages > 0) {
        close();
    }
}


// ---- 从完整路径提取文件名部分 ----
// 示例: "D:/data/FOV 357/file.tif" → "file.tif"
function fileNameFromPath(path) {
    slash = lastIndexOf(path, "/");
    back = lastIndexOf(path, "\\");
    idx = maxOf(slash, back);
    if (idx >= 0) {
        return substring(path, idx + 1);
    }
    return path;
}


// ---- 从文件名去掉扩展名 ----
// 示例: "FOV 00357_TG440.tif" → "FOV 00357_TG440"
function baseNameWithoutExt(name) {
    dot = lastIndexOf(name, ".");
    if (dot >= 0) {
        return substring(name, 0, dot);
    }
    return name;
}


// ============================================================
// 阶段一：交互式参数校准
// ============================================================
// 选择一个参考FOV，用户手动调整每个通道的亮度/对比度，
// 脚本记录 min/max 值，后续所有 FOV 统一使用这些参数

function calibrateParameters() {
    // 0. 检测目录结构：平铺式（通道文件夹直接在根目录下）还是嵌套式（有FOV编号子文件夹）
    dirList = getFileList(ROOT);
    isFlat = false;
    for (i = 0; i < dirList.length; i++) {
        for (c = 0; c < 4; c++) {
            if (dirList[i] == CHANNELS[c] && File.isDirectory(ROOT + dirList[i])) {
                isFlat = true; break;
            }
        }
        if (isFlat) break;
    }

    if (isFlat) {
        // 平铺结构：ROOT/DAPI/xxx.tif, ROOT/CD8-AF488/xxx.tif, ...
        refDir = ROOT;
        print("Structure: FLAT (channels directly under ROOT)");
    } else {
        // 嵌套结构：ROOT/872/DAPI/xxx.tif, ROOT/880/DAPI/xxx.tif, ...（原逻辑）
        if (dirList.length == 0) {
            exit("ERROR: No folders found in " + ROOT);
        }
        refFov = "";
        for (i = 0; i < dirList.length; i++) {
            if (File.isDirectory(ROOT + dirList[i])) {
                refFov = dirList[i];
                break;
            }
        }
        if (refFov == "") {
            exit("ERROR: No FOV subfolders in " + ROOT);
        }
        refFovBase = replace(refFov, "/", "");
        refDir = ROOT + refFov;
        print("Reference FOV: " + refFovBase);
    }

    // 3. 逐个通道：打开参考 FOV 的 TIFF→ 用户手动调亮度→记录 min/max→关闭
    // 这一步本质是：你在单张图上调好"最佳视觉效果"，脚本记住你的选择
    for (c = 0; c < 4; c++) {
        // 获取该通道子文件夹路径
        chDir = refDir + CHANNELS[c] + "/";

        // 找到该通道下的第一个 TIFF 文件（作为参考）
        path = findFirstTiff(chDir);
        if (path == "") {
            exit("ERROR: No TIFF found in " + chDir);
        }

        // 打开图像（此时是 16-bit 灰度图）
        open(path);
        id = getImageID();
        selectImage(id);

        // 应用伪彩色 LUT（灰度→彩色显示）
        run(LUTS[c]);

        // 弹出 Brightness/Contrast 窗口
        // ★★★ 用户操作：拖动 Min/Max 滑块直到图像显示效果满意 ★★★
        // ★★★ 注意：不要点击 Apply！只调整显示范围即可 ★★★
        run("Brightness/Contrast...");
        waitForUser(
            "Calibrate " + CHANNELS[c],
            "Adjust Brightness/Contrast for " + CHANNELS[c] + " (" + LUTS[c] + "):\n" +
            "  1) Drag Min/Max until the channel looks good\n" +
            "  2) Click OK when done\n\n" +
            "Do NOT click Apply; only the display range is recorded."
        );

        // 记录用户调整后的 min/max 值
        getMinAndMax(minVal, maxVal);
        gMins[c] = minVal;
        gMaxs[c] = maxVal;
        print("Channel " + CHANNELS[c] + " recorded: min=" + gMins[c] + ", max=" + gMaxs[c]);

        // 关闭参考图像，释放内存
        close();
    }
}


// ============================================================
// 阶段二：处理单个 FOV
// ============================================================
// 对给定 FOV：
//  (a) 逐个通道：打开灰度图 → 应用统一 min/max → 伪彩色 → 另存为 -adjusted.tif
//  (b) 重新打开四个通道 → 合并为复合 RGB → 另存为 Merge-adjusted.tif

function processFov(fovName, fovDir) {
    fovBase = replace(fovName, "/", "");
    print("Processing FOV: " + fovBase);

    paths = newArray(4);    // 存储四个通道的 TIFF 路径，后续合并时用
    rgbSaved = true;        // 标记所有通道是否成功处理

    // ---- (a) 逐个通道保存伪彩色 RGB 图 ----
    for (c = 0; c < 4; c++) {
        chDir = fovDir + CHANNELS[c] + "/";
        path = findFirstTiff(chDir);
        if (path == "") {
            print("  SKIP: No TIFF in " + chDir);
            rgbSaved = false;
            break;
        }
        paths[c] = path;  // 保存路径，用于后续 Merge

        // 打开原始 16-bit 灰度图
        open(path);
        id = getImageID();
        selectImage(id);

        // 应用校准参数：设置显示范围 = 参考FOV 的 min/max
        // 这就是"所有FOV同一通道统一亮度"的核心操作
        setMinAndMax(gMins[c], gMaxs[c]);

        // 应用伪彩色 LUT（灰度值映射到颜色）
        run(LUTS[c]);

        // 转为 RGB 色彩空间（8-bit RGB × 3通道）
        run("RGB Color");

        // 另存为：原文件名-adjusted.tif，保存在通道子文件夹内
        srcName = File.getName(path);
        outBase = File.getNameWithoutExtension(srcName) + OUTPUT_SUFFIX;
        outPath = chDir + outBase + ".tif";
        saveAs("Tiff", outPath);
        print("  Saved channel RGB: " + outPath);
        close();
    }

    // 如果任何通道失败，跳过此 FOV 的 Merge 步骤
    if (!rgbSaved) {
        closeAllImages();
        return;
    }

    // ---- (b) 合并四个通道为一张复合图 ----
    // 重新打开原始 16-bit 灰度图（应用显示范围）
    mergeTitles = newArray(4);
    for (c = 0; c < 4; c++) {
        open(paths[c]);
        id = getImageID();
        selectImage(id);
        setMinAndMax(gMins[c], gMaxs[c]);
        mergeTitles[c] = getTitle();  // 记录窗口标题，用于 Merge 命令
    }

    // Merge Channels 命令参数格式:
    //   c1=红, c2=绿, c3=蓝, c4=灰, c5=青, c6=黄, c7=品红
    // 我们的映射：c1=NOXA(红), c2=FOXP3(绿), c3=DAPI(蓝), c5=CD4(品红)
    // 注意：这里的 c1-c7 是 ImageJ Merge 命令的固定槽位，不是通道索引
    //    c1 = 红色通道  → NOXA-AF594 (TG570, 索引2)
    //    c2 = 绿色通道  → FOXP3-AF488 (TG520, 索引1)
    //    c3 = 蓝色通道  → DAPI (TG440, 索引0)
    //    c5 = 青色(品红)通道 → CD4-AF647 (TG650, 索引3)
    mergeCmd = "c1=[" + mergeTitles[2] + "] c2=[" + mergeTitles[1]
             + "] c3=[" + mergeTitles[0] + "] c5=[" + mergeTitles[3] + "] create";
    run("Merge Channels...", mergeCmd);

    // 转为 RGB（此时四个通道叠在一起）
    run("RGB Color");

    // 保存在 FOV 根目录下
    mergePath = fovDir + "FOV " + fovBase + "-Merge" + OUTPUT_SUFFIX + ".tif";
    saveAs("Tiff", mergePath);
    print("  Saved merge RGB: " + mergePath);

    // 关闭本 FOV 的所有图像，准备处理下一个
    closeAllImages();
}


// ============================================================
// 阶段三：批量遍历所有 FOV
// ============================================================
// 扫描根目录下所有子文件夹，跳过非目录项，逐个调用 processFov

function processAll() {
    // 先检测是否是平铺结构（通道文件夹直接在 ROOT 下）
    dirList = getFileList(ROOT);
    isFlat = false;
    for (i = 0; i < dirList.length; i++) {
        for (c = 0; c < 4; c++) {
            if (dirList[i] == CHANNELS[c] && File.isDirectory(ROOT + dirList[i])) {
                isFlat = true; break;
            }
        }
        if (isFlat) break;
    }

    if (isFlat) {
        // 平铺结构：根目录就是唯一的"FOV"
        rootBase = ROOT;
        if (endsWith(rootBase, "/")) {
            rootBase = substring(rootBase, 0, lengthOf(rootBase) - 1);
        }
        slash = lastIndexOf(rootBase, "/");
        back = lastIndexOf(rootBase, "\\");
        idx = maxOf(slash, back);
        if (idx >= 0) {
            fovName = substring(rootBase, idx + 1);
        } else {
            fovName = rootBase;
        }
        processFov(fovName, ROOT);
    } else {
        // 嵌套结构：遍历所有 FOV 子文件夹（原逻辑）
        for (i = 0; i < dirList.length; i++) {
            fovName = dirList[i];
            fovDir = ROOT + fovName;
            if (!File.isDirectory(fovDir)) continue;
            processFov(fovName, fovDir);
        }
    }
}


// ============================================================
// 选择工作目录
// ============================================================
// 弹出文件夹选择对话框，用户选择包含 {FOV编号}/{通道名}/*.tif 的根目录
// 返回时将路径中的反斜杠统一为前斜杠，并在末尾加 /

function chooseRoot() {
    path = getDirectory("Choose the selected_images folder");
    if (path == "") {
        exit("ERROR: No folder selected.");
    }
    // 统一路径分隔符为前斜杠
    path = replace(path, "\\", "/");
    if (!endsWith(path, "/")) {
        path = path + "/";
    }
    return path;
}


// ============================================================
// 主程序入口
// ============================================================

// 1. 用户选择工作根目录
ROOT = chooseRoot();
print("Working directory: " + ROOT);

// 2. 校准阶段（交互式，非批处理模式）
//    弹出 B&C 窗口供用户手动调整，此时不隐藏图像
setBatchMode(false);
calibrateParameters();

// 3. 批量处理阶段（批处理模式）
//    隐藏图像窗口以加速处理，完成后恢复
setBatchMode(true);
processAll();
setBatchMode(false);

// 4. 完成提示
print("Batch processing finished.");
showMessage("Done",
    "Batch contrast adjustment finished.\nOutput is in:\n" + ROOT);
