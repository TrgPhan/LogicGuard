from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.models.goal import WritingType
from app.schemas.writing_types import WritingTypeResponse, WritingTypeDetailResponse

router = APIRouter()


@router.get("/", response_model=List[WritingTypeResponse])
def list_writing_types(db: Session = Depends(get_db)):
    """
    Fetch available writing templates (Essay, Proposal, Report, etc.)
    """
    writing_types = db.query(WritingType).all()
    
    # If no writing types exist, return default templates
    if not writing_types:
        from uuid import UUID as _UUID
        return [
            WritingTypeResponse(
                id=_UUID("00000000-0000-0000-0000-000000000001"),
                name="essay",
                display_name="Essay",
                description="Academic or personal essay with introduction, body paragraphs, and conclusion",
                default_checks={
                    "check_thesis": True,
                    "check_evidence": True,
                    "check_transitions": True
                },
                structure_template={
                    "sections": ["introduction", "body", "conclusion"],
                    "min_paragraphs": 5
                }
            ),
            WritingTypeResponse(
                id=_UUID("00000000-0000-0000-0000-000000000002"),
                name="proposal",
                display_name="Proposal",
                description="Project or business proposal document",
                default_checks={
                    "check_problem_statement": True,
                    "check_solution": True,
                    "check_budget": True
                },
                structure_template={
                    "sections": ["executive_summary", "problem", "solution", "timeline", "budget"],
                    "min_paragraphs": 8
                }
            ),
            WritingTypeResponse(
                id=_UUID("00000000-0000-0000-0000-000000000003"),
                name="report",
                display_name="Report",
                description="Formal report with findings and analysis",
                default_checks={
                    "check_data": True,
                    "check_analysis": True,
                    "check_recommendations": True
                },
                structure_template={
                    "sections": ["abstract", "introduction", "methodology", "findings", "conclusion"],
                    "min_paragraphs": 10
                }
            ),
            WritingTypeResponse(
                id=_UUID("00000000-0000-0000-0000-000000000004"),
                name="pitch",
                display_name="Pitch",
                description="Business pitch or elevator pitch",
                default_checks={
                    "check_hook": True,
                    "check_value_proposition": True,
                    "check_call_to_action": True
                },
                structure_template={
                    "sections": ["hook", "problem", "solution", "market", "ask"],
                    "min_paragraphs": 5
                }
            ),
            WritingTypeResponse(
                id=_UUID("00000000-0000-0000-0000-000000000005"),
                name="blog_post",
                display_name="Blog Post",
                description="Blog article or content piece",
                default_checks={
                    "check_headline": True,
                    "check_readability": True,
                    "check_cta": True
                },
                structure_template={
                    "sections": ["introduction", "body", "conclusion"],
                    "min_paragraphs": 4
                }
            )
        ]
    
    return writing_types


@router.get("/{writing_type_id}", response_model=WritingTypeDetailResponse)
def get_writing_type_detail(
    writing_type_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve section templates and default checks for a specific writing type
    """
    writing_type = db.query(WritingType).filter(
        WritingType.id == writing_type_id
    ).first()
    
    if not writing_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Writing type not found"
        )
    
    return writing_type
