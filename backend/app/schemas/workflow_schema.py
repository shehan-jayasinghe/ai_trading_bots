from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.workflow_status import WorkflowStatus


class WorkflowCreate(BaseModel):
    name: str
    trading_pair: str
    trading_type: str
    starting_time: datetime
    one_day_minimum_trade: str


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    trading_pair: Optional[str] = None
    trading_type: Optional[str] = None
    starting_time: Optional[datetime] = None
    one_day_minimum_trade: Optional[str] = None


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
