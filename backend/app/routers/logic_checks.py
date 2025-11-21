from typing import Any, Dict, Optional, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.logic_checks import (
    ContradictionCheckRequest,
    ContradictionCheckResponse,
    UndefinedTermsRequest,
    UndefinedTermsResponse,  # hiện chưa dùng trực tiếp cho unified, nhưng cứ import sẵn
    UnsupportedClaimsRequest,
    UnsupportedClaimsResponse,
)
from app.ai.models.contradictions import check_contradictions
from app.ai.models.Analysis import analyze_document

router = APIRouter(prefix="/logic-checks", tags=["Logic Checks"])


def _wrap_analysis_call(func, *args, error_message: str, **kwargs):
    try:
        return func(*args, **kwargs)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{error_message}: {exc}",
        ) from exc


def _detect_language(text: Optional[str], context: Optional[Any] = None) -> str:
    """
    Đoán language = 'vi' hoặc 'en' dựa trên nội dung (có dấu tiếng Việt hay không).
    """
    if not text:
        text = ""

    vi_chars = (
        "ăâêôơưđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ"
        "áàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũứừửữựýỳỷỹỵ"
    )
    has_vi = any(ch in vi_chars for ch in text)

    if not has_vi and isinstance(context, str):
        has_vi = any(ch in vi_chars for ch in context)

    return "vi" if has_vi else "en"


def _build_context_dict(raw_context: Any, fallback_main_goal: str = "") -> Dict[str, Any]:
    """
    Chuyển context từ frontend thành dict đúng format cho Analysis.analyze_document.
    - Nếu frontend đã gửi dict thì dùng luôn.
    - Nếu gửi string thì wrap lại thành dict đơn giản.
    """
    if isinstance(raw_context, dict):
        return raw_context or {}

    main_goal = (raw_context or fallback_main_goal or "").strip()
    return {
        "writing_type": "Document",
        "main_goal": main_goal or "Analyze document for logical issues",
        "criteria": [],
        "constraints": [],
    }


