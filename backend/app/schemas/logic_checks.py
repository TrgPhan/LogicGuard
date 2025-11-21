from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class ContextPayload(BaseModel):
    """Generic payload that carries document context + content."""

    context: Dict[str, Any] = Field(
        ..., description="Arbitrary context metadata supplied by the editor"
    )
    content: str = Field(..., min_length=1, description="Raw text that needs analysing")


class UnsupportedClaimsRequest(ContextPayload):
    """Request body for unsupported claim analysis."""

    mode: Optional[str] = Field(
        default="fast",
        description='Analysis mode: "fast" (default) or "deep".',
    )


class UndefinedTermsRequest(ContextPayload):
    """Request body for unified logic analysis (undefined terms + others)."""

    mode: Optional[str] = Field(
        default="fast",
        description='Analysis mode: "fast" (default) or "deep".',
    )


class Metadata(BaseModel):
    analyzed_at: Optional[str] = None
    model: Optional[str] = None
    threshold: Optional[float] = None
    error: Optional[str] = None


class UnsupportedClaimItem(BaseModel):
    claim: Optional[str] = None
    location: Optional[str] = None
    status: Literal["unsupported", "supported"]
    reason: Optional[str] = None
    surrounding_context: Optional[str] = None
    suggestion: Optional[str] = None
    evidence_type: Optional[str] = None
    evidence: Optional[str] = None


class UnsupportedClaimsResponse(BaseModel):
    success: bool
    content: str
    context: Dict[str, Any]
    total_claims_found: int
    total_unsupported: int
    unsupported_claims: List[UnsupportedClaimItem] = Field(default_factory=list)
    supported_claims: List[UnsupportedClaimItem] = Field(default_factory=list)
    metadata: Metadata


class UndefinedTermItem(BaseModel):
    term: Optional[str] = None
    first_appeared: Optional[str] = None
    context_snippet: Optional[str] = None
    is_defined: Optional[bool] = None
    reason: Optional[str] = None
    definition_found: Optional[str] = None


class UndefinedTermsResponse(BaseModel):
    success: bool
    content: str
    context: Dict[str, Any]
    total_terms_found: int
    total_undefined: int
    undefined_terms: List[UndefinedTermItem] = Field(default_factory=list)
    defined_terms: List[UndefinedTermItem] = Field(default_factory=list)
    metadata: Metadata


class ContradictionCheckRequest(BaseModel):
    text: str = Field(..., min_length=1)
    mode: Literal["base", "finetuned"] = "finetuned"
    threshold: float = 0.75
    use_embeddings_filter: bool = True
    embedding_model_name: str = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    top_k: int = 50
    sim_min: float = 0.30
    sim_max: float = 0.98
    batch_size: int = 8
    max_length: int = 128


class ContradictionItem(BaseModel):
    id: Optional[int] = None
    sentence1_index: Optional[int] = None
    sentence2_index: Optional[int] = None
    sentence1: Optional[str] = None
    sentence2: Optional[str] = None
    confidence: Optional[float] = None
    boosted: Optional[bool] = None


class ContradictionCheckResponse(BaseModel):
    success: bool
    mode: str
    model_path: Optional[str] = None
    text: str
    total_sentences: int
    sentences: List[str]
    total_contradictions: int
    contradictions: List[ContradictionItem]
    metadata: Metadata
