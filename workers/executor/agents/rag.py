import logging
from typing import Any

from llama_index.core import Document

from shared.events import WorkflowSnapshot
from shared.llama_embed import SageMakerLlamaEmbedding
from shared.rag_text import build_query_context, build_trade_summary
from shared.s3vectors_store import put_trade_vector, query_similar_trades
from shared.sagemaker_embed import embed_text_sync
from shared.settings import settings
from shared.trade_store import get_trades_by_ids, insert_trade, list_recent_trades

logger = logging.getLogger(__name__)

_embed_model = SageMakerLlamaEmbedding()


async def load_rag(
    snapshot: WorkflowSnapshot,
    market: dict | None = None,
    indicator: dict | None = None,
) -> dict[str, Any]:
    """Exact last-N from Postgres + semantic matches from S3 Vectors (same embed model)."""
    market = market or {}
    indicator = indicator or {}

    exact = await list_recent_trades(
        snapshot.workflow_id,
        limit=settings.rag_exact_window_n,
    )

    semantic: list[dict[str, Any]] = []
    query_text = build_query_context(snapshot, market, indicator)
    query_vec = _embed_model._get_query_embedding(query_text)
    if any(query_vec):
        hits = query_similar_trades(
            query_vec,
            workflow_id=snapshot.workflow_id,
            symbol=snapshot.trading_pair,
        )
        seen = {t.get("trade_id") for t in exact}
        for hit in hits:
            tid = hit.get("trade_id")
            if tid and tid not in seen:
                semantic.append(hit)
                seen.add(tid)

    snippets: list[dict[str, Any]] = []
    for row in exact:
        snippets.append(
            {
                "trade_id": row.get("trade_id"),
                "text": row.get("content_text"),
                "outcome": row.get("outcome"),
                "source": row.get("source"),
            }
        )

    missing_ids = [
        h["trade_id"]
        for h in semantic
        if h.get("trade_id") and not any(s.get("trade_id") == h["trade_id"] for s in snippets)
    ]
    if missing_ids:
        for row in await get_trades_by_ids(missing_ids):
            snippets.append(
                {
                    "trade_id": row.get("trade_id"),
                    "text": row.get("content_text"),
                    "outcome": row.get("outcome"),
                    "source": "semantic+postgres",
                }
            )
    for hit in semantic:
        if hit.get("content_text") and not any(
            s.get("trade_id") == hit.get("trade_id") for s in snippets
        ):
            snippets.append(
                {
                    "trade_id": hit.get("trade_id"),
                    "text": hit.get("content_text"),
                    "outcome": hit.get("outcome"),
                    "distance": hit.get("distance"),
                    "source": hit.get("source"),
                }
            )

    trading_id = exact[0].get("trade_id") if exact else None
    return {
        "trading_id": trading_id,
        "snippets": snippets,
        "exact_count": len(exact),
        "semantic_count": len(semantic),
        "query_text": query_text,
    }


async def save_rag(
    snapshot: WorkflowSnapshot,
    trade_result: dict,
    *,
    indicator: dict | None = None,
    mm_meta: dict | None = None,
    run_id: str | None = None,
) -> None:
    """Encode via SageMaker, store vector in S3 Vectors, persist trade row in Postgres."""
    if not trade_result.get("trade_id"):
        return
    if trade_result.get("outcome") not in ("win", "loss"):
        logger.debug("skip RAG write until trade settled outcome=%s", trade_result.get("outcome"))
        return

    summary = build_trade_summary(
        snapshot, trade_result, indicator=indicator, mm_meta=mm_meta
    )
    _ = Document(text=summary, metadata={"trade_id": trade_result.get("trade_id")})

    embedding = embed_text_sync(summary)
    if embedding is None:
        logger.info(
            "RAG encode skipped (no SageMaker) workflow=%s trade_id=%s",
            snapshot.workflow_id,
            trade_result.get("trade_id"),
        )
        return

    model_version = settings.sagemaker_embedding_model_id
    metadata = {
        "workflow_id": snapshot.workflow_id,
        "symbol": snapshot.trading_pair,
        "outcome": trade_result.get("outcome"),
        "direction": trade_result.get("direction"),
        "content_text": summary,
    }
    stored_vector = put_trade_vector(
        trade_id=str(trade_result["trade_id"]),
        embedding=embedding,
        metadata=metadata,
    )

    await insert_trade(
        trade_id=str(trade_result["trade_id"]),
        workflow_id=snapshot.workflow_id,
        run_id=run_id,
        symbol=snapshot.trading_pair,
        outcome=str(trade_result.get("outcome")),
        direction=trade_result.get("direction"),
        stake=_float_or_none(trade_result.get("stake")),
        profit=_float_or_none(trade_result.get("profit")),
        available_risk_after=_float_or_none(mm_meta.get("available_risk") if mm_meta else None),
        cycle_index=int(mm_meta["cycle_index"]) if mm_meta and mm_meta.get("cycle_index") is not None else None,
        content_text=summary,
        indicator_snapshot=indicator,
        embedding_model_version=model_version,
    )

    logger.info(
        "RAG write workflow=%s trade_id=%s dim=%s s3=%s",
        snapshot.workflow_id,
        trade_result.get("trade_id"),
        len(embedding),
        stored_vector,
    )


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