@router.post("/unsupported-claims", response_model=UnsupportedClaimsResponse)
def analyze_unsupported_claims(
    payload: UnsupportedClaimsRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Unsupported claims – dùng unified Analysis (Gemini),
    map kết quả về schema UnsupportedClaimsResponse.
    """

    context_dict = _build_context_dict(
        payload.context,
        fallback_main_goal="Detect unsupported claims",
    )
    language = _detect_language(payload.content, payload.context)

    analysis_mode = getattr(payload, "mode", None) or "fast"

    full_result = _wrap_analysis_call(
        analyze_document,
        context_dict,
        payload.content,
        language=language,
        mode=analysis_mode,
        error_message="Unsupported claims analysis failed",
    )

    section = full_result.get("unsupported_claims") or {}
    raw_items = section.get("items") or []

    unsupported_list: List[Dict[str, Any]] = []
    supported_list: List[Dict[str, Any]] = []

    for raw in raw_items:
        if not isinstance(raw, dict):
            continue

        status_raw = (raw.get("status") or "unsupported").lower()
        status = "supported" if status_raw == "supported" else "unsupported"

        item = {
            "claim": raw.get("claim"),
            "location": raw.get("location"),
            "status": status,
            "reason": raw.get("reason") or raw.get("explanation"),
            "surrounding_context": raw.get("surrounding_context"),
            "suggestion": raw.get("suggestion"),
            "evidence_type": raw.get("evidence_type"),
            "evidence": raw.get("evidence"),
        }

        if status == "supported":
            supported_list.append(item)
        else:
            unsupported_list.append(item)

    total_claims_found = len(raw_items)
    total_unsupported = len(unsupported_list)

    meta_src = full_result.get("analysis_metadata", {}) or {}
    error_msg = None
    if isinstance(full_result.get("metadata"), dict):
        error_msg = full_result["metadata"].get("error")

    metadata = {
        "analyzed_at": meta_src.get("analyzed_at"),
        "model": meta_src.get("model"),
        "threshold": None,
        "error": error_msg,
    }

    return {
        "success": True,
        "content": payload.content,
        "context": context_dict,
        "total_claims_found": total_claims_found,
        "total_unsupported": total_unsupported,
        "unsupported_claims": unsupported_list,
        "supported_claims": supported_list,
        "metadata": metadata,
    }


@router.post("/undefined-terms")
def analyze_undefined_terms(
    payload: UndefinedTermsRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Unified endpoint:
    - Gọi analyze_document (Gemini) 1 lần
    - Gom tất cả loại lỗi (undefined_terms, unsupported_claims,
      logical_jumps, contradictions) vào 1 list `issues` cho frontend.
    """

    print("=== [logic-checks] /undefined-terms called ===")
    print("Content length:", len(payload.content or ""))

    context_dict = _build_context_dict(
        payload.context,
        fallback_main_goal=(
            "Detect logical issues (undefined terms, unsupported claims, "
            "logical jumps, contradictions)"
        ),
    )
    language = _detect_language(payload.content, payload.context)
    print("Detected language:", language)

    analysis_mode = getattr(payload, "mode", None) or "fast"
    print("Analysis mode:", analysis_mode)

    # 👉 Không dùng _wrap_analysis_call cho endpoint unified
    try:
        full_result = analyze_document(
            context_dict,
            payload.content,
            language=language,
            mode=analysis_mode,
        )
    except Exception as exc:
        # Nếu Gemini/phân tích lỗi nặng → log + trả về success=False nhưng vẫn 200
        import traceback

        print("❌ analyze_document crashed in /undefined-terms:", repr(exc))
        traceback.print_exc()

        return {
            "success": False,
            "content": payload.content,
            "context": context_dict,
            "total_terms_found": 0,
            "total_undefined": 0,
            "metadata": {
                "language": language,
                "issues_by_type": {},
                "engine": "gemini_unified_analysis",
                "raw_summary": {},
                "error": str(exc),
            },
            "issues": [],
            "items": [],
        }

    aggregated_items: List[Dict[str, Any]] = []

    def _add_items_from_section(section_key: str, issue_type: str) -> None:
        section = full_result.get(section_key) or {}
        raw_items = section.get("items") or []
        if not isinstance(raw_items, list):
            return

        for raw in raw_items:
            if not isinstance(raw, dict):
                continue

            # Ưu tiên text từ backend (nếu có)
            text = (
                raw.get("text")
                or raw.get("term")
                or raw.get("claim")
                or raw.get("sentence1")
                or raw.get("phrase")
                or ""
            )

            reason = (
                raw.get("reason")
                or raw.get("message")
                or raw.get("explanation")
                or ""
            )

            suggestion = (
                raw.get("suggestion")
                or raw.get("fix")
                or raw.get("rewrite")
                or ""
            )

            start_pos = raw.get("start_pos") or raw.get("start") or 0
            end_pos = raw.get("end_pos") or raw.get("end") or 0

            # Nếu vẫn chưa có text → fallback theo loại lỗi
            if not text:
                if issue_type == "undefined_term":
                    term = raw.get("term") or "Undefined term"
                    text = term
                elif issue_type == "unsupported_claim":
                    claim = (raw.get("claim") or "").strip()
                    text = claim or "Unsupported claim"
                elif issue_type == "logical_jump":
                    fp = raw.get("from_paragraph")
                    tp = raw.get("to_paragraph")
                    text = (
                        f"Possible logical jump between paragraphs {fp} and {tp}"
                        if fp and tp
                        else "Logical jump between ideas"
                    )
                elif issue_type == "logic_contradiction":
                    s1 = (raw.get("sentence1") or "").strip()
                    s2 = (raw.get("sentence2") or "").strip()
                    if s1 or s2:
                        text = f"{s1} ↔ {s2}".strip()
                    else:
                        text = "Contradictory statements detected"

            aggregated_items.append(
                {
                    "id": raw.get("id") or f"{issue_type}_{len(aggregated_items) + 1}",
                    "type": issue_type,
                    "text": text,
                    "reason": reason,
                    "suggestion": suggestion,
                    "start_pos": start_pos,
                    "end_pos": end_pos,
                }
            )

    sections = [
        ("undefined_terms", "undefined_term"),
        ("unsupported_claims", "unsupported_claim"),
        ("logical_jumps", "logical_jump"),
        ("contradictions", "logic_contradiction"),
    ]

    for key, issue_type in sections:
        _add_items_from_section(key, issue_type)

    issues_by_type: Dict[str, int] = {}
    for item in aggregated_items:
        t = item.get("type") or "unknown"
        issues_by_type[t] = issues_by_type.get(t, 0) + 1

    total_undefined = issues_by_type.get("undefined_term", 0)

    response: Dict[str, Any] = {
        "success": full_result.get("success", False),
        "content": payload.content,
        "context": context_dict,
        "total_terms_found": total_undefined,
        "total_undefined": total_undefined,
        "metadata": {
            "language": language,
            "issues_by_type": issues_by_type,
            "engine": "gemini_unified_analysis",
            "raw_summary": full_result.get("summary", {}),
            "error": (full_result.get("metadata") or {}).get("error"),
        },
        "issues": aggregated_items,
        "items": aggregated_items,
    }

    print(f"✅ Unified analysis done. Total items: {len(aggregated_items)}")
    return response


@router.post("/contradictions", response_model=ContradictionCheckResponse)
def analyze_contradictions(
    payload: ContradictionCheckRequest,
    current_user: User = Depends(get_current_user),
):
    """Expose contradiction detection to the frontend."""
    return _wrap_analysis_call(
        check_contradictions,
        payload.text,
        mode=payload.mode,
        threshold=payload.threshold,
        use_embeddings_filter=payload.use_embeddings_filter,
        embedding_model_name=payload.embedding_model_name,
        top_k=payload.top_k,
        sim_min=payload.sim_min,
        sim_max=payload.sim_max,
        batch_size=payload.batch_size,
        max_length=payload.max_length,
        error_message="Contradiction analysis failed",
    )
