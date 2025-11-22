"""
Analysis - Gộp 4 Subtasks
========================================
1. Contradictions (Mâu thuẫn logic)
2. Undefined Terms (Thuật ngữ chưa định nghĩa)
3. Unsupported Claims (Luận điểm thiếu chứng cứ)
4. Logical Jumps (Nhảy logic)

Mục tiêu:
Phân tích toàn diện văn bản trong một lần gọi API duy nhất,
phát hiện tất cả các vấn đề về logic, terminology, evidence, và coherence.

Đầu vào:
- Context (ngữ cảnh)
- Content (văn bản thô)

Đầu ra:
Comprehensive JSON structure với đầy đủ 4 subtasks + summary
"""

import google.generativeai as genai
from google.generativeai import GenerationConfig
from google.generativeai.types import content_types
import json
import os
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

# Import from same directory
try:
    from .promptStore import prompt_analysis, prompt_analysis_vi
except ImportError:
    from promptStore import prompt_analysis, prompt_analysis_vi

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Define response schema to enforce JSON structure
# Updated to match simplified format in promptStore.py
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "analysis_metadata": {
            "type": "object",
            "properties": {
                "analyzed_at": {"type": "string"},
                "writing_type": {"type": "string"},
                "total_paragraphs": {"type": "integer"},
                "total_sentences": {"type": "integer"}
            },
            "required": []
        },
        "contradictions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "original_text": {"type": "string"},
                    "suggested_text": {"type": "string"},
                    "replacement_type": {"type": "string"}
                },
                "required": ["original_text", "suggested_text", "replacement_type"]
            }
        },
        "undefined_terms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "term": {"type": "string"},
                    "original_text": {"type": "string"},
                    "suggested_text": {"type": "string"},
                    "replacement_type": {"type": "string"}
                },
                "required": ["term", "original_text", "suggested_text", "replacement_type"]
            }
        },
        "unsupported_claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "original_text": {"type": "string"},
                    "suggested_text": {"type": "string"},
                    "replacement_type": {"type": "string"}
                },
                "required": ["original_text", "suggested_text", "replacement_type"]
            }
        },
        "logical_jumps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "suggested_text": {"type": "string"},
                    "replacement_type": {"type": "string"}
                },
                "required": ["location", "suggested_text", "replacement_type"]
            }
        },
        "summary": {
            "type": "object",
            "properties": {
                "total_issues": {"type": "integer"},
                "critical_issues": {"type": "integer"},
                "document_quality_score": {"type": "integer"},
                "key_recommendations": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": []
        }
    },
    "required": ["contradictions", "undefined_terms", "unsupported_claims", "logical_jumps"]
}


