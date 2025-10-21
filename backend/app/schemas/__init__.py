"""
Pydantic schemas package
"""
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse
from app.schemas.goal import GoalCreate, GoalResponse
from app.schemas.error import LogicErrorResponse
from app.schemas.feedback import FeedbackResponse

__all__ = [
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentListResponse",
    "GoalCreate",
    "GoalResponse",
    "LogicErrorResponse",
    "FeedbackResponse",
]
