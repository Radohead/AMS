#!/bin/bash

# AMS 前端启动脚本

# 进入前端目录
cd "$(dirname "$0")/frontend"

# 安装依赖
echo "安装前端依赖..."
npm install

# 启动开发服务器
echo "启动前端开发服务器..."
npm run dev