def analyze_document(context: Dict[str, Any], content: str, language: str = "en") -> Dict[str, Any]:
    """
    Phân tích toàn diện văn bản với 4 subtasks trong một lần gọi
    
    Args:
        context: Dictionary chứa thông tin ngữ cảnh
            - writing_type: Loại văn bản
            - main_goal: Mục tiêu chính
            - criteria: Danh sách tiêu chí
            - constraints: Các ràng buộc
        content: Nội dung văn bản cần phân tích
        language: Ngôn ngữ prompt ("en" hoặc "vi"). Mặc định: "en"
        
    Returns:
        Dict[str, Any]: Kết quả phân tích toàn diện
        {
            "success": bool,
            "content": str,
            "context": dict,
            "analysis_metadata": {
                "analyzed_at": str,
                "writing_type": str,
                "total_paragraphs": int,
                "total_sentences": int,
                "model": str
            },
            "contradictions": {
                "total_found": int,
                "items": [...]
            },
            "undefined_terms": {
                "total_found": int,
                "items": [...]
            },
            "unsupported_claims": {
                "total_found": int,
                "items": [...]
            },
            "logical_jumps": {
                "total_found": int,
                "items": [...]
            },
            "summary": {
                "total_issues": int,
                "critical_issues": int,
                "document_quality_score": int,
                "key_recommendations": [str]
            },
            "metadata": {
                "error": Optional[str]
            }
        }
    """
    
    result = {
        "success": False,
        "content": content,
        "context": context,
        "analysis_metadata": {
            "analyzed_at": datetime.utcnow().isoformat(),
            "writing_type": context.get("writing_type", "Document") if context else "Document",
            "total_paragraphs": 0,
            "total_sentences": 0,
            "model": GEMINI_MODEL
        },
        "contradictions": {
            "total_found": 0,
            "items": []
        },
        "undefined_terms": {
            "total_found": 0,
            "items": []
        },
        "unsupported_claims": {
            "total_found": 0,
            "items": []
        },
        "logical_jumps": {
            "total_found": 0,
            "items": []
        },
        "summary": {
            "total_issues": 0,
            "critical_issues": 0,
            "document_quality_score": 0,
            "key_recommendations": []
        },
        "metadata": {
            "error": None
        }
    }
    
    try:
        # Validate inputs
        if not content or not content.strip():
            result["metadata"]["error"] = "Content is empty"
            return result
        
        if not context or not isinstance(context, dict):
            result["metadata"]["error"] = "Invalid context format"
            return result
        
        # Validate language
        if language not in ["en", "vi"]:
            result["metadata"]["error"] = f"Invalid language '{language}'. Use 'en' or 'vi'"
            return result
        
        # Generate comprehensive prompt based on language
        if language == "vi":
            prompt = prompt_analysis_vi(context, content)
            print("Sử dụng prompt tiếng Việt...")
        else:
            prompt = prompt_analysis(context, content)
            print("Using English prompt...")
        
        # Validate prompt is not empty
        if not prompt or not prompt.strip():
            error_msg = "Generated prompt is empty"
            print(f"❌ {error_msg}")
            result["metadata"]["error"] = error_msg
            return result
        
        # Store language in metadata
        result["analysis_metadata"]["language"] = language
        
        # Initialize Gemini model with response schema
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA
        )
        model = genai.GenerativeModel(
            GEMINI_MODEL,
            generation_config=generation_config
        )
        
        # Generate response from Gemini
        lang_msg = "Đang phân tích văn bản toàn diện (4 nhiệm vụ)..." if language == "vi" else "Analyzing document comprehensively (all 4 subtasks)..."
        print(lang_msg)
        
        try:
            # Add timeout and better error handling
            import time
            start_time = time.time()
            print(f"[AI] Calling Gemini API... (this may take 30-120 seconds)")
            
            response = model.generate_content(prompt)
            
            elapsed_time = time.time() - start_time
            print(f"[AI] Gemini API call completed in {elapsed_time:.2f} seconds")
            
            if not response or not hasattr(response, 'text'):
                raise Exception("Empty or invalid response from Gemini API")
            
            response_text = response.text.strip()
            print(f"[AI] Response received, length: {len(response_text)} characters")
            
        except Exception as api_error:
            error_msg = f"Gemini API error: {str(api_error)}"
            print(f"❌ {error_msg}")
            result["metadata"]["error"] = error_msg
            return result
        
        # Parse JSON response (response_schema ensures clean JSON)
        llm_result = json.loads(response_text)
        
        # Update result with LLM response
        result["success"] = True
        
        # Extract analysis metadata
        if "analysis_metadata" in llm_result:
            result["analysis_metadata"].update(llm_result["analysis_metadata"])
        
        # Helper function to normalize format (new format is arrays, old format has items wrapper)
        def normalize_issue_format(issues_data, default_items_key="items"):
            """Convert new format (array) to old format (dict with items and total_found)"""
            if isinstance(issues_data, list):
                # New format: direct array
                return {
                    "total_found": len(issues_data),
                    "items": issues_data
                }
            elif isinstance(issues_data, dict):
                # Old format: already has structure
                if "items" in issues_data:
                    if "total_found" not in issues_data:
                        issues_data["total_found"] = len(issues_data.get("items", []))
                    return issues_data
                elif default_items_key in issues_data:
                    # Alternative key name
                    return {
                        "total_found": len(issues_data.get(default_items_key, [])),
                        "items": issues_data.get(default_items_key, [])
                    }
            return {"total_found": 0, "items": []}
        
        # Extract contradictions (new format: array, old format: dict with items)
        if "contradictions" in llm_result:
            result["contradictions"] = normalize_issue_format(llm_result["contradictions"])
        
        # Extract undefined terms
        if "undefined_terms" in llm_result:
            result["undefined_terms"] = normalize_issue_format(llm_result["undefined_terms"])
        
        # Extract unsupported claims
        if "unsupported_claims" in llm_result:
            result["unsupported_claims"] = normalize_issue_format(llm_result["unsupported_claims"])
        
        # Extract logical jumps
        if "logical_jumps" in llm_result:
            result["logical_jumps"] = normalize_issue_format(llm_result["logical_jumps"])
        
        # Extract summary
        if "summary" in llm_result:
            result["summary"] = llm_result["summary"]
        else:
            # Calculate summary if not provided
            total = (
                result["contradictions"]["total_found"] +
                result["undefined_terms"]["total_found"] +
                result["unsupported_claims"]["total_found"] +
                result["logical_jumps"]["total_found"]
            )
            result["summary"]["total_issues"] = total
        
        success_msg = f"✅ Phân tích hoàn tất! Tìm thấy {result['summary']['total_issues']} vấn đề" if language == "vi" else f"✅ Analysis complete! Found {result['summary']['total_issues']} total issues"
        print(success_msg)
        
    except json.JSONDecodeError as e:
        result["metadata"]["error"] = f"Failed to parse LLM response as JSON: {str(e)}"
        print(f"❌ JSON Parse Error: {e}")
        print(f"Response text: {response_text[:500]}...")
        
    except Exception as e:
        result["metadata"]["error"] = f"Error during analysis: {str(e)}"
        print(f"❌ Error: {e}")
    
    return result


