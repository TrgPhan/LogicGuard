from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class AnalysisRunCreate(BaseModel):
    trigger_source: str = "manual"


class AnalysisRunResponse(BaseModel):
    id: UUID
    document_id: UUID
    doc_version: int
    analysis_type: str
    trigger_source: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
