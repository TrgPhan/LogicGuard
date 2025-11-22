from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid
from app.core.database import Base
from app.utils.enum_types import EnumValueType


class AnalysisType(str, enum.Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    GOAL_ALIGNMENT = "goal_alignment"


class AnalysisStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisRun(Base):
    __tablename__ = "ANALYSIS_RUN"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("DOCUMENT.id", ondelete="CASCADE"), nullable=False)
    doc_version = Column(Integer, nullable=False)
    # Use custom EnumValueType to ensure enum values (not names) are stored in database
    analysis_type = Column(EnumValueType(AnalysisType), nullable=False, default=AnalysisType.INCREMENTAL.value)
    trigger_source = Column(Text, nullable=False)
    paragraphs_analyzed = Column(JSONB, nullable=False, server_default='[]')
    status = Column(EnumValueType(AnalysisStatus), nullable=False, default=AnalysisStatus.QUEUED.value)
    stats = Column(JSONB, nullable=False, server_default='{}')
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index('ix_analysis_doc_created', 'document_id', 'created_at'),
        Index('ix_analysis_doc_version', 'document_id', 'doc_version'),
    )

    # Relationships
    document = relationship("Document", back_populates="analysis_runs")
    logic_errors = relationship("LogicError", back_populates="analysis_run", cascade="all, delete-orphan")


class WritingSession(Base):
    __tablename__ = "WRITING_SESSION"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("DOCUMENT.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("USER.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True))
    words_added = Column(Integer, nullable=False, default=0)
    words_deleted = Column(Integer, nullable=False, default=0)
    paragraphs_added = Column(Integer, nullable=False, default=0)
    errors_introduced = Column(Integer, nullable=False, default=0)
    errors_fixed = Column(Integer, nullable=False, default=0)
    active_time_seconds = Column(Integer, nullable=False, default=0)
    analysis_runs_triggered = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index('ix_session_user_started', 'user_id', 'started_at'),
        Index('ix_session_doc_started', 'document_id', 'started_at'),
    )

    # Relationships
    document = relationship("Document", back_populates="writing_sessions")
    user = relationship("User", back_populates="writing_sessions")
