from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class WorkflowSnapshot(BaseModel):
    workflow_id: str
    user_id: str
    name: str
    trading_pair: str
    trading_type: str
    starting_time: datetime
    one_day_minimum_trade: int
    bot_rules: list[dict[str, Any]] = Field(default_factory=list)
    graph_definition: dict[str, Any] | None = None
    deriv_app_id: str | None = None
    deriv_api_token: str | None = None
    risk_capital: float = 5.0
    mm_cycle_trades: int = 10
    mm_target_wins: int = 6
    mm_payout: float = 1.95
    account_currency: str = "USD"
    contract_strategy: str = "rise_fall"
    duration_ticks: int = 2


class WorkflowScheduledEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: Literal["workflow.scheduled"] = "workflow.scheduled"
    schedule_id: str
    snapshot: WorkflowSnapshot
    priority: int = 0
