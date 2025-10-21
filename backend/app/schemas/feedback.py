from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class FeedbackResponse(BaseModel):
    id: UUID
    suggestion: str
    explanation: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
