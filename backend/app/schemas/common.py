from pydantic import BaseModel
from typing import Optional, Any, List, Dict, Union


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Union[str, List[str], Dict[str, Any]]] = None


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 10
    order_by: Optional[str] = None
    order_desc: bool = False


class HealthCheck(BaseModel):
    status: str = "ok"
    version: str
    database_status: str