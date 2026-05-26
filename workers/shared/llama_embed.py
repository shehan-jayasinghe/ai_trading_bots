"""LlamaIndex embedding adapter — same SageMaker model for ingest and query."""
from __future__ import annotations

from llama_index.core.base.embeddings.base import BaseEmbedding

from shared.sagemaker_embed import embed_text_sync


class SageMakerLlamaEmbedding(BaseEmbedding):
    """Wraps SageMaker endpoint so LlamaIndex Documents use one encoding model."""

    model_name: str = "sagemaker-minilm"
    embed_batch_size: int = 1

    def _get_text_embedding(self, text: str) -> list[float]:
        vec = embed_text_sync(text)
        if vec:
            return vec
        return [0.0] * 384

    def _get_query_embedding(self, query: str) -> list[float]:
        return self._get_text_embedding(query)

    async def _aget_text_embedding(self, text: str) -> list[float]:
        return self._get_text_embedding(text)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._get_query_embedding(query)
