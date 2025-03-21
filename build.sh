#!/bin/bash

docker build -t blog-rag-image .

base_path=$(cd `dirname $0`; pwd)

docker run -itd --name blog-rag -h blog-rag \
-p 18888:18888 \
-p 28888:28888 \
-v ${base_path}/model_weight/bge-m3:/app/model_weight/bge-m3 \
-v ${base_path}/model_weight/bge-reranker-v2-m3:/app/model_weight/bge-reranker-v2-m3 \
-v ${base_path}/rag_chat/.env:/app/rag_chat/.env \
-v ${base_path}/rag_service/config.py:/app/rag_service/config.py \
blog-rag-image

docker update blog-rag --restart=always
