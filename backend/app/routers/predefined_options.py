"""
Predefined Options Router
Provides predefined writing types, rubrics, and constraints for frontend UI
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/writing-types", response_model=List[Dict[str, Any]])
async def get_predefined_writing_types():
    """
    Get predefined writing type options with default rubrics and constraints
    
    Returns:
        List of writing type configurations for frontend UI
    """
    return [
        {
            "id": "academic_essay",
            "name": "Academic Essay",
            "description": "Structured academic writing with thesis and evidence",
            "default_rubrics": [
                "Clear thesis statement",
                "Logical argument flow",
                "Evidence-based support",
                "Proper citations",
                "Coherent conclusions"
            ],
            "default_constraints": [
                "Avoid passive voice",
                "Maintain formal tone",
                "Check for redundancy",
                "Verify paragraph transitions",
                "Ensure consistent terminology"
            ]
        },
        {
            "id": "research_paper",
            "name": "Research Paper",
            "description": "In-depth research with methodology and findings",
            "default_rubrics": [
                "Clear research question",
                "Comprehensive literature review",
                "Sound methodology",
                "Valid data analysis",
                "Meaningful conclusions"
            ],
            "default_constraints": [
                "Use academic language",
                "Cite all sources properly",
                "Follow format guidelines",
                "Maintain objectivity",
                "Support claims with evidence"
            ]
        },
        {
            "id": "business_proposal",
            "name": "Business Proposal",
            "description": "Professional business proposal with problem-solution structure",
            "default_rubrics": [
                "Clear problem statement",
                "Feasible solution",
                "Cost-benefit analysis",
                "Implementation timeline",
                "Risk assessment"
            ],
            "default_constraints": [
                "Use professional language",
                "Include supporting data",
                "Address stakeholder concerns",
                "Provide clear recommendations",
                "Follow business format"
            ]
        },
        {
            "id": "creative_writing",
            "name": "Creative Writing",
            "description": "Creative narrative with engaging storytelling",
            "default_rubrics": [
                "Engaging narrative voice",
                "Strong character development",
                "Vivid descriptions",
                "Compelling plot structure",
                "Emotional resonance"
            ],
            "default_constraints": [
                "Show, don't tell",
                "Maintain consistent point of view",
                "Use active voice",
                "Create sensory details",
                "Develop authentic dialogue"
            ]
        }
    ]


@router.get("/rubric-templates/{writing_type_id}", response_model=Dict[str, Any])
async def get_rubric_template(writing_type_id: str):
    """
    Get detailed rubric template for a specific writing type
    
    Args:
        writing_type_id: ID of the writing type (e.g., 'academic_essay')
    
    Returns:
        Detailed rubric template with descriptions and weights
    """
    writing_types = await get_predefined_writing_types()
    
    for wt in writing_types:
        if wt["id"] == writing_type_id:
            return {
                "writing_type": wt["name"],
                "description": wt["description"],
                "rubric_items": [
                    {
                        "label": rubric,
                        "description": f"Evaluate {rubric.lower()}",
                        "weight": 1.0 / len(wt["default_rubrics"]),
                        "is_mandatory": True
                    }
                    for rubric in wt["default_rubrics"]
                ],
                "constraint_items": [
                    {
                        "label": constraint,
                        "description": f"Check for: {constraint.lower()}",
                        "is_required": True
                    }
                    for constraint in wt["default_constraints"]
                ]
            }
    
    raise HTTPException(status_code=404, detail=f"Writing type '{writing_type_id}' not found")
