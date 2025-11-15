# Undefined Terms Detection Module

## Mô tả

Module này phát hiện các thuật ngữ chưa được định nghĩa trong văn bản bằng cách sử dụng Google Gemini AI.

## Cấu trúc

### 1. `promptStore.py` - Prompt Generation

Hàm `prompt_undefined_terms(context, content)` tạo prompt chi tiết cho Gemini API:

**Đầu vào:**
- `context`: Dictionary chứa thông tin ngữ cảnh
  - `writing_type`: Loại văn bản (Technical Proposal, Academic Essay, etc.)
  - `main_goal`: Mục tiêu chính của bài viết
  - `criteria`: Danh sách các tiêu chí đánh giá
  - `constraints`: Các ràng buộc (word_limit, etc.)
- `content`: Nội dung văn bản cần phân tích

**Đầu ra:**
- String prompt đầy đủ được tối ưu hóa cho Gemini AI

**Đặc điểm của prompt:**
- Hướng dẫn rõ ràng về các pattern định nghĩa cần tìm ("là", "được hiểu là", "gọi là", etc.)
- Yêu cầu phân tích từng thuật ngữ lần đầu xuất hiện
- Định dạng output là JSON có cấu trúc
- Bao gồm cả thuật ngữ đã định nghĩa và chưa định nghĩa để có tính minh bạch

### 2. `undefinedTerms.py` - Main Analysis Function

Hàm `check_undefined_terms(context, content)` thực hiện phân tích thực tế:

**Đầu vào:**
- `context`: Dictionary với cấu trúc như trên
- `content`: Nội dung văn bản

**Đầu ra:**
Dictionary với cấu trúc:
```python
{
    "success": bool,              # Trạng thái thành công
    "content": str,               # Nội dung gốc
    "context": dict,              # Context gốc
    "total_terms_found": int,     # Tổng số thuật ngữ tìm thấy
    "total_undefined": int,       # Số thuật ngữ chưa định nghĩa
    "undefined_terms": [          # Danh sách thuật ngữ chưa định nghĩa
        {
            "term": str,
            "first_appeared": str,
            "context_snippet": str,
            "is_defined": false,
            "reason": str
        }
    ],
    "defined_terms": [            # Danh sách thuật ngữ đã định nghĩa
        {
            "term": str,
            "first_appeared": str,
            "context_snippet": str,
            "is_defined": true,
            "definition_found": str
        }
    ],
    "metadata": {
        "analyzed_at": str,       # Timestamp ISO format
        "model": str,             # Tên model Gemini
        "error": str or None      # Thông báo lỗi nếu có
    }
}
```

## Sử dụng

### Ví dụ cơ bản:

```python
from app.ai.models.undefinedTerms import check_undefined_terms

# Chuẩn bị context
context = {
    "writing_type": "Technical Proposal",
    "main_goal": "Chứng minh NoSQL có khả năng mở rộng tốt hơn",
    "criteria": ["nhắc đến scalability", "có luận cứ kỹ thuật"],
    "constraints": ["word_limit: 1000"]
}

# Nội dung cần phân tích
content = """
Trong thế giới công nghệ hiện đại, NoSQL databases đang ngày càng phổ biến.
Gradient clipping là một kỹ thuật quan trọng trong machine learning.

Scalability, hay khả năng mở rộng, là khả năng của hệ thống xử lý 
khối lượng công việc ngày càng tăng.
"""

# Thực hiện phân tích
result = check_undefined_terms(context, content)

# Kiểm tra kết quả
if result["success"]:
    print(f"Tìm thấy {result['total_terms_found']} thuật ngữ")
    print(f"Trong đó {result['total_undefined']} thuật ngữ chưa được định nghĩa:")
    
    for term in result["undefined_terms"]:
        print(f"  - {term['term']}: {term['reason']}")
else:
    print(f"Lỗi: {result['metadata']['error']}")
```

## Cơ chế hoạt động

1. **Tạo Prompt**: Hàm `prompt_undefined_terms()` tạo prompt chi tiết với:
   - Ngữ cảnh từ `context`
   - Nội dung văn bản
   - Hướng dẫn về các pattern định nghĩa
   - Định dạng output mong muốn

2. **Gọi Gemini API**: Hàm `check_undefined_terms()`:
   - Validate đầu vào
   - Gọi `prompt_undefined_terms()` để tạo prompt
   - Khởi tạo Gemini model với API key từ `.env`
   - Gửi request đến Gemini API
   - Nhận và parse JSON response

3. **Xử lý Response**:
   - Loại bỏ markdown code blocks nếu có
   - Parse JSON
   - Validate cấu trúc
   - Trả về kết quả có cấu trúc

4. **Error Handling**:
   - Validate input
   - Try-catch cho JSON parsing
   - Try-catch cho API calls
   - Trả về thông báo lỗi chi tiết

## Lưu ý

### Về Pattern định nghĩa

Các pattern được nhận diện:
- "X là..."
- "X được hiểu là..."
- "X gọi là..."
- "X (viết tắt của...)"
- "X, hay còn gọi là..."
- Giải thích trong dấu ngoặc
- Ngữ cảnh làm rõ nghĩa

### Về độ chính xác

- Model có thể có false positives/negatives
- Phụ thuộc vào chất lượng của Gemini API
- Cân nhắc audience và level của văn bản
- Thuật ngữ phổ thông có thể không cần định nghĩa

### Performance

- API call đến Gemini có thể mất vài giây
- Rate limits của Gemini API (free tier)
- Nên cache results nếu phân tích lại cùng văn bản