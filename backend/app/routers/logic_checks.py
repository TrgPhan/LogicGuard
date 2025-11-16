from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.logic_checks import (
    ContradictionCheckRequest,
    ContradictionCheckResponse,
    UndefinedTermsRequest,
    UndefinedTermsResponse,
    UnsupportedClaimsRequest,
    UnsupportedClaimsResponse,
)
from app.ai.models.contradictions import check_contradictions
from app.ai.models.undefinedTerms import check_undefined_terms
from app.ai.models.unsupportedClaims import check_unsupported_claims

router = APIRouter(prefix="/logic-checks", tags=["Logic Checks"])


def _wrap_analysis_call(func, *args, error_message: str, **kwargs):
    try:
        return func(*args, **kwargs)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    except Exception as exc:  # noqa: BLE001 - propagate as HTTP error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{error_message}: {exc}"
        ) from exc


@router.post("/unsupported-claims", response_model=UnsupportedClaimsResponse)
def analyze_unsupported_claims(
    payload: UnsupportedClaimsRequest,
    current_user: User = Depends(get_current_user)
):
    """Expose unsupported-claim detection to the frontend."""

    return _wrap_analysis_call(
        check_unsupported_claims,
        payload.context,
        payload.content,
        error_message="Unsupported claims analysis failed"
    )


@router.post("/undefined-terms", response_model=UndefinedTermsResponse)
def analyze_undefined_terms(
    payload: UndefinedTermsRequest,
    current_user: User = Depends(get_current_user)
):
    """Expose undefined-term detection to the frontend."""

    return _wrap_analysis_call(
        check_undefined_terms,
        payload.context,
        payload.content,
        error_message="Undefined terms analysis failed"
    )


@router.post("/contradictions", response_model=ContradictionCheckResponse)
def analyze_contradictions(
    payload: ContradictionCheckRequest,
    current_user: User = Depends(get_current_user)
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
        error_message="Contradiction analysis failed"
    )
