# 设置基础镜像
FROM python:3.12-slim

# 设置工作目录并拷贝代码
WORKDIR /app
COPY ./rag_chat /app/rag_chat
COPY ./rag_service /app/rag_service
COPY ./build.sh /app/build.sh
COPY ./start.sh /app/start.sh

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    yarn \
    && rm -rf /var/lib/apt/lists/*

# 安装后端依赖
RUN pip install -r /app/rag_service/requirements.txt

# 安装前端依赖
RUN npm install --prefix /app/rag_chat --registry=https://registry.npmmirror.com

# 赋予脚本可执行权限
RUN chmod u+x /app/start.sh

# 设置启动命令
ENTRYPOINT ["/app/start.sh"]