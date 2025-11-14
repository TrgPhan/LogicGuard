from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import re
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.goal import Goal, RubricCriterion, WritingType
from app.schemas.goal import GoalCreate, GoalResponse, GoalDetailResponse, GoalUpdate
from app.schemas.goal_preview import (
    GoalPreviewRequest, GoalPreviewResponse, CriterionPreview,
    GoalValidationRequest, GoalValidationResponse
)

router = APIRouter()


def _extract_rubrics_from_text(text: str) -> List[str]:
    """Normalize rubric text into individual chealist items."""
    if not text:
        return []
    items = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Remove bullet/numbering prefixes (e.g., "1.", "-", "•")
        line = re.sub(r"^(?:\d+[\.)]|[-•])\s*", "", line)
        if line:
            items.append(line)
    return items


def _determine_rubrics(rubric_text: Optional[str], selected_rubrics: Optional[List[str]]) -> List[str]:
    if selected_rubrics:
        return [item.strip() for item in selected_rubrics if item.strip()]
    if rubric_text:
        return _extract_rubrics_from_text(rubric_text)
    return []


def _build_rubric_text(rubrics: List[str], fallback_text: Optional[str] = None) -> str:
    if rubrics:
        return "\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(rubrics))
    if fallback_text:
        return fallback_text
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="At least one rubric item is required"
    )


def _build_extracted_payload(rubrics: List[str], writing_type_name: Optional[str]) -> dict:
    return {
        "writing_type": writing_type_name,
        "criteria": [
            {
                "label": label,
                "description": label,
                "weight": 1,
                "order_index": idx,
                "is_mandatory": True,
            }
            for idx, label in enumerate(rubrics)
        ],
        "source": "manual",
    }


def _replace_goal_criteria(db: Session, goal: Goal, rubric_items: List[str]):
    db.query(RubricCriterion).filter(RubricCriterion.goal_id == goal.id).delete()
    for idx, label in enumerate(rubric_items):
        db.add(
            RubricCriterion(
                goal_id=goal.id,
                label=label,
                description=label,
                weight=1,
                order_index=idx,
                is_mandatory=True,
            )
        )


def _resolve_writing_type_name(db: Session, writing_type_id: Optional[UUID], custom_name: Optional[str]) -> Optional[str]:
    if writing_type_id:
        writing_type = db.query(WritingType).filter(WritingType.id == writing_type_id).first()
        if writing_type:
            return writing_type.display_name
    return custom_name


@router.get("/", response_model=List[GoalResponse])
def get_user_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all goals created by the user"""
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id
    ).order_by(Goal.created_at.desc()).all()
    return goals


@router.post("/", response_model=GoalDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_new_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new goal without relying on external LLM services."""
    rubric_items = _determine_rubrics(goal_data.rubric_text, goal_data.selected_rubrics)
    if not rubric_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either rubric_text or selected_rubrics must be provided"
        )

    writing_type_name = _resolve_writing_type_name(db, goal_data.writing_type_id, goal_data.writing_type_custom)
    rubric_text = _build_rubric_text(rubric_items, goal_data.rubric_text)
    extracted_payload = _build_extracted_payload(rubric_items, writing_type_name)

    new_goal = Goal(
        user_id=current_user.id,
        writing_type_id=goal_data.writing_type_id,
        writing_type_custom=goal_data.writing_type_custom,
        rubric_text=rubric_text,
        key_constraints=goal_data.key_constraints,
        extracted_criteria=extracted_payload
    )
    db.add(new_goal)
    db.flush()

    _replace_goal_criteria(db, new_goal, rubric_items)
    db.commit()
    db.refresh(new_goal)
    return new_goal


@router.get("/{goal_id}", response_model=GoalDetailResponse)
def get_goal_detail(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve goal details including extracted criteria and rubric structure
    """
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    return goal


@router.put("/{goal_id}", response_model=GoalDetailResponse)
def update_goal(
    goal_id: UUID,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )

    rubric_text_input = goal_data.rubric_text if goal_data.rubric_text is not None else goal.rubric_text
    rubric_items = _determine_rubrics(rubric_text_input, goal_data.selected_rubrics)
    if not rubric_items:
        rubric_items = _extract_rubrics_from_text(goal.rubric_text)
    rubric_text = _build_rubric_text(rubric_items, rubric_text_input)

    goal.writing_type_id = goal_data.writing_type_id if goal_data.writing_type_id is not None else goal.writing_type_id
    goal.writing_type_custom = (
        goal_data.writing_type_custom if goal_data.writing_type_custom is not None else goal.writing_type_custom
    )
    goal.key_constraints = (
        goal_data.key_constraints if goal_data.key_constraints is not None else goal.key_constraints
    )
    goal.rubric_text = rubric_text

    writing_type_name = _resolve_writing_type_name(db, goal.writing_type_id, goal.writing_type_custom)
    goal.extracted_criteria = _build_extracted_payload(rubric_items, writing_type_name)

    _replace_goal_criteria(db, goal, rubric_items)
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a goal and all linked rubric criteria
    """
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found"
        )
    
    # Delete the goal (cascades to rubric criteria)
    db.delete(goal)
    db.commit()
    return None

@router.post("/preview", response_model=GoalPreviewResponse)
async def preview_goal_extraction(
    request: GoalPreviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview criteria based on manual rubric selections only."""
    rubric_items = _determine_rubrics(request.rubric_text, request.selected_rubrics)
    if not rubric_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either rubric_text or selected_rubrics must be provided"
        )

    writing_type_name = _resolve_writing_type_name(db, request.writing_type_id, request.writing_type_custom)

    criteria_previews = [
        CriterionPreview(
            label=item,
            description=item,
            weight=1.0,
            is_mandatory=True,
            order_index=idx,
        )
        for idx, item in enumerate(rubric_items)
    ]

    mandatory_count = len(criteria_previews)
    optional_count = 0

    return GoalPreviewResponse(
        main_goal=writing_type_name or "Document writing goal",
        criteria=criteria_previews,
        success_indicators=[],
        writing_type=writing_type_name,
        key_constraints=request.key_constraints,
        total_criteria=len(criteria_previews),
        mandatory_count=mandatory_count,
        optional_count=optional_count,
    )


@router.post("/validate", response_model=GoalValidationResponse)
async def validate_criteria(
    request: GoalValidationRequest,
    current_user: User = Depends(get_current_user)
):
    # Simple local validation: ensure each criterion has a label
    invalid_labels = [c for c in request.criteria if not c.get("label")]
    suggestions = []
    if invalid_labels:
        suggestions.append("Provide a label for every criterion.")

    return GoalValidationResponse(
        is_valid=len(invalid_labels) == 0,
        suggestions=suggestions,
        missing_elements=[],
        confidence_score=1.0 if not invalid_labels else 0.6,
    )
