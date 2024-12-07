# -*- coding: utf-8 -*-

import gc
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
        connections.connect("default", host=config.MILVUS_SERVER, port=config.MILVUS_PORT, user=config.MILVUS_USER, password=config.MILVUS_PASSWORD)
        self.kb_collection = Collection(config.MILVUS_KB_NAME, consistency_level="Strong")
        self.kb_collection.load()
        self.config = config

    async def retrieve(self, query, topk):
        query_embeddings = self.embedder([query])
        res = self.kb_collection.search(
            query_embeddings["dense"], "dense_vector",
            {"metric_type": "L2"}, limit=topk * 2,
            output_fields=["chunk_content", "doc_name"]
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
