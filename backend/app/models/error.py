from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid
from app.core.database import Base


class ErrorType(str, enum.Enum):
    UNCLEAR_TERM = "unclear_term"
    UNDEFINED_TECHNICAL_TERM = "undefined_technical_term"
    AMBIGUOUS_REFERENCE = "ambiguous_reference"
    VAGUE_LANGUAGE = "vague_language"
    CONTRADICTION = "contradiction"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    LOGIC_GAP = "logic_gap"
    OFF_TOPIC = "off_topic"
    MISSING_RUBRIC_ELEMENT = "missing_rubric_element"
    WEAK_EVIDENCE = "weak_evidence"


class ErrorCategory(str, enum.Enum):
    CLARITY = "clarity"
    LOGIC = "logic"
    STRUCTURE = "structure"
    GOAL_ALIGNMENT = "goal_alignment"


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    MEDIUM = "medium"
    MINOR = "minor"


class LogicError(Base):
    __tablename__ = "LOGIC_ERROR"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_run_id = Column(UUID(as_uuid=True), ForeignKey("ANALYSIS_RUN.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("DOCUMENT.id", ondelete="CASCADE"), nullable=False)
    paragraph_id = Column(UUID(as_uuid=True), ForeignKey("PARAGRAPH.id", ondelete="SET NULL"))
    sentence_id = Column(UUID(as_uuid=True), ForeignKey("SENTENCE.id", ondelete="SET NULL"))
    error_type = Column(SQLEnum(ErrorType, name="ERROR_TYPE"), nullable=False)
    error_category = Column(SQLEnum(ErrorCategory, name="ERROR_CATEGORY"), nullable=False)
    severity = Column(SQLEnum(Severity, name="SEVERITY"), nullable=False, default=Severity.MEDIUM)
    message = Column(Text, nullable=False)
    meta = Column(JSONB, nullable=False, server_default='{}')
    p_index = Column(Integer)
    s_index = Column(Integer)
    is_resolved = Column(Boolean, nullable=False, default=False)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by_doc_version = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_error_doc_resolved', 'document_id', 'is_resolved', 'created_at'),
        Index('ix_error_run_type', 'analysis_run_id', 'error_type'),
    )

    # Relationships
    analysis_run = relationship("AnalysisRun", back_populates="logic_errors")
    document = relationship("Document", back_populates="logic_errors")
    paragraph = relationship("Paragraph", back_populates="logic_errors")
    sentence = relationship("Sentence", back_populates="logic_errors")
    feedback = relationship("Feedback", back_populates="logic_error", cascade="all, delete-orphan")
