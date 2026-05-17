from typing import Any, TypedDict

from shared.events import WorkflowSnapshot


class TradeState(TypedDict, total=False):
    run_id: str
    attempt_id: str
    snapshot: WorkflowSnapshot
    market_packet: dict[str, Any]
    indicator_signal: dict[str, Any]
    rag_context: dict[str, Any]
    decision: dict[str, Any]
    stake: float
    trade_result: dict[str, Any]
    error: str | None
