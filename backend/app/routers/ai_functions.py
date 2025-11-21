# app/routers/ai_functions.py

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_user
from app.models.user import User
from app.services.ai_analysis_service import ai_analysis_service

router = APIRouter(
    prefix="/ai",
    tags=["AI Functions"],
)


class UnifiedAnalysisRequest(BaseModel):
    """
    Request body cho AI Function unified analysis.
    - content: văn bản cần phân tích
    - context: có thể là string (mục tiêu) hoặc dict (writing_type, main_goal, criteria,...)
    - language: 'en' | 'vi' | None (None thì auto detect)
    - mode: flag 'fast' | 'quality' (hiện tại chỉ log, không đổi model)
    """
    content: str
    context: Optional[Any] = None
    language: Optional[str] = None
    mode: str = "fast"


class UnifiedAnalysisResponse(BaseModel):
    """
    Response chuẩn cho FE dùng làm AI Function result.
    - analysis: toàn bộ object trả về từ app.ai.models.Analysis.analyze_document
    """
    success: bool
    content: str
    context: Any
    analysis: Dict[str, Any]


@router.post(
    "/unified-analysis",
    response_model=UnifiedAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def run_unified_analysis(
    payload: UnifiedAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Unified AI Function endpoint:
    - Dùng Gemini 2.5 (model cấu hình trong .env)
    - Chạy 5 subtasks trong một lần:
        1) contradictions
        2) undefined_terms
        3) unsupported_claims
        4) logical_jumps
        5) spelling_errors
    """
    # Gọi service
    result = await ai_analysis_service.analyze_unified(
        content=payload.content,
        context=payload.context,
        language=payload.language,
        mode=payload.mode,
    )

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI analysis service returned invalid result",
        )

    return {
        "success": bool(result.get("success", False)),
        "content": result.get("content", payload.content),
        "context": result.get("context", payload.context),
        "analysis": result,
    }
