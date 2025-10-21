from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class LogicErrorResponse(BaseModel):
    id: UUID
    error_type: str
    error_category: str
    severity: str
    message: str
    p_index: Optional[int]
    s_index: Optional[int]
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True
