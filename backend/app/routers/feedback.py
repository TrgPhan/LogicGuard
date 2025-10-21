from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.error import LogicError
from app.models.feedback import Feedback
from app.schemas.error import LogicErrorResponse
from app.schemas.feedback import FeedbackResponse

router = APIRouter()


@router.get("/documents/{document_id}/errors", response_model=List[LogicErrorResponse])
def get_document_errors(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all logic errors for a document"""
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
    
    errors = db.query(LogicError).filter(
        LogicError.document_id == document_id,
        LogicError.is_resolved == False
    ).all()
    
    return errors


@router.get("/errors/{error_id}/feedback", response_model=List[FeedbackResponse])
def get_error_feedback(
    error_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback for a specific error"""
    error = db.query(LogicError).filter(LogicError.id == error_id).first()
    
    if not error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error not found"
        )
    
    # Verify the error belongs to a document owned by the user
    document = db.query(Document).filter(
        Document.id == error.document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    feedback = db.query(Feedback).filter(Feedback.logic_error_id == error_id).all()
    return feedback
