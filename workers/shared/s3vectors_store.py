"""Amazon S3 Vectors PutVectors / QueryVectors for trade RAG."""
from __future__ import annotations

import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from shared.settings import settings

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384


def _client():
    region = (settings.aws_region or settings.bedrock_region or "us-west-1").strip()
    return boto3.client("s3vectors", region_name=region)


def _configured() -> bool:
    return bool(
        (settings.s3_vectors_bucket_name or "").strip()
        and (settings.s3_vectors_index_name or "").strip()
    )


def put_trade_vector(
    *,
    trade_id: str,
    embedding: list[float],
    metadata: dict[str, Any],
) -> bool:
    if not _configured():
        return False
    if len(embedding) != settings.s3_vectors_embedding_dimension:
        logger.warning(
            "embedding dim %s != index dim %s",
            len(embedding),
            settings.s3_vectors_embedding_dimension,
        )
        return False

    vector = {
        "key": trade_id,
        "data": {"float32": [float(x) for x in embedding]},
        "metadata": metadata,
    }
    try:
        _client().put_vectors(
            vectorBucketName=settings.s3_vectors_bucket_name.strip(),
            indexName=settings.s3_vectors_index_name.strip(),
            vectors=[vector],
        )
        return True
    except (ClientError, BotoCoreError) as exc:
        logger.warning("S3 Vectors put_vectors failed: %s", exc)
        return False


def query_similar_trades(
    query_embedding: list[float],
    *,
    workflow_id: str,
    symbol: str | None = None,
    top_k: int | None = None,
) -> list[dict[str, Any]]:
    if not _configured() or not query_embedding:
        return []

    k = top_k or settings.rag_semantic_top_k
    filt: dict[str, Any] = {"workflow_id": workflow_id}
    if symbol:
        filt["symbol"] = symbol

    try:
        response = _client().query_vectors(
            vectorBucketName=settings.s3_vectors_bucket_name.strip(),
            indexName=settings.s3_vectors_index_name.strip(),
            queryVector={"float32": [float(x) for x in query_embedding]},
            topK=k,
            filter=filt,
            returnDistance=True,
            returnMetadata=True,
        )
    except (ClientError, BotoCoreError) as exc:
        logger.warning("S3 Vectors query_vectors failed: %s", exc)
        return []

    hits: list[dict[str, Any]] = []
    for item in response.get("vectors") or []:
        meta = item.get("metadata") or {}
        hits.append(
            {
                "trade_id": item.get("key"),
                "distance": item.get("distance"),
                "content_text": meta.get("content_text") or meta.get("source_text"),
                "outcome": meta.get("outcome"),
                "symbol": meta.get("symbol"),
                "workflow_id": meta.get("workflow_id"),
                "source": "s3vectors_semantic",
            }
        )
    return hits
