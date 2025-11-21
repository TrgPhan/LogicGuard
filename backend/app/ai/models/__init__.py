# Make this folder a Python package
# and expose key modules for cleaner imports.

from .Analysis import analyze_document
from .promptStore import (
    prompt_analysis,
    prompt_analysis_vi
)
from .term_normalizer import (
    normalize_text,
    NormalizationResult
)

__all__ = [
    "analyze_document",
    "prompt_analysis",
    "prompt_analysis_vi",
    "normalize_text",
    "NormalizationResult",
]
