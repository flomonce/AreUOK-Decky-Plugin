#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "❌ 请使用 sudo 运行此脚本"
  exit 1
fi

REAL_USER=${SUDO_USER:-$(whoami)}
USER_HOME=$(eval echo "~$REAL_USER")
PLUGIN_DIR="$USER_HOME/homebrew/plugins/AreUOK"
TMP_DIR="/tmp/areuok-download"
REPO_URL="https://github.com/flomonce/AreUOK-Decky-Plugin/archive/refs/heads/main.tar.gz"

echo "========================================="
echo " 🚀 开始安装 AreUOK"
echo "========================================="

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

echo "[1/3] 正在从 GitHub 下载源码 (可能需要魔法)..."
# 使用 -L 跟随重定向，--retry 增加重试机制，防止偶发断流
curl -L --retry 3 -# "$REPO_URL" -o "$TMP_DIR/main.tar.gz"

if [ ! -s "$TMP_DIR/main.tar.gz" ]; then
    echo "❌ 下载失败！文件为空，请检查网络。"
    exit 1
fi

echo "[2/3] 正在解压并部署文件..."
tar -xzf "$TMP_DIR/main.tar.gz" -C "$TMP_DIR" --strip-components=1

if [ ! -d "$TMP_DIR/dist" ]; then
    echo "❌ 解压后找不到 dist 文件夹！可能下载到了错误的网页。"
    exit 1
fi

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
