"""
Subtask 3: Unsupported Claims (Luận điểm thiếu chứng cứ)
Mục tiêu:
 Xác định các câu mang tính khẳng định nhưng không có dữ kiện, ví dụ, hoặc trích dẫn hỗ trợ.
Đầu vào:
Văn bản thô cần phân tích.
Context (ngữ cảnh)

- Ví dụ đầu vào:
    context : {
    "writing_type": "Technical Proposal",
    "main_goal": "Chứng minh NoSQL có khả năng mở rộng tốt hơn",
    "criteria": ["nhắc đến scalability", "có luận cứ kỹ thuật", "xem xét chi phí"],
    "constraints": ["word_limit: 1000"]
    }
    content : "Nội dung bài viết "

- Mô hình claim–evidence classifier hoặc prompt LLM phân loại kiểu câu: supported,unsupported, evidence.
- Xử lý:
    Gắn nhãn từng câu.
    Kiểm tra khoảng cách ngữ cảnh: nếu claim không có evidence trong ±2 câu → flag "unsupported".
    Đầu ra:
    [
    {
        "claim": "AI can perfectly predict human emotions.",
        "status": "unsupported",
        "suggestion": "Add source, data, or example to support this claim."
    }
    ]
"""

import google.generativeai as genai
import json
import os
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

# Import from same directory
try:
    from .promptStore import prompt_unsupported_claims
except ImportError:
    from promptStore import prompt_unsupported_claims

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY_UNSUPPORTED_CLAIMS = os.getenv("GEMINI_API_KEY_UNSUPPORTED_CLAIMS")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not GEMINI_API_KEY_UNSUPPORTED_CLAIMS:
    raise ValueError("GEMINI_API_KEY_UNSUPPORTED_CLAIMS not found in environment variables")
genai.configure(api_key=GEMINI_API_KEY_UNSUPPORTED_CLAIMS)


def check_unsupported_claims(context: Dict[str, Any], content: str) -> Dict[str, Any]:
    """
    Phân tích văn bản để tìm các luận điểm thiếu chứng cứ
    
    Args:
        context: Dictionary chứa thông tin ngữ cảnh
            - writing_type: Loại văn bản
            - main_goal: Mục tiêu chính
            - criteria: Danh sách tiêu chí
            - constraints: Các ràng buộc
        content: Nội dung văn bản cần phân tích
        
    Returns:
        Dict[str, Any]: Kết quả phân tích
        {
            "success": bool,
            "content": str,
            "context": dict,
            "total_claims_found": int,
            "total_unsupported": int,
            "unsupported_claims": [
                {
                    "claim": str,
                    "location": str,
                    "status": "unsupported",
                    "reason": str,
                    "surrounding_context": str,
                    "suggestion": str
                }
            ],
            "supported_claims": [
                {
                    "claim": str,
                    "location": str,
                    "status": "supported",
                    "evidence_type": str,
                    "evidence": str
                }
            ],
            "metadata": {
                "analyzed_at": str,
                "model": str,
                "error": Optional[str]
            }
        }
    """
    
    result = {
        "success": False,
        "content": content,
        "context": context,
        "total_claims_found": 0,
        "total_unsupported": 0,
        "unsupported_claims": [],
        "supported_claims": [],
        "metadata": {
            "analyzed_at": datetime.utcnow().isoformat(),
            "model": GEMINI_MODEL,
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
        
        # Generate prompt using promptStore function
        prompt = prompt_unsupported_claims(context, content)
        
        # Initialize Gemini model
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Generate response from Gemini
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up response (remove markdown code blocks if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        elif response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove trailing ```
        
        response_text = response_text.strip()
        
        # Parse JSON response
        llm_result = json.loads(response_text)
        
        # Validate response structure
        if "unsupported_claims" not in llm_result:
            llm_result["unsupported_claims"] = []
        if "supported_claims" not in llm_result:
            llm_result["supported_claims"] = []
        if "total_claims_found" not in llm_result:
            llm_result["total_claims_found"] = len(llm_result["unsupported_claims"]) + len(llm_result.get("supported_claims", []))
        
        # Update result with LLM response
        result["success"] = True
        result["total_claims_found"] = llm_result.get("total_claims_found", 0)
        result["total_unsupported"] = len(llm_result["unsupported_claims"])
        result["unsupported_claims"] = llm_result["unsupported_claims"]
        result["supported_claims"] = llm_result.get("supported_claims", [])
        
    except json.JSONDecodeError as e:
        result["metadata"]["error"] = f"Failed to parse LLM response as JSON: {str(e)}"
        print(f"JSON Parse Error: {e}")
        print(f"Response text: {response_text[:500]}...")  # Print first 500 chars for debugging
        
    except Exception as e:
        result["metadata"]["error"] = f"Error during analysis: {str(e)}"
        print(f"Error: {e}")
    
    return result
