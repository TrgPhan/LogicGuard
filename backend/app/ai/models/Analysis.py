"""
Analysis - Gộp 4 Subtasks + Spelling
========================================
1. Contradictions (Mâu thuẫn logic)
2. Undefined Terms (Thuật ngữ chưa định nghĩa)
3. Unsupported Claims (Luận điểm thiếu chứng cứ)
4. Logical Jumps (Nhảy logic)
5. Spelling Errors (Lỗi chính tả EN + VI)

Mục tiêu:
Phân tích toàn diện văn bản trong một lần gọi API duy nhất,
phát hiện tất cả các vấn đề về logic, terminology, evidence, coherence và spelling.

Đầu vào:
- Context (ngữ cảnh)
- Content (văn bản thô)

Đầu ra:
Comprehensive JSON structure với đầy đủ 5 subtasks + summary
"""

from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

import google.generativeai as genai
from google.generativeai import GenerationConfig
from dotenv import load_dotenv

from .promptStore import prompt_analysis, prompt_analysis_vi
from .term_normalizer import NormalizationResult, normalize_text

# -------------------------------------------------------------------
# Gemini config: đọc từ biến môi trường (.env backend)
# -------------------------------------------------------------------

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# -------------------------------------------------------------------
# JSON schema cho Gemini
# -------------------------------------------------------------------

RESPONSE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "analysis_metadata": {
            "type": "object",
            "properties": {
                "analyzed_at": {"type": "string"},
                "writing_type": {"type": "string"},
                "total_paragraphs": {"type": "integer"},
                "total_sentences": {"type": "integer"},
            },
            "required": [
                "analyzed_at",
                "writing_type",
                "total_paragraphs",
                "total_sentences",
            ],
        },
        "contradictions": {
            "type": "object",
            "properties": {
                "total_found": {"type": "integer"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "sentence1": {"type": "string"},
                            "sentence2": {"type": "string"},
                            "sentence1_location": {"type": "string"},
                            "sentence2_location": {"type": "string"},
                            "contradiction_type": {"type": "string"},
                            "severity": {"type": "string"},
                            "explanation": {"type": "string"},
                            "suggestion": {"type": "string"},
                        },
                        "required": ["sentence1", "sentence2", "explanation"],
                    },
                },
            },
            "required": ["total_found", "items"],
        },
        "undefined_terms": {
            "type": "object",
            "properties": {
                "total_found": {"type": "integer"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "term": {"type": "string"},
                            "first_appeared": {"type": "string"},
                            "context_snippet": {"type": "string"},
                            "is_defined": {"type": "boolean"},
                            "reason": {"type": "string"},
                            "suggestion": {"type": "string"},
                        },
                        "required": ["term", "reason"],
                    },
                },
            },
            "required": ["total_found", "items"],
        },
        "unsupported_claims": {
            "type": "object",
            "properties": {
                "total_found": {"type": "integer"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "claim": {"type": "string"},
                            "location": {"type": "string"},
                            "status": {"type": "string"},
                            "claim_type": {"type": "string"},
                            "reason": {"type": "string"},
                            "surrounding_context": {"type": "string"},
                            "suggestion": {"type": "string"},
                        },
                        "required": ["claim", "reason"],
                    },
                },
            },
            "required": ["total_found", "items"],
        },
        "logical_jumps": {
            "type": "object",
            "properties": {
                "total_found": {"type": "integer"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from_paragraph": {"type": "integer"},
                            "to_paragraph": {"type": "integer"},
                            "from_paragraph_summary": {"type": "string"},
                            "to_paragraph_summary": {"type": "string"},
                            "coherence_score": {"type": "number"},
                            "flag": {"type": "string"},
                            "severity": {"type": "string"},
                            "explanation": {"type": "string"},
                            "suggestion": {"type": "string"},
                        },
                        "required": [
                            "from_paragraph",
                            "to_paragraph",
                            "coherence_score",
                            "explanation",
                        ],
                    },
                },
            },
            "required": ["total_found", "items"],
        },
        # Spelling errors (EN + VI) do Gemini trả về
        "spelling_errors": {
            "type": "object",
            "properties": {
                "total_found": {"type": "integer"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "original": {"type": "string"},
                            "suggested": {"type": "string"},
                            "start_pos": {"type": "integer"},
                            "end_pos": {"type": "integer"},
                            "language": {"type": "string"},
                            "reason": {"type": "string"},
                        },
                        "required": ["original", "suggested"],
                    },
                },
            },
            "required": ["total_found", "items"],
        },
        "summary": {
            "type": "object",
            "properties": {
                "total_issues": {"type": "integer"},
                "critical_issues": {"type": "integer"},
                "document_quality_score": {"type": "integer"},
                "key_recommendations": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": [
                "total_issues",
                "critical_issues",
                "document_quality_score",
                "key_recommendations",
            ],
        },
    },
    "required": [
        "analysis_metadata",
        "contradictions",
        "undefined_terms",
        "unsupported_claims",
        "logical_jumps",
        "spelling_errors",
        "summary",
    ],
}


