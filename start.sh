#!/bin/bash

# 启动后端
cd /app/rag_service
echo "正在启动后端服务..."
uvicorn --host=0.0.0.0 --port=18888 --workers=1 fastapi_app:app &

# 启动前端
cd /app/rag_chat
echo "正在启动前端服务..."
npm run serve