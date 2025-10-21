from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.goal import Goal, RubricCriterion
from app.schemas.goal import GoalCreate, GoalResponse, GoalDetailResponse
from app.utils.nlp import extract_criteria_from_rubric

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
def create_new_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new goal with rubric text and key constraints.
    Automatically extracts criteria using NLP.
    """
    # Extract criteria from rubric text using NLP
    extracted_criteria = extract_criteria_from_rubric(goal_data.rubric_text)
    
    # Create the goal
    new_goal = Goal(
        user_id=current_user.id,
        writing_type_custom=goal_data.writing_type_custom,
        rubric_text=goal_data.rubric_text,
        key_constraints=goal_data.key_constraints,
        extracted_criteria=extracted_criteria
    )
    db.add(new_goal)
    db.flush()  # Get the goal ID without committing
    
    # Create rubric criteria entries
    for idx, criterion in enumerate(extracted_criteria.get("criteria", [])):
        rubric_criterion = RubricCriterion(
            goal_id=new_goal.id,
            label=criterion.get("label", f"Criterion {idx + 1}"),
            description=criterion.get("description", ""),
            weight=criterion.get("weight", 1.0),
            order_index=idx,
            is_mandatory=criterion.get("is_mandatory", True)
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
