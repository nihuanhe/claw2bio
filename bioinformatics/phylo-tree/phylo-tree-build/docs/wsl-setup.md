# WSL2 Setup Guide for phylo-tree-build (Windows)

> 中文说明：本指南带你在 Windows 上装好 WSL2 + Ubuntu 24.04 + 建树工具链
> （bcgTree / IQ-TREE2 / MAFFT / parsnp）。约 30–60 分钟，只需做一次。
> 标注 **【截图 N】** 的位置需要插入实机截图（占位，待补）。

phylo-tree-build runs its compute steps (bcgTree, IQ-TREE2, parsnp) inside
**WSL2 (Windows Subsystem for Linux)** because these tools are Linux-native.
This guide takes a Windows machine from zero to a ready environment.

## 0. What you will install

| Component | Role | How |
|---|---|---|
| WSL2 + Ubuntu 24.04 | Linux environment inside Windows | Windows feature |
| Miniconda | package manager inside Ubuntu | wget installer |
| conda env `bcgtree` | bcgTree + parsnp + harvesttools | bioconda |
| IQ-TREE2, MAFFT | tree builder / aligner | apt |

## 1. Install WSL2 + Ubuntu 24.04

1. Open **PowerShell as Administrator** (Start → type "PowerShell" → right-click → Run as administrator).
   **【截图 1：以管理员身份运行 PowerShell】**
2. Run:

```powershell
wsl --install -d Ubuntu-24.04
```

3. **Restart** the computer when prompted.
4. After reboot, an Ubuntu window opens automatically and asks you to create a
   **Linux username and password** (the password is invisible while typing —
   this is normal). Remember this password; `sudo` needs it.
   **【截图 2：Ubuntu 首次启动创建用户】**
5. Verify: open PowerShell and run `wsl -l -v` — you should see
   `Ubuntu-24.04  Running  2` (VERSION must be **2**). If it shows 1, run
   `wsl --set-version Ubuntu-24.04 2`.
   **【截图 3：wsl -l -v 显示 VERSION 2】**

> Troubleshooting: if `wsl --install` fails with a virtualisation error, enable
> "Virtual Machine Platform" in BIOS/UEFI (VT-x/AMD-V) and Windows optional
> features, then retry. See https://learn.microsoft.com/windows/wsl/install

## 2. Choose where WSL lives (optional, recommended for small C: drives)

By default WSL installs on C:. To move the distro to another drive
(e.g. D:\WSL): export → unregister → import.

```powershell
wsl --export Ubuntu-24.04 D:\WSL\ubuntu2404.tar
wsl --unregister Ubuntu-24.04
wsl --import Ubuntu-24.04 D:\WSL\Ubuntu-24.04 D:\WSL\ubuntu2404.tar
```

**【截图 4：wsl --import 完成】**

## 3. Open an Ubuntu terminal

Start menu → "Ubuntu 24.04" (or run `wsl` in PowerShell). All remaining steps
happen **inside this Ubuntu window**.

**【截图 5：Ubuntu 终端窗口】**

## 4. Run the bootstrap script

Copy the skill's `scripts/00_bootstrap_ubuntu.sh` into Ubuntu (or call it
straight from the Windows drive via `/mnt/<盘符>/...`) and run:

```bash
bash 00_bootstrap_ubuntu.sh
```

It installs IQ-TREE2 + MAFFT (apt), Miniconda, and the conda env `bcgtree`
(bcgTree + parsnp + harvesttools). Expect 10–30 min depending on network.

**【截图 6：bootstrap 脚本运行完成，打印版本号】**

> 国内网络提示：若 apt/conda 很慢，先把 apt 源换成国内镜像
> （`sudo sed -i 's|archive.ubuntu.com|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources`），
> conda 换清华镜像（`~/.condarc` 配置详见清华镜像站文档）。

## 5. Apply the one-time bcgTree patch

bioconda 的 bcgTree 1.2.1 与新版 Gblocks 有一个已知兼容 bug（详见脚本头注释），
必须打一次补丁：

```bash
python3 patch_bcgtree_gblocks.py
# expect: bcgTree.pm patched OK
```

## 6. Sanity check

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate bcgtree
iqtree2 --version | head -1     # IQ-TREE 2.x
mafft --version | head -1       # v7.x
bcgTree.pl --help | head -3     # usage text
parsnp --version                # parsnp 1.x/2.x
```

All four should print versions without errors.
**【截图 7：四个工具版本号齐全】**

## 7. The golden path rules (读三遍)

1. **路径纪律**：bcgTree/Perl 遇到中文路径会崩。中间产物一律放纯 ASCII
   目录（脚本里的 `WORK`，默认 `~/phylo_work`）；基因组可以从中文路径拷入，
   但 bcgTree 运行目录必须纯英文。
2. Windows 盘在 WSL 里挂载为 `/mnt/c`、`/mnt/d`、`/mnt/e`……
3. 建树顺序：`01_run_bcgtree.sh` → `02_iqtree_main.sh`（→ 可选
   `03_parsnp_subtrees.sh`）。每个脚本只需改头部 `EDIT THESE` 变量。

---

## Screenshot checklist (待补截图清单)

| # | 内容 | 位置 |
|---|---|---|
| 1 | 以管理员身份运行 PowerShell | §1.2 |
| 2 | Ubuntu 首次启动创建用户 | §1.4 |
| 3 | `wsl -l -v` 显示 VERSION 2 | §1.5 |
| 4 | `wsl --import` 完成（可选节） | §2 |
| 5 | Ubuntu 终端窗口 | §3 |
| 6 | bootstrap 跑完打印版本 | §4 |
| 7 | 四工具版本号自检 | §6 |
