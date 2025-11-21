from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.models.user import User
from app.services.ai_analysis_service import ai_analysis_service

router = APIRouter(
    prefix="/functions",  # include ở main với prefix="/api/ai" → /api/ai/functions/...
    tags=["AI Functions"],
)


# ======================
# 📦 1. SCHEMAS
# ======================


class RunAIFunctionRequest(BaseModel):
    """
    Request chung cho AI Function.
    FE có thể truyền các function_name khác nhau nếu sau này mở rộng.
    """

    function_name: str = Field(
        ...,
        description="Tên function logic. Ví dụ: 'logicguard.unified_analysis'",
    )
    content: str = Field(..., description="Văn bản gốc cần phân tích")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Ngữ cảnh (writing_type, main_goal, criteria, constraints, ...)",
    )
    language: Optional[str] = Field(
        default=None,
        description="en | vi. Nếu bỏ trống sẽ auto detect",
    )
    mode: Optional[str] = Field(
        default="fast",
        description="Flag log lại. Hiện tại luôn dùng Gemini 2.5 (model trong .env GEMINI_MODEL).",
    )


class RunAIFunctionResponse(BaseModel):
    success: bool
    function_name: str
    data: Dict[str, Any]


# ======================
# 🚀 2. ENDPOINT CHÍNH
# ======================


@router.post(
    "/run",
    response_model=RunAIFunctionResponse,
    status_code=status.HTTP_200_OK,
)
async def run_ai_function(
    payload: RunAIFunctionRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Gateway duy nhất cho FE gọi các "AI Functions" liên quan đến phân tích logic.

    Giai đoạn 1:
    - Hỗ trợ function_name:
        + "logicguard.unified_analysis"
        + "logicguard.analyze_full" (alias của unified_analysis)

    Sau này có thể mở rộng thêm:
        + "logicguard.unsupported_claims_only"
        + "logicguard.undefined_terms_only"
        + ...
    """

    fn = payload.function_name.strip()

    # ===== 1) Unified analysis (5 subtasks) =====
    if fn in ("logicguard.unified_analysis", "logicguard.analyze_full"):
        result = await ai_analysis_service.analyze_unified(
            content=payload.content,
            context=payload.context,
            language=payload.language,
            mode=payload.mode or "fast",
        )

        return RunAIFunctionResponse(
            success=bool(result.get("success", False)),
            function_name=fn,
            data=result,
        )

    # ===== 2) Function name không support =====
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unknown or unsupported function_name '{fn}'",
    )
