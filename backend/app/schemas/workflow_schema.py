from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.workflow_status import WorkflowStatus


class WorkflowCreate(BaseModel):
    name: str
    trading_pair: str
    trading_type: str
    starting_time: datetime
    one_day_minimum_trade: str
    deriv_app_id: Optional[str] = Field(default=None, alias="derivAppId")
    deriv_api_token: Optional[str] = Field(default=None, alias="derivApiToken")
    risk_capital: float = Field(default=5.0, alias="riskCapital")
    mm_cycle_trades: int = Field(default=10, alias="mmCycleTrades")
    mm_target_wins: int = Field(default=6, alias="mmTargetWins")
    mm_payout: float = Field(default=1.95, alias="mmPayout")
    account_currency: str = Field(default="USD", alias="accountCurrency")
    contract_strategy: str = Field(default="rise_fall", alias="contractStrategy")
    duration_ticks: int = Field(default=2, alias="durationTicks")

    model_config = ConfigDict(populate_by_name=True)


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    trading_pair: Optional[str] = None
    trading_type: Optional[str] = None
    starting_time: Optional[datetime] = None
    one_day_minimum_trade: Optional[str] = None
    deriv_app_id: Optional[str] = Field(default=None, alias="derivAppId")
    deriv_api_token: Optional[str] = Field(default=None, alias="derivApiToken")
    risk_capital: Optional[float] = Field(default=None, alias="riskCapital")
    mm_cycle_trades: Optional[int] = Field(default=None, alias="mmCycleTrades")
    mm_target_wins: Optional[int] = Field(default=None, alias="mmTargetWins")
    mm_payout: Optional[float] = Field(default=None, alias="mmPayout")
    account_currency: Optional[str] = Field(default=None, alias="accountCurrency")
    contract_strategy: Optional[str] = Field(default=None, alias="contractStrategy")
    duration_ticks: Optional[int] = Field(default=None, alias="durationTicks")

    model_config = ConfigDict(populate_by_name=True)


class WorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    trading_pair: str
    trading_type: str
    status: WorkflowStatus
    starting_time: Optional[datetime] = None
    one_day_minimum_trade: Optional[str] = None
    created_at: Optional[datetime] = None
    deriv_app_id: Optional[str] = Field(default=None, validation_alias="deriv_app_id")
    has_deriv_api_token: bool = False
    last_trade_result: Optional[dict[str, Any]] = Field(
        default=None, validation_alias="last_trade_result"
    )
    risk_capital: float = Field(default=5.0, validation_alias="risk_capital")
    mm_cycle_trades: int = Field(default=10, validation_alias="mm_cycle_trades")
    mm_target_wins: int = Field(default=6, validation_alias="mm_target_wins")
    mm_payout: float = Field(default=1.95, validation_alias="mm_payout")
    account_currency: str = Field(default="USD", validation_alias="account_currency")
    contract_strategy: str = Field(
        default="rise_fall", validation_alias="contract_strategy"
    )
    duration_ticks: int = Field(default=2, validation_alias="duration_ticks")

    @model_validator(mode="before")
    @classmethod
    def from_orm_workflow(cls, data: Any) -> Any:
        if not isinstance(data, dict) and hasattr(data, "deriv_api_token"):
            return {
                "id": data.id,
                "user_id": data.user_id,
                "name": data.name,
                "trading_pair": data.trading_pair,
                "trading_type": data.trading_type,
                "status": data.status,
                "starting_time": data.starting_time,
                "one_day_minimum_trade": data.one_day_minimum_trade,
                "created_at": data.created_at,
                "deriv_app_id": data.deriv_app_id,
                "has_deriv_api_token": bool(data.deriv_api_token),
                "last_trade_result": data.last_trade_result,
                "risk_capital": data.risk_capital if data.risk_capital is not None else 5.0,
                "mm_cycle_trades": data.mm_cycle_trades if data.mm_cycle_trades is not None else 10,
                "mm_target_wins": data.mm_target_wins if data.mm_target_wins is not None else 6,
                "mm_payout": data.mm_payout if data.mm_payout is not None else 1.95,
                "account_currency": data.account_currency or "USD",
                "contract_strategy": data.contract_strategy or "rise_fall",
                "duration_ticks": data.duration_ticks if data.duration_ticks is not None else 2,
            }
        return data
