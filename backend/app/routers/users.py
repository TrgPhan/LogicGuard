from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash, verify_password
from app.models.user import User
from app.models.document import Document
from app.models.error import LogicError
from app.models.feedback import UserErrorPattern
from app.models.analysis import WritingSession
from app.schemas.user import UserResponse
from app.schemas.user_extended import UserUpdate, UserProfileResponse, ErrorPatternResponse

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get authenticated user's profile and usage statistics.
    
    Returns:
    - User profile information
    - Total documents created
    - Total words written
    - Total errors found and fixed
    - Active writing time
    """
    # Get document statistics
    total_documents = db.query(func.count(Document.id)).filter(
        Document.user_id == current_user.id
    ).scalar() or 0
    
    total_words = db.query(func.sum(Document.word_count)).filter(
        Document.user_id == current_user.id
    ).scalar() or 0
    
    # Get error statistics from writing sessions
    error_stats = db.query(
        func.sum(WritingSession.errors_introduced).label('errors_found'),
        func.sum(WritingSession.errors_fixed).label('errors_fixed'),
        func.sum(WritingSession.active_time_seconds).label('active_time')
    ).filter(
        WritingSession.user_id == current_user.id
    ).first()
    
    errors_found = error_stats.errors_found if error_stats and error_stats.errors_found else 0
    errors_fixed = error_stats.errors_fixed if error_stats and error_stats.errors_fixed else 0
    active_time_seconds = error_stats.active_time if error_stats and error_stats.active_time else 0
    
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        created_at=current_user.created_at.isoformat(),
        total_documents=total_documents,
        total_words_written=total_words,
        total_errors_found=errors_found,
        total_errors_fixed=errors_fixed,
        active_writing_time_minutes=active_time_seconds // 60
    )


@router.put("/update", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile (email and/or password).
    
    - **email**: New email address (optional)
    - **password**: New password (optional, min 6 characters)
    - **current_password**: Current password (required when changing password)
    
    Returns updated user information.
    """
    # If no updates provided
    if not user_update.email and not user_update.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )
    
    # Update email
    if user_update.email and user_update.email != current_user.email:
        # Check if email already exists
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        
        current_user.email = user_update.email
    
    # Update password
    if user_update.password:
        # Verify current password
        if not user_update.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is required to change password"
            )
        
        if not verify_password(user_update.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Update to new password
        current_user.password_hash = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)


@router.get("/error-patterns", response_model=List[ErrorPatternResponse])
def get_user_error_patterns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch user's recurring error patterns and statistics.
    
    Returns a list of error types the user frequently makes, including:
    - Error type
    - Frequency (how many times it occurred)
    - Last occurrence timestamp
    - Average time to fix (in seconds and minutes)
    
    Useful for personalized feedback and learning insights.
    """
    error_patterns = db.query(UserErrorPattern).filter(
        UserErrorPattern.user_id == current_user.id
    ).order_by(UserErrorPattern.frequency.desc()).all()
    
    # Format response with additional computed fields
    results = []
    for pattern in error_patterns:
        pattern_data = ErrorPatternResponse(
            error_type=pattern.error_type,
            frequency=pattern.frequency,
            last_occurred_at=pattern.last_occurred_at.isoformat(),
            avg_time_to_fix_seconds=pattern.avg_time_to_fix_seconds,
            avg_time_to_fix_minutes=pattern.avg_time_to_fix_seconds // 60 if pattern.avg_time_to_fix_seconds else None
        )
        results.append(pattern_data)
    
    return results


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account permanently.
    
    ⚠️ WARNING: This action is irreversible!
    All user data including documents, goals, and analysis will be deleted.
    """
    db.delete(current_user)
    db.commit()
    return None
