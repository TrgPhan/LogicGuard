from pydantic import BaseModel, field_serializer
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class DocumentCreate(BaseModel):
    title: str = "Untitled"
    content_full: str = ""
    goal_id: Optional[UUID] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content_full: Optional[str] = None
    goal_id: Optional[UUID] = None


class DocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    goal_id: Optional[UUID]
    title: str
    content_full: str
    version: int
    word_count: int
    structure_json: Dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    id: UUID
    title: str
    word_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Section schemas
class SectionResponse(BaseModel):
    id: UUID
    document_id: UUID
    section_type: str
    section_label: Optional[str]
    order_index: int
    is_complete: bool

    @field_serializer('section_type')
    def serialize_section_type(self, value):
        # Convert enum to string value if needed
        return value.value if hasattr(value, 'value') else value

    class Config:
        from_attributes = True


class SectionUpdateStatus(BaseModel):
    is_complete: bool


# Paragraph schemas
class ParagraphResponse(BaseModel):
    id: UUID
    document_id: UUID
    section_id: Optional[UUID]
    p_index: int
    text: str
    word_count: int
    emb: Optional[List[float]] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class ParagraphUpdate(BaseModel):
    text: Optional[str] = None
    emb: Optional[List[float]] = None


# Sentence schemas
class SentenceResponse(BaseModel):
    id: UUID
    paragraph_id: UUID
    s_index: int
    text: str
    role: Optional[str]
    confidence_score: Optional[int]

    @field_serializer('role')
    def serialize_role(self, value):
        # Convert enum to string value if needed
        return value.value if hasattr(value, 'value') else value

    class Config:
        from_attributes = True
