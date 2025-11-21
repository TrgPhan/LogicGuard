from typing import Any, Dict, Optional

from app.ai.models.Analysis import analyze_document as _analyze_document


class AIAnalysisService:
    """
    Service trung gian để gọi unified logic analysis (Gemini 2.5).

    - KHÔNG phụ thuộc FastAPI (router)
    - KHÔNG import ngược lại app.services.* để tránh circular import
    - Được dùng bởi:
        + AI Functions Gateway (app/routers/ai_functions.py)
        + Bất kỳ chỗ nào khác muốn xài unified analysis
    """

    def __init__(self) -> None:
        # Sau này nếu muốn inject logger, config riêng, ... thì thêm ở đây
        ...

    @staticmethod
    def _detect_language(text: Optional[str], context: Optional[Any] = None) -> str:
        """
        Đoán language = 'vi' hoặc 'en' dựa trên nội dung (có dấu tiếng Việt hay không).
        Dùng chung cho các chỗ cần detect language.
        """
        if not text:
            text = ""

        vi_chars = (
            "ăâêôơưđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊ"
            "ÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ"
            "áàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩị"
            "óòỏõọốồổỗộớờởỡợúùủũứừửữựýỳỷỹỵ"
        )
        has_vi = any(ch in vi_chars for ch in text)

        if not has_vi and isinstance(context, str):
            has_vi = any(ch in vi_chars for ch in context)

        return "vi" if has_vi else "en"

    def _build_context_dict(
        self,
        raw_context: Optional[Any],
        fallback_main_goal: str = "Analyze document for logical issues",
    ) -> Dict[str, Any]:
        """
        Chuẩn hóa context về dict đúng format cho Analysis.analyze_document.

        - Nếu FE gửi dict thì dùng luôn.
        - Nếu gửi string thì wrap lại.
        - Nếu None thì tạo context mặc định.
        """
        if isinstance(raw_context, dict):
            # đảm bảo không trả về None
            return raw_context or {}

        main_goal = (raw_context or fallback_main_goal or "").strip()
        return {
            "writing_type": "Document",
            "main_goal": main_goal or fallback_main_goal,
            "criteria": [],
            "constraints": [],
        }

    async def analyze_unified(
        self,
        *,
        content: str,
        context: Optional[Any] = None,
        language: Optional[str] = None,
        mode: str = "fast",
    ) -> Dict[str, Any]:
        """
        Gọi unified analysis (5 subtasks):
          1) contradictions
          2) undefined_terms
          3) unsupported_claims
          4) logical_jumps
          5) spelling_errors

        Trả về đúng structure của app.ai.models.Analysis.analyze_document
        để FE có thể tái sử dụng luôn.
        """

        # 1) Chuẩn hóa context
        context_dict = self._build_context_dict(
            raw_context=context,
            fallback_main_goal="Analyze document for logical issues (unified)",
        )

        # 2) Nếu FE không truyền language thì auto detect
        lang = (language or "").strip().lower()
        if lang not in ("en", "vi"):
            lang = self._detect_language(content, context)

        # 3) Gọi hàm core (đồng bộ)
        #   - Hiện tại cứ gọi trực tiếp
        #   - Sau này nếu muốn offload sang thread pool / task queue thì chỉnh chỗ này
        result = _analyze_document(
            context=context_dict,
            content=content,
            language=lang,
            mode=mode or "fast",
        )

        # 4) Bọc thêm metadata nhẹ cho AI Function
        result.setdefault("metadata", {})
        result["metadata"].setdefault("engine", "gemini_unified_analysis")
        result["metadata"].setdefault("language", lang)

        return result


# Singleton instance cho toàn app
ai_analysis_service = AIAnalysisService()
