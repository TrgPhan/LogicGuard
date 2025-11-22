from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class LogicErrorResponse(BaseModel):
    id: UUID
    error_type: str
    error_category: str
    severity: str
    message: str
    meta: Optional[Dict[str, Any]] = None
    p_index: Optional[int] = None
    s_index: Optional[int] = None
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True