def analyze_document(
    context: Dict[str, Any],
    content: str,
    language: str = "en",
    mode: str = "fast",  # chỉ để log, không đổi model
) -> Dict[str, Any]:
    """
    Phân tích toàn diện văn bản với 5 subtasks trong một lần gọi.
    (4 logic + 1 spelling)
    """

    selected_model = GEMINI_MODEL  # luôn dùng 1 model Gemini 2.5

    result: Dict[str, Any] = {
        "success": False,
        "content": content,  # giữ nguyên văn bản gốc cho FE
        "context": context,
        "analysis_metadata": {
            "analyzed_at": datetime.utcnow().isoformat(),
            "writing_type": context.get("writing_type", "Document") if context else "Document",
            "total_paragraphs": 0,
            "total_sentences": 0,
            "model": selected_model,
            "mode_used": mode,
        },
        "contradictions": {"total_found": 0, "items": []},
        "undefined_terms": {"total_found": 0, "items": []},
        "unsupported_claims": {"total_found": 0, "items": []},
        "logical_jumps": {"total_found": 0, "items": []},
        "spelling_errors": {"total_found": 0, "items": []},
        "summary": {
            "total_issues": 0,
            "critical_issues": 0,
            "document_quality_score": 0,
            "key_recommendations": [],
        },
        "metadata": {
            "error": None,
            "normalization": {},
            "spelling_errors_rule_based": [],
        },
    }

    try:
        # -------- Validate input --------
        if not content or not content.strip():
            result["metadata"]["error"] = "Content is empty"
            return result

        if not context or not isinstance(context, Dict):
            result["metadata"]["error"] = "Invalid context format"
            return result

        if language not in ["en", "vi"]:
            result["metadata"]["error"] = f"Invalid language '{language}'. Use 'en' or 'vi'."
            return result

        # -------- 1) SPELL & TERM NORMALIZATION (nhẹ, an toàn) --------
        norm: NormalizationResult = normalize_text(content, language=language)

        # Feed văn bản gốc vào LLM, không thay đổi text user
        normalized_content_for_llm = content

        result["metadata"]["normalization"] = {
            "changed": norm.normalized_text != norm.original_text,
            "total_spelling_corrections": len(getattr(norm, "spelling_corrections", [])),
            "total_term_mappings": len(getattr(norm, "term_mappings", [])),
        }
        result["metadata"]["spelling_errors_rule_based"] = getattr(
            norm, "spelling_corrections", []
        )

        if norm.normalized_text != norm.original_text:
            print(
                f"[Normalization] Text normalized (light) "
                f"(spelling_corrections={result['metadata']['normalization']['total_spelling_corrections']}, "
                f"term_mappings={result['metadata']['normalization']['total_term_mappings']})"
            )

        # -------- 2) Build prompt theo ngôn ngữ --------
        if language == "vi":
            prompt = prompt_analysis_vi(context, normalized_content_for_llm)
            print("Sử dụng prompt tiếng Việt...")
        else:
            prompt = prompt_analysis(context, normalized_content_for_llm)
            print("Using English prompt...")

        result["analysis_metadata"]["language"] = language

        # -------- 3) Gọi Gemini với schema --------
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
        )
        model = genai.GenerativeModel(
            selected_model,
            generation_config=generation_config,
        )

        lang_msg = (
            "Đang phân tích văn bản toàn diện (5 nhiệm vụ: 4 logic + spelling)..."
            if language == "vi"
            else "Analyzing document comprehensively (5 subtasks: 4 logic + spelling)..."
        )
        print(f"{lang_msg} | model={selected_model} | mode_flag={mode}")

        # Retry parse JSON tối đa 2 lần
        last_error: Optional[Exception] = None
        llm_result: Optional[Dict[str, Any]] = None
        response_text: str = ""

        for attempt in range(2):
            try:
                response = model.generate_content(prompt)
                response_text = (response.text or "").strip()
                llm_result = json.loads(response_text)
                break
            except json.JSONDecodeError as e:
                last_error = e
                print(f"❌ JSON Parse Error (attempt {attempt + 1}): {e}")
                print(f"Response text (first 500 chars): {response_text[:500]}...")

        if llm_result is None:
            result["metadata"]["error"] = (
                f"Failed to parse LLM response as JSON after retries: {last_error}"
            )
            return result

        result["success"] = True

        # -------- Merge kết quả từ LLM vào result chuẩn --------

        # analysis_metadata
        if "analysis_metadata" in llm_result:
            result["analysis_metadata"].update(llm_result["analysis_metadata"])

        # contradictions
        if "contradictions" in llm_result:
            result["contradictions"] = llm_result["contradictions"]
            if "total_found" not in result["contradictions"]:
                result["contradictions"]["total_found"] = len(
                    result["contradictions"].get("items", []) or []
                )

        # undefined_terms
        if "undefined_terms" in llm_result:
            result["undefined_terms"] = llm_result["undefined_terms"]
            if "total_found" not in result["undefined_terms"]:
                result["undefined_terms"]["total_found"] = len(
                    result["undefined_terms"].get("items", []) or []
                )

        # unsupported_claims
        if "unsupported_claims" in llm_result:
            result["unsupported_claims"] = llm_result["unsupported_claims"]
            if "total_found" not in result["unsupported_claims"]:
                result["unsupported_claims"]["total_found"] = len(
                    result["unsupported_claims"].get("items", []) or []
                )

        # logical_jumps
        if "logical_jumps" in llm_result:
            result["logical_jumps"] = llm_result["logical_jumps"]
            if "total_found" not in result["logical_jumps"]:
                result["logical_jumps"]["total_found"] = len(
                    result["logical_jumps"].get("items", []) or []
                )

        # spelling_errors
        if "spelling_errors" in llm_result:
            result["spelling_errors"] = llm_result["spelling_errors"]
            if "total_found" not in result["spelling_errors"]:
                result["spelling_errors"]["total_found"] = len(
                    result["spelling_errors"].get("items", []) or []
                )

        # summary
        if "summary" in llm_result:
            result["summary"] = llm_result["summary"]
        else:
            total = (
                result["contradictions"]["total_found"]
                + result["undefined_terms"]["total_found"]
                + result["unsupported_claims"]["total_found"]
                + result["logical_jumps"]["total_found"]
                + result["spelling_errors"]["total_found"]
            )
            result["summary"]["total_issues"] = total

        print(
            f"✅ Phân tích hoàn tất. "
            f"Tổng issues: {result['summary'].get('total_issues', 0)}"
        )

    except Exception as e:
        result["metadata"]["error"] = f"Error during analysis: {str(e)}"
        print(f"❌ Error in analyze_document: {e}")

    return result


