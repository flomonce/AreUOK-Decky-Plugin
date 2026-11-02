#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "❌ 请使用 sudo 运行此脚本"
  exit 1
fi

# 获取真实用户和路径
REAL_USER=${SUDO_USER:-$(whoami)}
USER_HOME=$(eval echo "~$REAL_USER")
PLUGIN_DIR="$USER_HOME/homebrew/plugins/AreUOK"
TMP_DIR="/tmp/areuok-download"

echo "========================================="
echo " 🚀 开始在线安装 AreUOK"
echo "========================================="

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

echo "[1/3] 正在从 GitHub 下载成品..."
# 下载 GitHub 上的 main 分支压缩包
curl -sL https://github.com/flomonce/AreUOK-Decky-Plugin/archive/refs/heads/main.tar.gz | tar -xz -C "$TMP_DIR" --strip-components=1

if [ ! -d "$TMP_DIR/dist" ]; then
    echo "❌ 下载失败或仓库中缺少 dist 文件夹！"
    rm -rf "$TMP_DIR"
    exit 1
fi

echo "[2/3] 正在部署到 Decky 目录..."
rm -rf "$PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"

cp -r "$TMP_DIR/dist" "$PLUGIN_DIR/"
cp "$TMP_DIR/main.py" "$PLUGIN_DIR/"
cp "$TMP_DIR/plugin.json" "$PLUGIN_DIR/"

# 赋权
chown -R "$REAL_USER":"$REAL_USER" "$PLUGIN_DIR"
chmod +x "$PLUGIN_DIR/main.py"

echo "[3/3] 重启 Decky Loader..."
systemctl restart plugin_loader.service

rm -rf "$TMP_DIR"
echo "✅ 安装成功！请回到大屏查看。"
