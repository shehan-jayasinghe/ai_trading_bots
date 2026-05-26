"""Async Postgres pool and schema bootstrap for worker trade storage."""
from __future__ import annotations

import logging
import re

import asyncpg

from shared.settings import settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS trades (
    trade_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    run_id TEXT,
    symbol TEXT NOT NULL,
    outcome TEXT NOT NULL,
    direction TEXT,
    stake DOUBLE PRECISION,
    profit DOUBLE PRECISION,
    available_risk_after DOUBLE PRECISION,
    cycle_index INTEGER,
    content_text TEXT NOT NULL,
    indicator_snapshot JSONB,
    embedding_model_version TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS trades_workflow_created_idx
    ON trades (workflow_id, created_at DESC);
"""


def _asyncpg_dsn(url: str) -> str:
    """Normalize SQLAlchemy-style URL for asyncpg."""
    raw = (url or "").strip()
    if not raw:
        return ""
    return re.sub(r"^postgresql\+asyncpg://", "postgresql://", raw)


async def get_pool() -> asyncpg.Pool | None:
    global _pool
    dsn = _asyncpg_dsn(settings.postgres_database_url)
    if not dsn:
        return None
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
        async with _pool.acquire() as conn:
            await conn.execute(_SCHEMA_SQL)
        logger.info("Postgres pool ready (trades schema ensured)")
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
