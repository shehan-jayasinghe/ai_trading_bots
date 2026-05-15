from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: Optional[str] = None
    name: Optional[str] = None