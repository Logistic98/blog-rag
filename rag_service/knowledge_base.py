# -*- coding: utf-8 -*-

import gc

import numpy as np
import torch
from pymilvus import Collection, connections
from pymilvus.model.hybrid import BGEM3EmbeddingFunction
from pymilvus.model.reranker import BGERerankFunction
from config import Config


class KnowledgeBase:
    def __init__(self, config: Config):
        torch.cuda.empty_cache()
        gc.collect()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embedder = BGEM3EmbeddingFunction(
            model_name=config.EMBEDDING_MODEL, use_fp16=False, device=device
        )
        self.use_reranker = config.USE_RERANKER
        self.reranker = (
            BGERerankFunction(model_name=config.RERANKING_MODEL, device=device)
            if self.use_reranker else None
        )
        connections.connect(
            "default",
            host=config.MILVUS_SERVER,
            port=config.MILVUS_PORT,
            user=config.MILVUS_USER,
            password=config.MILVUS_PASSWORD
        )
        self.kb_collection = Collection(config.MILVUS_KB_NAME, consistency_level="Strong")
        self.kb_collection.load()
        self.config = config

    async def retrieve(self, query, topk, file_types=['chunk']):
        """
        根据查询和指定的文件类型检索文档片段。

        参数:
            query (str): 用户查询。
            topk (int): 每种文件类型检索的文档数量。
            file_types (list): 要检索的文件类型列表（例如 ['toc', 'metadata', 'chunk']）。

        返回:
            list: 检索到的文档片段。
            list: 参考文档名称列表。
        """
        query_embeddings = self.embedder([query])
        query_embeddings["dense"] = query_embeddings["dense"] / np.linalg.norm(
            query_embeddings["dense"], axis=1, keepdims=True
        )

        if len(file_types) == 1:
            filter_expr = f"file_type == '{file_types[0]}'"
        else:
            file_types_str = " or ".join([f"file_type == '{ft}'" for ft in file_types])
            filter_expr = f"({file_types_str})"

        res = self.kb_collection.search(
            query_embeddings["dense"], "dense_vector",
            {"metric_type": "COSINE"}, limit=topk,
            output_fields=["chunk_content", "doc_name"],
            expr=filter_expr
        )
        hits = res[0]
        if self.use_reranker:
            result_texts = [hit.entity.get("chunk_content") for hit in hits]
            content_to_doc_name = {hit.entity.get("chunk_content"): hit.entity.get("doc_name") for hit in hits}
            results = self.reranker(query, result_texts, top_k=topk)
            doc_names = [content_to_doc_name.get(hit.text) for hit in results if content_to_doc_name.get(hit.text)]
            unique_doc_names = list(dict.fromkeys(doc_names))
            references = unique_doc_names
            return [
                       {
                           "text": hit.text,
                           "score": hit.score,
                           "doc_name": content_to_doc_name.get(hit.text)
                       } for hit in results
                   ], references
        else:
            chunks = []
            doc_names = []
            for hit in hits:
                doc_name = hit.entity.get("doc_name")
                if doc_name:
                    doc_names.append(doc_name)
                    chunks.append(
                        {
                            "text": hit.entity.get("chunk_content"),
                            "score": hit.distance,
                            "doc_name": doc_name
                        }
                    )
            unique_doc_names = list(dict.fromkeys(doc_names))
            references = unique_doc_names
            return chunks, references