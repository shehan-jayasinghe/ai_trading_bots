from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from shared.events import WorkflowSnapshot


class TradeState(BaseModel):
    """LangGraph executor state (Pydantic so StateGraph satisfies type checkers)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    run_id: str = ""
    attempt_id: str = ""
    snapshot: WorkflowSnapshot
    market_packet: dict[str, Any] = Field(default_factory=dict)
    indicator_signal: dict[str, Any] = Field(default_factory=dict)
    rag_context: dict[str, Any] = Field(default_factory=dict)
    decision: dict[str, Any] = Field(default_factory=dict)
    stake: float = 0.0
    trade_result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
