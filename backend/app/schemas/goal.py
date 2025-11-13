from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class GoalCreate(BaseModel):
    writing_type_id: Optional[UUID] = None  # Reference to predefined writing type
    writing_type_custom: Optional[str] = None  # Custom writing type name
    rubric_text: Optional[str] = Field(None, min_length=1, description="The rubric text to extract criteria from")
    selected_rubrics: Optional[List[str]] = None  # Selected rubric checkboxes from UI
    key_constraints: Optional[List[str]] = None  # List of constraint strings
    
    class Config:
        # Custom validation to ensure either rubric_text or selected_rubrics is provided
        @staticmethod
        def validate_rubric_input(values):
            rubric_text = values.get('rubric_text')
            selected_rubrics = values.get('selected_rubrics')
            if not rubric_text and not selected_rubrics:
                raise ValueError('Either rubric_text or selected_rubrics must be provided')
            return values


class GoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    writing_type_id: Optional[UUID] = None
    writing_type_custom: Optional[str]
    rubric_text: str
    extracted_criteria: dict  # JSONB field - stores auto-extracted criteria
    key_constraints: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class GoalUpdate(BaseModel):
    writing_type_id: Optional[UUID] = None
    writing_type_custom: Optional[str] = None
    rubric_text: Optional[str] = Field(None, min_length=1)
    selected_rubrics: Optional[List[str]] = None
    key_constraints: Optional[List[str]] = None


class RubricCriterionResponse(BaseModel):
    id: UUID
    goal_id: UUID
    label: str
    description: Optional[str]
    weight: float  # 0.0 to 1.0
    order_index: int
    is_mandatory: bool

    class Config:
        from_attributes = True


class RubricCriterionCreate(BaseModel):
    label: str = Field(..., min_length=1)
    description: Optional[str] = None
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Weight must be between 0 and 1")
    order_index: int = Field(default=0, ge=0)
    is_mandatory: bool = True


class RubricCriterionUpdate(BaseModel):
    label: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    order_index: Optional[int] = Field(None, ge=0)
    is_mandatory: Optional[bool] = None


class GoalDetailResponse(BaseModel):
    id: UUID
    user_id: UUID
    writing_type_id: Optional[UUID] = None
    writing_type_custom: Optional[str]
    rubric_text: str
    extracted_criteria: dict
    key_constraints: Optional[List[str]]
    created_at: datetime
    criteria: List[RubricCriterionResponse] = []

    class Config:
        from_attributes = True


# Additional schemas for criterion coverage tracking
class CriterionCoverageResponse(BaseModel):
    id: UUID
    document_id: UUID
    criterion_id: UUID
    is_addressed: bool
    confidence_score: float  # 0.0 to 1.0
    supporting_paragraph_ids: list  # JSONB list of paragraph UUIDs
    supporting_sentence_ids: list   # JSONB list of sentence UUIDs
    evidence_quality: str  # 'strong', 'moderate', 'weak', 'missing'
    last_checked_at: datetime

    class Config:
        from_attributes = True


class CriterionCoverageDetail(BaseModel):
    criterion: RubricCriterionResponse
    coverage: CriterionCoverageResponse

    class Config:
        from_attributes = True