def get_analysis_summary(analysis_result: Dict[str, Any]) -> str:
    """
    Tạo text summary từ kết quả phân tích
    
    Args:
        analysis_result: Kết quả từ analyze_document_comprehensive()
        
    Returns:
        str: Human-readable summary
    """
    if not analysis_result.get("success"):
        return f"Analysis failed: {analysis_result.get('metadata', {}).get('error', 'Unknown error')}"
    
    lines = []
    lines.append("=" * 80)
    lines.append("DOCUMENT ANALYSIS SUMMARY")
    lines.append("=" * 80)
    
    meta = analysis_result.get("analysis_metadata", {})
    lines.append(f"\nWriting Type: {meta.get('writing_type', 'N/A')}")
    lines.append(f"Total Paragraphs: {meta.get('total_paragraphs', 0)}")
    lines.append(f"Total Sentences: {meta.get('total_sentences', 0)}")
    lines.append(f"Analyzed At: {meta.get('analyzed_at', 'N/A')}")
    
    summary = analysis_result.get("summary", {})
    lines.append(f"\n📊 OVERALL QUALITY SCORE: {summary.get('document_quality_score', 0)}/100")
    lines.append(f"Total Issues Found: {summary.get('total_issues', 0)}")
    lines.append(f"Critical Issues: {summary.get('critical_issues', 0)}")
    
    # Contradictions
    contra = analysis_result.get("contradictions", {})
    lines.append(f"\n🔴 CONTRADICTIONS: {contra.get('total_found', 0)} found")
    if contra.get("items"):
        for item in contra["items"][:3]:
            original = item.get('original_text', item.get('sentence1', 'N/A'))
            lines.append(f"  - {original[:70]}...")
    
    # Undefined Terms
    terms = analysis_result.get("undefined_terms", {})
    lines.append(f"\n📚 UNDEFINED TERMS: {terms.get('total_found', 0)} found")
    if terms.get("items"):
        for item in terms["items"][:5]:
            term = item.get('term', 'N/A')
            lines.append(f"  - {term}")
    
    # Unsupported Claims
    claims = analysis_result.get("unsupported_claims", {})
    lines.append(f"\n⚠️  UNSUPPORTED CLAIMS: {claims.get('total_found', 0)} found")
    if claims.get("items"):
        for item in claims["items"][:3]:
            original = item.get('original_text', item.get('claim', 'N/A'))
            lines.append(f"  - {original[:70]}...")
    
    # Logical Jumps
    jumps = analysis_result.get("logical_jumps", {})
    lines.append(f"\n🔀 LOGICAL JUMPS: {jumps.get('total_found', 0)} found")
    if jumps.get("items"):
        for item in jumps["items"]:
            location = item.get('location', f"Paragraph {item.get('from_paragraph', '?')} → {item.get('to_paragraph', '?')}")
            lines.append(f"  - {location}")
    
    # Key Recommendations
    if summary.get("key_recommendations"):
        lines.append("\n💡 KEY RECOMMENDATIONS:")
        for i, rec in enumerate(summary["key_recommendations"], 1):
            lines.append(f"  {i}. {rec}")
    
    lines.append("\n" + "=" * 80)
    
    return "\n".join(lines)
