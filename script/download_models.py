# -*- coding: utf-8 -*-

import os
from huggingface_hub import snapshot_download

model_repos = [
    "Qwen/QwQ-32B",
    "Qwen/Qwen2.5-7B-Instruct",
    "BAAI/bge-m3",
    "BAAI/bge-reranker-v2-m3"
]

base_dir = "../model_weight"

for repo_id in model_repos:
    model_name = repo_id.split("/")[-1]
    local_dir = os.path.join(base_dir, model_name)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    print(f"Downloading model {repo_id} to {local_dir}...")
    snapshot_download(repo_id=repo_id, local_dir=local_dir)

print("All models downloaded successfully.")
