// ============================================
// Western Blot 定量宏脚本
// 功能：自动预处理 + 支持手动顺序 / 自动坐标排序 + 一键导出 CSV
// 保存位置：与当前打开图片同目录，文件名相同，扩展名改为 .csv
// 参考教程：https://www.iivd.net/forum.php?mod=viewthread&action=printable&tid=80534
// ============================================

// ========== 用户配置区（可按需修改） ==========
autoSort = true;              // true = 自动按坐标排序; false = 严格使用 ROI Manager 原有顺序
nCols = 2;                    // 自动排序时，每行包含的条带数（列数）
rollingBallRadius = 50;       // Subtract Background 半径，按图片分辨率调整
// =============================================

// ---------- 前置检查：ROI Manager 不能为空 ----------
// 本脚本要求用户先手动框选条带并按 T 添加到 ROI Manager，然后再运行脚本
n = roiManager("count");
if (n == 0) {
    showMessage("Missing ROIs",
        "ROI Manager is empty.\n\n" +
        "Please do the following BEFORE running this macro:\n" +
        "1. Use the Rectangle or Freehand tool to draw a selection around each band.\n" +
        "2. Press 'T' to add each selection to the ROI Manager.\n" +
        "3. Run this macro again.\n\n" +
        "Note: If autoSort=true, ROI order does not matter.\n" +
        "If autoSort=false, add ROIs strictly in row order (left to right, top to bottom).");
    exit("ROI Manager is empty.");
}

// ---------- 步骤1: 自动预处理 ----------
// 转为 8-bit 灰度图
run("8-bit");

// 使用 Rolling Ball 算法去除背景（参考网页步骤）
// Light background 对应"白背景、黑条带"的 WB 图
run("Subtract Background...", "rolling=" + rollingBallRadius + " light");

// 设置测量参数：Area, Mean, Min, Max, Integrated Density
run("Set Measurements...", "area mean min max integrated redirect=None decimal=3");

// 设置单位为像素
run("Set Scale...", "distance=0 known=0 pixel=1 unit=pixel");

// 反转亮度：黑条带变为亮条带，使"越黑 = 数值越大"
run("Invert");

if (autoSort) {
    // ---------- 自动排序模式 ----------
    
    // 收集每个 ROI 的中心坐标和原始索引
    xs = newArray(n);
    ys = newArray(n);
    idx = newArray(n);
    for (i = 0; i < n; i++) {
        roiManager("select", i);
        getSelectionBounds(x, y, w, h);
        xs[i] = x + w/2;
        ys[i] = y + h/2;
        idx[i] = i;
    }
    
    // 按 Y 坐标排序（从上到下，冒泡排序）
    for (i = 0; i < n - 1; i++) {
        for (j = 0; j < n - 1 - i; j++) {
            if (ys[j] > ys[j+1]) {
                tmp = ys[j]; ys[j] = ys[j+1]; ys[j+1] = tmp;
                tmp = xs[j]; xs[j] = xs[j+1]; xs[j+1] = tmp;
                tmp = idx[j]; idx[j] = idx[j+1]; idx[j+1] = tmp;
            }
        }
    }
    
    // 按行分组，每行内按 X 坐标排序（从左到右）
    nRows = floor(n / nCols);
    if (n % nCols > 0) nRows += 1;
    for (row = 0; row < nRows; row++) {
        start = row * nCols;
        // 计算该行的实际列数（最后一行可能不足 nCols 个）
        actualCols = nCols;
        if (start + actualCols > n) actualCols = n - start;
        end = start + actualCols - 1;
        // 至少需要2个元素才能排序
        if (actualCols >= 2) {
            for (i = start; i < end; i++) {
                for (j = start; j < end - (i - start); j++) {
                    if (xs[j] > xs[j+1]) {
                        tmp = xs[j]; xs[j] = xs[j+1]; xs[j+1] = tmp;
                        tmp = ys[j]; ys[j] = ys[j+1]; ys[j+1] = tmp;
                        tmp = idx[j]; idx[j] = idx[j+1]; idx[j+1] = tmp;
                    }
                }
            }
        }
    }
    
    // 生成预览图，在 ROI 中心标注排序后的红色编号
    run("Duplicate...", "title=Sorting_Preview");
    selectWindow("Sorting_Preview");
    setFont("SansSerif", 20, "antialiased");
    setColor("red");
    for (i = 0; i < n; i++) {
        roiManager("select", idx[i]);
        getSelectionBounds(x, y, w, h);
        cx = x + w/2 - 6;
        cy = y + h/2 + 6;
        drawString("" + (i+1), cx, cy);
    }
    
    // 等待用户确认排序结果
    // getBoolean 只接受单参数，标题和正文需合并
    confirmed = getBoolean("Sorting Preview\n\nRed numbers (1,2,3...) are overlaid on the image.\nPlease verify: Row 1 should be 1,2; Row 2 should be 3,4; and so on.\nIs the order correct?");
    
    // 关闭预览图，回到原图
    selectWindow("Sorting_Preview");
    close();
    dir = getInfo("image.directory");
    name = getInfo("image.filename");
    selectWindow(name);
    
    if (!confirmed) {
        exit("Cancelled. Please adjust ROI positions or the nCols parameter and rerun.");
    }
    
    // 按排序后的顺序逐个测量
    run("Clear Results");
    for (i = 0; i < n; i++) {
        roiManager("select", idx[i]);
        roiManager("measure");
    }
    
} else {
    // ---------- 手动顺序模式 ----------
    run("Clear Results");
    roiManager("deselect");
    roiManager("measure");
}

// ---------- 步骤4: 自动保存 CSV ----------
// 获取当前图片的路径和文件名
// 在同目录下保存同名 CSV（扩展名改为 .csv）
dir = getInfo("image.directory");
name = getInfo("image.filename");

if (dir == "null" || name == "null") {
    // 如果无法获取路径（如图片未保存），弹出文件夹选择对话框
    csvPath = getDir("Please choose a folder to save the CSV") + "wb_results.csv";
} else {
    // 去掉原扩展名，改为 .csv
    dotIndex = lastIndexOf(name, ".");
    if (dotIndex > 0) {
        baseName = substring(name, 0, dotIndex);
    } else {
        baseName = name;
    }
    csvPath = dir + baseName + ".csv";
}

saveAs("Results", csvPath);
showMessage("Done", "Measurement complete! " + n + " ROIs analyzed.\nResults saved to:\n" + csvPath);
