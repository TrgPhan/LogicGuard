from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.analysis import AnalysisRun, AnalysisType, AnalysisStatus
from app.schemas.analysis import AnalysisRunCreate, AnalysisRunResponse

router = APIRouter()


@router.post("/documents/{document_id}/analyze", response_model=AnalysisRunResponse, status_code=status.HTTP_201_CREATED)
def analyze_document(
    document_id: UUID,
    analysis_data: AnalysisRunCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger analysis on a document"""
    # Verify document belongs to user
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Create analysis run
    analysis_run = AnalysisRun(
        document_id=document_id,
        doc_version=document.version,
        analysis_type=AnalysisType.FULL,
        trigger_source=analysis_data.trigger_source,
        status=AnalysisStatus.QUEUED
    )
    
    db.add(analysis_run)
    db.commit()
    db.refresh(analysis_run)
    
    # TODO: Queue the actual analysis task (e.g., with Celery or background task)
    
    return analysis_run