def get_analysis_summary(analysis_result: Dict[str, Any]) -> str:
    """
    Tạo text summary từ kết quả phân tích (debug / log).
    """
    if not analysis_result.get("success"):
        return f"Analysis failed: {analysis_result.get('metadata', {}).get('error', 'Unknown error')}"

    lines: List[str] = []
    lines.append("=" * 80)
    lines.append("DOCUMENT ANALYSIS SUMMARY")
    lines.append("=" * 80)

    meta = analysis_result.get("analysis_metadata", {})
    lines.append(f"\nWriting Type: {meta.get('writing_type', 'N/A')}")
    lines.append(f"Mode Flag: {meta.get('mode_used', 'N/A')}")
    lines.append(f"Model: {meta.get('model', 'N/A')}")
    lines.append(f"Total Paragraphs: {meta.get('total_paragraphs', 0)}")
    lines.append(f"Total Sentences: {meta.get('total_sentences', 0)}")
    lines.append(f"Analyzed At: {meta.get('analyzed_at', 'N/A')}")

    summary = analysis_result.get("summary", {})
    lines.append(
        f"\n📊 OVERALL QUALITY SCORE: {summary.get('document_quality_score', 0)}/100"
    )
    lines.append(f"Total Issues Found: {summary.get('total_issues', 0)}")
    lines.append(f"Critical Issues: {summary.get('critical_issues', 0)}")

    # Contradictions
    contra = analysis_result.get("contradictions", {})
    lines.append(f"\n🔴 CONTRADICTIONS: {contra.get('total_found', 0)} found")
    if contra.get("items"):
        for item in contra["items"][:3]:
            lines.append(
                f"  - {item.get('sentence1', '')[:60]}... ↔ "
                f"{item.get('sentence2', '')[:60]}..."
            )

    # Undefined Terms
    terms = analysis_result.get("undefined_terms", {})
    lines.append(f"\n📚 UNDEFINED TERMS: {terms.get('total_found', 0)} found")
    if terms.get("items"):
        for item in terms["items"][:5]:
            lines.append(f"  - {item.get('term', 'N/A')}")

    # Unsupported Claims
    claims = analysis_result.get("unsupported_claims", {})
    lines.append(f"\n⚠️  UNSUPPORTED CLAIMS: {claims.get('total_found', 0)} found")
    if claims.get("items"):
        for item in claims["items"][:3]:
            lines.append(f"  - {item.get('claim', 'N/A')[:70]}...")

    # Logical Jumps
    jumps = analysis_result.get("logical_jumps", {})
    lines.append(f"\n🔀 LOGICAL JUMPS: {jumps.get('total_found', 0)} found")
    if jumps.get("items"):
        for item in jumps["items"]:
            lines.append(
                f"  - Paragraph {item.get('from_paragraph', '?')} → "
                f"{item.get('to_paragraph', '?')} "
                f"(coherence: {item.get('coherence_score', 0)})"
            )

    # Spelling errors
    spell = analysis_result.get("spelling_errors", {})
    lines.append(f"\n✏️  SPELLING ERRORS: {spell.get('total_found', 0)} found")
    if spell.get("items"):
        for item in spell["items"][:5]:
            lines.append(
                f"  - {item.get('original', '')} → {item.get('suggested', '')} "
                f"({item.get('language', 'unknown')})"
            )

    # Key Recommendations
    if summary.get("key_recommendations"):
        lines.append("\n💡 KEY RECOMMENDATIONS:")
        for i, rec in enumerate(summary["key_recommendations"], 1):
            lines.append(f"  {i}. {rec}")

    lines.append("\n" + "=" * 80)
    return "\n".join(lines)
