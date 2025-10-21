from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid
from app.core.database import Base


class UserAction(str, enum.Enum):
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    IGNORED = "ignored"
    APPLIED = "applied"


class Feedback(Base):
    __tablename__ = "FEEDBACK"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    logic_error_id = Column(UUID(as_uuid=True), ForeignKey("LOGIC_ERROR.id", ondelete="CASCADE"), nullable=False)
    suggestion = Column(Text, nullable=False)
    explanation = Column(Text)
    meta = Column(JSONB, nullable=False, server_default='{}')
    user_action = Column(SQLEnum(UserAction, name="USER_ACTION"))
    user_action_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    logic_error = relationship("LogicError", back_populates="feedback")


class UserErrorPattern(Base):
    __tablename__ = "USER_ERROR_PATTERN"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("USER.id", ondelete="CASCADE"), nullable=False)
    error_type = Column(Text, nullable=False)  # Using Text instead of Enum to avoid circular import
    frequency = Column(Integer, nullable=False, default=1)
    last_occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    avg_time_to_fix_seconds = Column(Integer)

    __table_args__ = (
        Index('ix_user_error_pattern', 'user_id', 'error_type', unique=True),
    )

    # Relationships
    user = relationship("User", back_populates="error_patterns")
