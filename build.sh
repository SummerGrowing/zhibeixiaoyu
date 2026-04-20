#!/usr/bin/env bash
# Render 构建脚本
set -e

echo "=== 智备小语 构建 ==="
echo "安装 Python 依赖..."
pip install -r zhibei_backend/requirements.txt

echo "构建完成！"
