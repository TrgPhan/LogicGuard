from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid
from app.core.database import Base


class WritingTypeName(str, enum.Enum):
    ESSAY = "essay"
    PROPOSAL = "proposal"
    REPORT = "report"
    PITCH = "pitch"
    BLOG_POST = "blog_post"


class EvidenceQuality(str, enum.Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    MISSING = "missing"


class WritingType(Base):
    __tablename__ = "WRITING_TYPE"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)  # Changed from SQLEnum to String to avoid enum mismatch
    display_name = Column(Text, nullable=False)
    description = Column(Text)
    default_checks = Column(JSONB, nullable=False, server_default='{}')
    structure_template = Column(JSONB, nullable=False, server_default='{}')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    goals = relationship("Goal", back_populates="writing_type")


class Goal(Base):
    __tablename__ = "GOAL"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("USER.id", ondelete="CASCADE"), nullable=False)
    writing_type_id = Column(UUID(as_uuid=True), ForeignKey("WRITING_TYPE.id", ondelete="SET NULL"))
    writing_type_custom = Column(Text)
    rubric_text = Column(Text, nullable=False)
    extracted_criteria = Column(JSONB, nullable=False, server_default='[]')
    key_constraints = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="goals")
    writing_type = relationship("WritingType", back_populates="goals")
    criteria = relationship("RubricCriterion", back_populates="goal", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="goal")


class RubricCriterion(Base):
    __tablename__ = "RUBRIC_CRITERION"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("GOAL.id", ondelete="CASCADE"), nullable=False)
    label = Column(Text, nullable=False)
    description = Column(Text)
    weight = Column(Integer, nullable=False, default=1)
    order_index = Column(Integer, nullable=False, default=0)
    is_mandatory = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        CheckConstraint('weight >= 0 AND weight <= 1', name='weight_check'),
        Index('ix_rubric_criterion_goal_order', 'goal_id', 'order_index', unique=True),
    )

    # Relationships
    goal = relationship("Goal", back_populates="criteria")
    coverage = relationship("CriterionCoverage", back_populates="criterion", cascade="all, delete-orphan")


class CriterionCoverage(Base):
    __tablename__ = "CRITERION_COVERAGE"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("DOCUMENT.id", ondelete="CASCADE"), nullable=False)
    criterion_id = Column(UUID(as_uuid=True), ForeignKey("RUBRIC_CRITERION.id", ondelete="CASCADE"), nullable=False)
    is_addressed = Column(Boolean, nullable=False, default=False)
    confidence_score = Column(Integer, nullable=False, default=0)
    supporting_paragraph_ids = Column(JSONB, nullable=False, server_default='[]')
    supporting_sentence_ids = Column(JSONB, nullable=False, server_default='[]')
    evidence_quality = Column(SQLEnum(EvidenceQuality, name="EVIDENCE_QUALITY"), nullable=False, default=EvidenceQuality.MISSING)
    last_checked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_coverage_doc_criterion', 'document_id', 'criterion_id', unique=True),
    )

    # Relationships
    criterion = relationship("RubricCriterion", back_populates="coverage")
