"""OLTP trade rows for exact RAG window retrieval."""
from __future__ import annotations

import json
import logging
from typing import Any

from shared.postgres import get_pool

logger = logging.getLogger(__name__)


async def insert_trade(
    *,
    trade_id: str,
    workflow_id: str,
    run_id: str | None,
    symbol: str,
    outcome: str,
    direction: str | None,
    stake: float | None,
    profit: float | None,
    available_risk_after: float | None,
    cycle_index: int | None,
    content_text: str,
    indicator_snapshot: dict[str, Any] | None,
    embedding_model_version: str,
) -> None:
    pool = await get_pool()
    if pool is None:
        logger.warning("skip trade insert: POSTGRES_DATABASE_URL not set")
        return

    indicator_json = json.dumps(indicator_snapshot or {})
    await pool.execute(
        """
        INSERT INTO trades (
            trade_id, workflow_id, run_id, symbol, outcome, direction,
            stake, profit, available_risk_after, cycle_index,
            content_text, indicator_snapshot, embedding_model_version
        ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12::jsonb,$13)
        ON CONFLICT (trade_id) DO UPDATE SET
            outcome = EXCLUDED.outcome,
            profit = EXCLUDED.profit,
            content_text = EXCLUDED.content_text,
            indicator_snapshot = EXCLUDED.indicator_snapshot,
            embedding_model_version = EXCLUDED.embedding_model_version
        """,
        trade_id,
        workflow_id,
        run_id,
        symbol,
        outcome,
        direction,
        stake,
        profit,
        available_risk_after,
        cycle_index,
        content_text,
        indicator_json,
        embedding_model_version,
    )


async def list_recent_trades(workflow_id: str, limit: int = 10) -> list[dict[str, Any]]:
    pool = await get_pool()
    if pool is None:
        return []

    rows = await pool.fetch(
        """
        SELECT trade_id, workflow_id, run_id, symbol, outcome, direction,
               stake, profit, available_risk_after, cycle_index,
               content_text, indicator_snapshot, embedding_model_version, created_at
        FROM trades
        WHERE workflow_id = $1
        ORDER BY created_at DESC
        LIMIT $2
        """,
        workflow_id,
        limit,
    )
    result: list[dict[str, Any]] = []
    for row in rows:
        snap = row["indicator_snapshot"]
        if isinstance(snap, str):
            snap = json.loads(snap) if snap else {}
        result.append(
            {
                "trade_id": row["trade_id"],
                "workflow_id": row["workflow_id"],
                "run_id": row["run_id"],
                "symbol": row["symbol"],
                "outcome": row["outcome"],
                "direction": row["direction"],
                "stake": row["stake"],
                "profit": row["profit"],
                "available_risk_after": row["available_risk_after"],
                "cycle_index": row["cycle_index"],
                "content_text": row["content_text"],
                "indicator_snapshot": snap,
                "embedding_model_version": row["embedding_model_version"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "source": "postgres_exact",
            }
        )
    return result


async def get_trades_by_ids(trade_ids: list[str]) -> list[dict[str, Any]]:
    if not trade_ids:
        return []
    pool = await get_pool()
    if pool is None:
        return []

    rows = await pool.fetch(
        """
        SELECT trade_id, content_text, outcome, profit, direction, symbol, created_at
        FROM trades
        WHERE trade_id = ANY($1::text[])
        """,
        trade_ids,
    )
    return [
        {
            "trade_id": row["trade_id"],
            "content_text": row["content_text"],
            "outcome": row["outcome"],
            "profit": row["profit"],
            "direction": row["direction"],
            "symbol": row["symbol"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "source": "postgres_lookup",
        }
        for row in rows
    ]
