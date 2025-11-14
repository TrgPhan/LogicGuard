"""
Subtask 2: Undefined Terms (Thuật ngữ chưa định nghĩa)
- Mục tiêu:
 Nhận diện các thuật ngữ, khái niệm, hoặc từ chuyên ngành chưa được định nghĩa hoặc giải thích ở đâu trong bài.
- Đầu vào:
    Context (ngữ cảnh)
    Văn bản thô của bài viết hoặc tài liệu.

- Ví dụ đầu vào:
    context : {
    "writing_type": "Technical Proposal",
    "main_goal": "Chứng minh NoSQL có khả năng mở rộng tốt hơn",
    "criteria": ["nhắc đến scalability", "có luận cứ kỹ thuật", "xem xét chi phí"],
    "constraints": ["word_limit: 1000"]
    }

    content : "Nội dung bài viết "

- Xử lý:
    Theo dõi lần đầu tiên mỗi thực thể (term, khái niệm) xuất hiện.
    Kiểm tra xem ở đoạn đầu đó có xuất hiện cụm “là”, “được hiểu là”, “gọi là”, “(viết tắt của …)” hoặc pattern định nghĩa tương tự không.
    Nếu không, flag entity là “chưa được định nghĩa”.
- Ví dụ đầu ra:
    [
    {
        "term": "gradient clipping",
        "first_appeared": "Paragraph 3",
        "is_defined": false
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
    from .promptStore import prompt_undefined_terms
except ImportError:
    from promptStore import prompt_undefined_terms

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)


def check_undefined_terms(context: Dict[str, Any], content: str) -> Dict[str, Any]:
    """
    Phân tích văn bản để tìm các thuật ngữ chưa được định nghĩa
    
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
            "total_terms_found": int,
            "total_undefined": int,
            "undefined_terms": [
                {
                    "term": str,
                    "first_appeared": str,
                    "context_snippet": str,
                    "is_defined": bool,
                    "reason": str
                }
            ],
            "defined_terms": [
                {
                    "term": str,
                    "first_appeared": str,
                    "context_snippet": str,
                    "is_defined": bool,
                    "definition_found": str
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
        "total_terms_found": 0,
        "total_undefined": 0,
        "undefined_terms": [],
        "defined_terms": [],
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
        prompt = prompt_undefined_terms(context, content)
        
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
        if "undefined_terms" not in llm_result:
            llm_result["undefined_terms"] = []
        if "defined_terms" not in llm_result:
            llm_result["defined_terms"] = []
        if "total_terms_found" not in llm_result:
            llm_result["total_terms_found"] = len(llm_result["undefined_terms"]) + len(llm_result.get("defined_terms", []))
        
        # Update result with LLM response
        result["success"] = True
        result["total_terms_found"] = llm_result.get("total_terms_found", 0)
        result["total_undefined"] = len(llm_result["undefined_terms"])
        result["undefined_terms"] = llm_result["undefined_terms"]
        result["defined_terms"] = llm_result.get("defined_terms", [])
        
    except json.JSONDecodeError as e:
        result["metadata"]["error"] = f"Failed to parse LLM response as JSON: {str(e)}"
        print(f"JSON Parse Error: {e}")
        print(f"Response text: {response_text[:500]}...")  # Print first 500 chars for debugging
        
    except Exception as e:
        result["metadata"]["error"] = f"Error during analysis: {str(e)}"
        print(f"Error: {e}")
    
    return result