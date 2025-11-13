from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CriterionPreview(BaseModel):
    """Preview of a single criterion before creation"""
    label: str
    description: str
    weight: float = Field(ge=0.0, le=1.0)
    is_mandatory: bool
    order_index: int


class GoalPreviewRequest(BaseModel):
    """Request to preview goal extraction"""
    rubric_text: Optional[str] = Field(None, min_length=1)
    selected_rubrics: Optional[List[str]] = None  # Selected rubric checkboxes from UI
    writing_type_id: Optional[str] = None
    writing_type_custom: Optional[str] = None
    key_constraints: Optional[List[str]] = None  # List of constraint strings


class GoalPreviewResponse(BaseModel):
    """Response with extracted criteria preview"""
    main_goal: str
    criteria: List[CriterionPreview]
    success_indicators: List[str]
    writing_type: Optional[str] = None
    key_constraints: Optional[List[str]] = None  # List of constraint strings
    
    # Metadata
    total_criteria: int
    mandatory_count: int
    optional_count: int


class GoalValidationRequest(BaseModel):
    """Request to validate extracted criteria"""
    criteria: List[Dict[str, Any]]
    writing_type: str


class GoalValidationResponse(BaseModel):
    """Response with validation results"""
    is_valid: bool
    suggestions: List[str]
    missing_elements: List[str]
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
