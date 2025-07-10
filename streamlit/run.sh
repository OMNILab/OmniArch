#!/bin/bash

# 智慧会议系统启动脚本

echo "🎨 启动智慧会议系统..."

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.8+"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "app.py" ]; then
    echo "❌ 请在 streamlit 目录下运行此脚本"
    exit 1
fi

# 检查依赖是否安装
echo "📦 检查依赖..."
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📥 安装依赖..."
    pip install -r requirements.txt
fi

# 启动应用
echo "🚀 启动 Streamlit 应用..."
echo "📱 应用将在浏览器中打开: http://localhost:8501"
echo "🛑 按 Ctrl+C 停止应用"
echo ""

streamlit run app.py --server.port 8501 --server.address 0.0.0.0 