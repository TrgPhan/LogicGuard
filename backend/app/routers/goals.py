from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.goal import Goal, RubricCriterion, WritingType
from app.schemas.goal import GoalCreate, GoalResponse, GoalDetailResponse
from app.schemas.goal_preview import (
    GoalPreviewRequest, GoalPreviewResponse, CriterionPreview,
    GoalValidationRequest, GoalValidationResponse
)
from app.services.llm_service import llm_service

router = APIRouter()


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
    """
    Create a new goal with rubric text and key constraints.
    Automatically extracts criteria using LLM (Gemini).
    """
    # Get writing type context if provided
    writing_type_name = None
    if goal_data.writing_type_id:
        writing_type = db.query(WritingType).filter(
            WritingType.id == goal_data.writing_type_id
        ).first()
        if writing_type:
            writing_type_name = writing_type.display_name
    elif goal_data.writing_type_custom:
        writing_type_name = goal_data.writing_type_custom
    
    # Extract criteria from rubric text using LLM
    llm_result = await llm_service.extract_criteria_from_rubric(
        rubric_text=goal_data.rubric_text,
        writing_type=writing_type_name,
        key_constraints=goal_data.key_constraints
    )
    
    # Create the goal
    new_goal = Goal(
        user_id=current_user.id,
        writing_type_id=goal_data.writing_type_id,
        writing_type_custom=goal_data.writing_type_custom,
        rubric_text=goal_data.rubric_text,
        key_constraints=goal_data.key_constraints,
        extracted_criteria=llm_result  # Store full LLM result
    )
    db.add(new_goal)
    db.flush()  # Get the goal ID without committing
    
    # Create rubric criteria entries from LLM extraction
    for criterion_data in llm_result.get("criteria", []):
        rubric_criterion = RubricCriterion(
            goal_id=new_goal.id,
            label=criterion_data.get("label", "Unnamed criterion"),
            description=criterion_data.get("description", ""),
            weight=float(criterion_data.get("weight", 1.0)),
            order_index=int(criterion_data.get("order_index", 0)),
            is_mandatory=bool(criterion_data.get("is_mandatory", True))
        )
        db.add(rubric_criterion)
    
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
    """
    Preview criteria extraction from rubric text WITHOUT saving to database.
    
    This allows users to:
    1. See what criteria will be extracted
    2. Review weights and mandatory flags
    3. Adjust rubric text before final creation
    
    Perfect for Task 1: Context Setup - validating Goal Objects
    """
    # Get writing type context
    writing_type_name = None
    if request.writing_type_id:
        writing_type = db.query(WritingType).filter(
            WritingType.id == request.writing_type_id
        ).first()
        if writing_type:
            writing_type_name = writing_type.display_name
    elif request.writing_type_custom:
        writing_type_name = request.writing_type_custom
    
    # Extract criteria using LLM
    llm_result = await llm_service.extract_criteria_from_rubric(
        rubric_text=request.rubric_text,
        writing_type=writing_type_name,
        key_constraints=request.key_constraints
    )
    
    # Convert to preview format
    criteria_previews = [
        CriterionPreview(
            label=c.get("label", "Unnamed"),
            description=c.get("description", ""),
            weight=float(c.get("weight", 1.0)),
            is_mandatory=bool(c.get("is_mandatory", True)),
            order_index=int(c.get("order_index", idx))
        )
        for idx, c in enumerate(llm_result.get("criteria", []))
    ]
    
    # Calculate stats
    mandatory_count = sum(1 for c in criteria_previews if c.is_mandatory)
    optional_count = len(criteria_previews) - mandatory_count
    
    return GoalPreviewResponse(
        main_goal=llm_result.get("main_goal", "Document writing goal"),
        criteria=criteria_previews,
        success_indicators=llm_result.get("success_indicators", []),
        writing_type=writing_type_name,
        key_constraints=request.key_constraints,
        total_criteria=len(criteria_previews),
        mandatory_count=mandatory_count,
        optional_count=optional_count
    )


@router.post("/validate", response_model=GoalValidationResponse)
async def validate_criteria(
    request: GoalValidationRequest,
    current_user: User = Depends(get_current_user)
):
    # Validate with LLM
    validation_result = await llm_service.validate_criteria_alignment(
        criteria=request.criteria,
        writing_type=request.writing_type
    )
    
    # Calculate confidence score based on validation
    is_valid = validation_result.get("is_valid", True)
    suggestions_count = len(validation_result.get("suggestions", []))
    missing_count = len(validation_result.get("missing_elements", []))
    
    # Simple confidence calculation
    # Start with 1.0, reduce based on issues
    confidence = 1.0
    if not is_valid:
        confidence -= 0.3
    confidence -= min(0.4, suggestions_count * 0.1)  # Max -0.4 for suggestions
    confidence -= min(0.3, missing_count * 0.05)     # Max -0.3 for missing elements
    confidence = max(0.0, confidence)  # Ensure >= 0
    
    return GoalValidationResponse(
        is_valid=is_valid,
        suggestions=validation_result.get("suggestions", []),
        missing_elements=validation_result.get("missing_elements", []),
        confidence_score=round(confidence, 2)
    )
