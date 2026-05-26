"""Build narrative text for RAG encode (trade write) and decode (query)."""
from __future__ import annotations

from typing import Any

from shared.events import WorkflowSnapshot


def build_trade_summary(
    snapshot: WorkflowSnapshot,
    trade_result: dict,
    *,
    indicator: dict | None = None,
    mm_meta: dict | None = None,
) -> str:
    parts = [
        f"workflow={snapshot.name}",
        f"workflow_id={snapshot.workflow_id}",
        f"symbol={snapshot.trading_pair}",
        f"outcome={trade_result.get('outcome')}",
        f"profit={trade_result.get('profit')}",
        f"stake={trade_result.get('stake')}",
        f"direction={trade_result.get('direction')}",
    ]
    if indicator:
        parts.append(f"indicator_direction={indicator.get('direction')}")
    if mm_meta:
        parts.append(f"mm_capital={mm_meta.get('available_risk')}")
        parts.append(f"cycle_index={mm_meta.get('cycle_index')}")
    return " ".join(str(p) for p in parts if p is not None)


def build_query_context(
    snapshot: WorkflowSnapshot,
    market: dict,
    indicator: dict,
) -> str:
    direction = indicator.get("direction", "neutral")
    prices = market.get("prices") or market.get("ticks") or []
    tail = prices[-5:] if isinstance(prices, list) else []
    return (
        f"workflow_id={snapshot.workflow_id} symbol={snapshot.trading_pair} "
        f"indicator_direction={direction} recent_prices={tail}"
    )
