#!/bin/bash

# AMS 资产管理系统 启动脚本

# 进入后端目录
cd "$(dirname "$0")/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 初始化数据库
echo "初始化数据库..."
python -m app.init_db

# 启动服务
echo "启动服务..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
