"""Persist executor results on Workflow (Postgres)."""
from __future__ import annotations

import json
import logging
from typing import Any

import asyncpg

from shared.settings import settings

logger = logging.getLogger(__name__)


def _asyncpg_dsn(url: str) -> str:
    return url.replace("postgresql+asyncpg://", "postgresql://", 1)


async def save_last_trade(
    workflow_id: str,
    *,
    run_id: str,
    trade_result: dict[str, Any],
) -> None:
    dsn = settings.postgres_database_url.strip()
    if not dsn:
        logger.warning("POSTGRES_DATABASE_URL not set; skip saving last trade")
        return

    payload = {
        "run_id": run_id,
        **trade_result,
    }
    sql = """
        UPDATE "Workflow"
        SET "lastTradeResult" = $1::jsonb
        WHERE id = $2
    """
    try:
        conn = await asyncpg.connect(_asyncpg_dsn(dsn))
        try:
            await conn.execute(sql, json.dumps(payload), workflow_id)
        finally:
            await conn.close()
        logger.info("saved last trade workflow=%s run_id=%s", workflow_id, run_id)
    except Exception:
        logger.exception("failed to save last trade workflow=%s", workflow_id)
