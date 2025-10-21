from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, REAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid
from app.core.database import Base


class SectionType(str, enum.Enum):
    INTRO = "intro"
    BODY = "body"
    CONCLUSION = "conclusion"
    CUSTOM = "custom"


class SentenceRole(str, enum.Enum):
    CLAIM = "claim"
    EVIDENCE = "evidence"
    NEUTRAL = "neutral"
    DEFINITION = "definition"
    TRANSITION = "transition"


class Document(Base):
    __tablename__ = "DOCUMENT"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("USER.id", ondelete="CASCADE"), nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("GOAL.id", ondelete="SET NULL"))
    title = Column(Text, nullable=False, default='Untitled')
    content_full = Column(Text, nullable=False, default='')
    structure_json = Column(JSONB, nullable=False, server_default='{}')
    version = Column(Integer, nullable=False, default=1)
    word_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_document_user_updated', 'user_id', 'updated_at'),
    )

    # Relationships
    user = relationship("User", back_populates="documents")
    goal = relationship("Goal", back_populates="documents")
    sections = relationship("DocumentSection", back_populates="document", cascade="all, delete-orphan")
    paragraphs = relationship("Paragraph", back_populates="document", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="document", cascade="all, delete-orphan")
    logic_errors = relationship("LogicError", back_populates="document", cascade="all, delete-orphan")
    writing_sessions = relationship("WritingSession", back_populates="document", cascade="all, delete-orphan")


class DocumentSection(Base):
    __tablename__ = "DOCUMENT_SECTION"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("DOCUMENT.id", ondelete="CASCADE"), nullable=False)
    section_type = Column(Text, nullable=False)  # Changed from SQLEnum to String to avoid enum mismatch
    section_label = Column(Text)
    is_complete = Column(Boolean, nullable=False, default=False)
    order_index = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index('ix_doc_section_order', 'document_id', 'order_index', unique=True),
    )

    # Relationships
    document = relationship("Document", back_populates="sections")
    paragraphs = relationship("Paragraph", back_populates="section")


class Paragraph(Base):
    __tablename__ = "PARAGRAPH"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("DOCUMENT.id", ondelete="CASCADE"), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("DOCUMENT_SECTION.id", ondelete="SET NULL"))
    p_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False, default='')
    hash = Column(Text, nullable=False)
    emb = Column(ARRAY(REAL))  # pgvector compatible
    word_count = Column(Integer, nullable=False, default=0)
    last_analyzed_version = Column(Integer)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_paragraph_doc_index', 'document_id', 'p_index', unique=True),
        Index('ix_paragraph_hash', 'hash'),
    )

    # Relationships
    document = relationship("Document", back_populates="paragraphs")
    section = relationship("DocumentSection", back_populates="paragraphs")
    sentences = relationship("Sentence", back_populates="paragraph", cascade="all, delete-orphan")
    logic_errors = relationship("LogicError", back_populates="paragraph")


class Sentence(Base):
    __tablename__ = "SENTENCE"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paragraph_id = Column(UUID(as_uuid=True), ForeignKey("PARAGRAPH.id", ondelete="CASCADE"), nullable=False)
    s_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False, default='')
    hash = Column(Text, nullable=False)
    role = Column(Text)  # Changed from SQLEnum to Text to avoid enum mismatch
    emb = Column(ARRAY(REAL))  # pgvector compatible
    confidence_score = Column(Integer)

    __table_args__ = (
        Index('ix_sentence_para_index', 'paragraph_id', 's_index', unique=True),
        Index('ix_sentence_hash', 'hash'),
    )

    # Relationships
    paragraph = relationship("Paragraph", back_populates="sentences")
    logic_errors = relationship("LogicError", back_populates="sentence")
