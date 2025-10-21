from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class GoalCreate(BaseModel):
    writing_type_custom: Optional[str] = None
    rubric_text: str
    key_constraints: Optional[str] = None


class GoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    writing_type_custom: Optional[str]
    rubric_text: str
    extracted_criteria: dict
    key_constraints: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RubricCriterionResponse(BaseModel):
    id: UUID
    goal_id: UUID
    label: str
    description: Optional[str]
    weight: float
    order_index: int
    is_mandatory: bool

    class Config:
        from_attributes = True


class GoalDetailResponse(BaseModel):
    id: UUID
    user_id: UUID
    writing_type_custom: Optional[str]
    rubric_text: str
    extracted_criteria: dict
    key_constraints: Optional[str]
    created_at: datetime
    criteria: List[RubricCriterionResponse] = []

    class Config:
        from_attributes = True
