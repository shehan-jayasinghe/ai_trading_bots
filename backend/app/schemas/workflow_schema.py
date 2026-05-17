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

    model_config = ConfigDict(populate_by_name=True)


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    trading_pair: Optional[str] = None
    trading_type: Optional[str] = None
    starting_time: Optional[datetime] = None
    one_day_minimum_trade: Optional[str] = None
    deriv_app_id: Optional[str] = Field(default=None, alias="derivAppId")
    deriv_api_token: Optional[str] = Field(default=None, alias="derivApiToken")

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
            }
        return data
