from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class BaseResponse(BaseModel):
    success: bool = True
    message: str = "Success"


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None


class IDMixin(BaseModel):
    id: int