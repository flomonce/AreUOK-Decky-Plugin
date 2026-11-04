# AreUOK - Steam Deck / Bazzite UU 加速器监控插件

> *“Are U OK?” —— 一款极度轻量、零轮询的 Decky 插件，用于实时监控 Steam Deck (SteamOS / Bazzite) 上网易 UU 加速器的状态。*

你是否经历过：打游戏正到关键时刻突然卡顿，切出侧边栏才绝望地发现加速器早就断了？
或者，你是否为了排查一个 Decky 插件的底层 Bug，熬到深夜对着屏幕发出灵魂拷问：*“Are U OK？”*

这就是这个插件诞生的原因。它会在后台静默监控 UU 加速器创建的 TUN 虚拟网卡，只要网络状态一有变化，立刻通过 SteamOS 原生 Toast 弹窗通知你。

本插件代码完全由deepseek生成。

## ✨ 核心特性

*   **⚡ 纯事件驱动（拒绝轮询）**：彻底抛弃耗电的 `setInterval` 轮询。底层利用 Linux 原生的 `ip monitor` 监听内核 Netlink 事件，后台 CPU 占用率真正为 **0%**。
*   **🔔 原生系统级通知**：加速器连接或断开时，无论在不在插件面板，屏幕右上角都会瞬间弹出系统级提示。
*   **⏰ 冷启动与唤醒完美适配**：开机和睡眠唤醒时自动检测状态。加入了动态 3 秒防吞缓冲，确保你每次都能看到完整的弹窗动画。
*   **🎛️ 把电量控制权交给你**：面板内自带“后台监听”开关，不想用时一键彻底关闭底层进程，状态自动持久化保存。
*   **🧹 干净且标准**：完全遵循 Decky 官方标准的前后端架构，代码极致精简，没有魔法。

## 📦 安装方法

### 方法一：Decky 开发者模式安装（最推荐）
1. 前往本仓库的 [Releases](https://github.com/flomonce/AreUOK-Decky-Plugin/releases) 页面，下载最新版的 `AreUOK.zip`。
2. 将 ZIP 文件传到你的 Steam Deck 上。
3. 呼出 Decky 侧边栏，进入 **设置 -> 开发者 (Developer) -> 从 ZIP 文件安装插件**。
4. 选择刚下载的 ZIP 文件，等待安装完成并重启 Decky 即可。

### 方法二：手动安装
1. 下载并解压最新的 ZIP 包。
2. 将解压出来的 `AreUOK` 文件夹直接复制到 `~/homebrew/plugins/` 目录下。
3. 重启 Decky 服务（或重启设备）。

## 💡 使用说明
安装完成后，在 Decky 侧边栏找到 **ARE U OK**：
*   **当前加速状态**：实时显示 TUN 网卡的连接状态。
*   **后台状态监听**：保持开启即可享受无感的后台通知。开关状态会自动保存在浏览器本地。

## 🛠️ 从源码构建

依赖环境：Node.js >= 18, pnpm, Python 3.11+

```bash
# 1. 安装依赖
pnpm install

# 2. 编译前端
pnpm run build

# 3. 打包（注意：Decky 要求 ZIP 内必须套一层外壳文件夹）
mkdir AreUOK
cp -r dist main.py package.json plugin.json AreUOK/
zip -r AreUOK.zip AreUOK/
rm -rf AreUOK
```
## 📄 开源协议 (License)

本项目基于 [MIT License](LICENSE) 协议开源。
