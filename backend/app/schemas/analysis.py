from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.schemas.error import LogicErrorResponse


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
    stats: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisResultResponse(BaseModel):
    analysis_run: AnalysisRunResponse
    errors: List[LogicErrorResponse]
    total_issues: int
