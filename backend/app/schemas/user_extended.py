from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    current_password: Optional[str] = None  # Required when changing password


class UserProfileResponse(BaseModel):
    """Extended user profile with statistics"""
    id: str
    email: str
    created_at: str
    total_documents: int = 0
    total_words_written: int = 0
    total_errors_found: int = 0
    total_errors_fixed: int = 0
    active_writing_time_minutes: int = 0


class ErrorPatternResponse(BaseModel):
    """User's recurring error pattern"""
    error_type: str
    frequency: int
    last_occurred_at: str
    avg_time_to_fix_seconds: Optional[int] = None
    avg_time_to_fix_minutes: Optional[int] = None
    
    class Config:
        from_attributes = True
