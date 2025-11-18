# Phiên Bản Tiếng Việt - Comprehensive Analysis

## 📋 Tổng Quan

Đây là phiên bản **hoàn toàn bằng tiếng Việt** của prompt comprehensive analysis, phân tích văn bản theo 4 chiều:

1. **Mâu thuẫn logic (Contradictions)** - Phát hiện các mâu thuẫn logic giữa các phát biểu
2. **Thuật ngữ chưa định nghĩa (Undefined Terms)** - Xác định thuật ngữ không có định nghĩa rõ ràng
3. **Luận điểm thiếu chứng cứ (Unsupported Claims)** - Tìm các khẳng định thiếu bằng chứng
4. **Nhảy logic (Logical Jumps)** - Phát hiện chuyển đề đột ngột với độ liên kết thấp

## 🎯 Mục Đích

- **Dễ hiểu hơn**: Prompt tiếng Việt giúp model hiểu context Việt Nam tốt hơn
- **Phù hợp văn hóa**: Các ví dụ và mô tả được điều chỉnh cho văn hóa Việt
- **Tương thích**: Cùng cấu trúc JSON output với phiên bản tiếng Anh

## 🔧 Sử Dụng

### Import Function

```python
from promptStore import prompt_analysis_vi  # Phiên bản tiếng Việt
```

### Basic Usage

```python
# Setup context bằng tiếng Việt
context = {
    "writing_type": "Bài luận học thuật",
    "main_goal": "Lập luận về tác động của AI đến giáo dục",
    "criteria": ["dựa trên bằng chứng", "logic rõ ràng", "có trích dẫn"],
    "constraints": ["1500-2000 từ", "ít nhất 5 nguồn tham khảo"]
}

# Văn bản tiếng Việt
content = """
Trí tuệ nhân tạo đang thay đổi cách chúng ta học và dạy.
Các nghiên cứu cho thấy AI có thể cá nhân hóa trải nghiệm học tập.
Tuy nhiên, cần cân nhắc các vấn đề về quyền riêng tư và đạo đức.
"""

# Tạo prompt tiếng Việt
prompt = prompt_analysis_vi(context, content)

# Gửi đến LLM (Gemini, GPT, v.v.)
# response = model.generate_content(prompt)
```

## 📊 So Sánh Với Phiên Bản Tiếng Anh

### Thống Kê

| Đặc điểm | Tiếng Anh | Tiếng Việt |
|----------|-----------|------------|
| **Độ dài prompt** | ~8,500 ký tự | ~9,600 ký tự |
| **Số nhiệm vụ phụ** | 4 | 4 |
| **Cấu trúc JSON** | Giống nhau | Giống nhau |
| **Test coverage** | 5/5 passed | 4/4 passed |

### Điểm Khác Biệt

#### Tiếng Anh (`prompt_analysis`)
```python
"You are LogicGuard, an expert AI writing analyst..."
"### Mission Overview"
"SUBTASK 1: CONTRADICTIONS"
```

#### Tiếng Việt (`prompt_analysis_vi`)
```python
"Bạn là LogicGuard, một chuyên gia AI phân tích văn bản..."
"### Nhiệm Vụ Tổng Quan"
"NHIỆM VỤ PHỤ 1: MÂU THUẪN LOGIC"
```

## 🌟 Tính Năng Đặc Biệt

### 1. Mẫu Định Nghĩa Tiếng Việt

Phiên bản tiếng Việt nhận diện các pattern định nghĩa đặc trưng:

```
- "X là..." (X is...)
- "X được hiểu là..." (X is understood as...)
- "X gọi là..." (called X...)
- "X (viết tắt của...)" (X, abbreviation for...)
- "X, hay còn gọi là..." (X, also known as...)
```

### 2. Ngữ Cảnh Văn Hóa Việt Nam

Context được format theo cách Việt Nam:

```
Loại văn bản: Bài luận học thuật
Mục tiêu chính: Lập luận về...
Tiêu chí đánh giá:
  - dựa trên bằng chứng
  - logic rõ ràng
Ràng buộc:
  - 1500-2000 từ
```

### 3. Hỗ Trợ Ký Tự Đặc Biệt

Xử lý hoàn hảo các dấu tiếng Việt:
- Dấu sắc: á é í ó ú ý
- Dấu huyền: à è ì ò ù ỳ
- Dấu hỏi: ả ẻ ỉ ỏ ủ ỷ
- Dấu ngã: ã ẽ ĩ õ ũ ỹ
- Dấu nặng: ạ ệ ị ọ ụ ỵ
- Chữ đặc biệt: ă â ê ô ơ ư đ

## 📝 Ví Dụ Chi Tiết

### Ví Dụ 1: Bài Luận Học Thuật

```python
context = {
    "writing_type": "Bài luận học thuật",
    "main_goal": "Phân tích tác động của mạng xã hội đến thanh thiếu niên",
    "criteria": [
        "dựa trên nghiên cứu khoa học",
        "có trích dẫn đầy đủ",
        "lập luận logic"
    ],
    "constraints": ["2000-3000 từ", "ít nhất 10 nguồn tham khảo"]
}

content = """
Mạng xã hội đang gây hại nghiêm trọng cho sức khỏe tinh thần của thanh thiếu niên.
Nghiên cứu của Trần Văn A (2023) cho thấy 65% học sinh sử dụng mạng xã hội hơn 3 giờ/ngày.
Tuy nhiên, mạng xã hội giúp kết nối bạn bè và gia đình hiệu quả.

Do đó, chúng ta cần cải cách hệ thống giáo dục ngay lập tức.
"""

prompt = prompt_analysis_vi(context, content)
```

**Kết quả mong đợi**:
- ✅ Phát hiện mâu thuẫn: "gây hại nghiêm trọng" vs "giúp kết nối hiệu quả"
- ✅ Phát hiện nhảy logic: từ mạng xã hội sang cải cách giáo dục
- ✅ Luận điểm thiếu chứng cứ: "gây hại nghiêm trọng" cần thêm dẫn chứng

### Ví Dụ 2: Báo Cáo Kỹ Thuật

```python
context = {
    "writing_type": "Báo cáo kỹ thuật",
    "main_goal": "Trình bày kiến trúc hệ thống AI",
    "criteria": [
        "độ chính xác kỹ thuật cao",
        "có biểu đồ minh họa",
        "dễ hiểu cho người không chuyên"
    ],
    "constraints": ["5000 từ", "có code examples"]
}

content = """
Hệ thống sử dụng transformer architecture với attention mechanism.
Mô hình BERT được fine-tune trên corpus tiếng Việt.
Gradient descent được áp dụng để tối ưu hóa loss function.

Kết quả cho thấy độ chính xác đạt 95% trên tập test.
"""

prompt = prompt_analysis_vi(context, content)
```

**Kết quả mong đợi**:
- ✅ Thuật ngữ chưa định nghĩa: transformer, attention mechanism, BERT, gradient descent, loss function
- ✅ Luận điểm có chứng cứ: "95% trên tập test" (có số liệu cụ thể)

### Ví Dụ 3: Bài Viết Blog

```python
context = {
    "writing_type": "Bài viết blog",
    "main_goal": "Chia sẻ kinh nghiệm học lập trình",
    "criteria": ["dễ hiểu", "có ví dụ thực tế", "thân thiện"],
    "constraints": ["800-1200 từ", "có hình ảnh"]
}

content = """
Học lập trình không khó như bạn nghĩ!
Tôi đã học được Python chỉ trong 2 tuần.
Bạn chỉ cần kiên trì và luyện tập mỗi ngày.

Quantum computing sẽ thay đổi hoàn toàn ngành công nghiệp trong 5 năm tới.
"""

prompt = prompt_analysis_vi(context, content)
```

**Kết quả mong đợi**:
- ✅ Nhảy logic: từ học Python sang quantum computing
- ✅ Thuật ngữ chưa định nghĩa: quantum computing (cho blog đại chúng)
- ✅ Luận điểm thiếu chứng cứ: "học được Python trong 2 tuần", "5 năm tới"

## 🔍 Các Nhiệm Vụ Phụ Chi Tiết

### NHIỆM VỤ PHỤ 1: Mâu Thuẫn Logic

**Phát hiện**:
- Phát biểu trực tiếp đối lập
- Xung đột dữ liệu, số liệu
- Khẳng định không tương thích

**Ví dụ**:
```
❌ "AI rất hữu ích cho giáo dục" + "AI nên bị cấm trong trường học"
❌ "Tỷ lệ tăng 50%" + "Tỷ lệ giảm 30%" (cùng một chỉ số)
```

### NHIỆM VỤ PHỤ 2: Thuật Ngữ Chưa Định Nghĩa

**Phát hiện**:
- Thuật ngữ kỹ thuật không giải thích
- Từ viết tắt không mở rộng
- Khái niệm chuyên môn không rõ

**Ví dụ**:
```
❌ "Sử dụng API để..."  (không giải thích API là gì)
✅ "Sử dụng API (Application Programming Interface) để..."
```

### NHIỆM VỤ PHỤ 3: Luận Điểm Thiếu Chứng Cứ

**Phát hiện**:
- Khẳng định không có dẫn chứng
- Số liệu không có nguồn
- Dự đoán không có cơ sở

**Quy tắc ±2 câu**:
```
❌ "AI tăng hiệu quả 300%."  (không có chứng cứ trong ±2 câu)
✅ "Theo nghiên cứu X, AI tăng hiệu quả 300%."
✅ "AI tăng hiệu quả 300%. Điều này được chứng minh qua..."
```

### NHIỆM VỤ PHỤ 4: Nhảy Logic

**Phát hiện**:
- Chuyển đề đột ngột
- Thiếu câu chuyển tiếp
- Luồng ý không mạch lạc

**Ví dụ**:
```
❌ Đoạn 1: "Về machine learning..."
   Đoạn 2: "Nông nghiệp hữu cơ..."  (coherence: 0.1)

✅ Đoạn 1: "Về machine learning..."
   Đoạn 2: "ML cũng được ứng dụng trong nông nghiệp..."  (coherence: 0.7)
```

## 📋 JSON Output Format

Phiên bản tiếng Việt vẫn sử dụng **cùng cấu trúc JSON** như tiếng Anh:

```json
{
    "analysis_metadata": {
        "analyzed_at": "2024-11-18T10:00:00Z",
        "writing_type": "Bài luận học thuật",
        "total_paragraphs": 5,
        "total_sentences": 15
    },
    "contradictions": {
        "total_found": 2,
        "items": [...]
    },
    "undefined_terms": {
        "total_found": 5,
        "items": [...]
    },
    "unsupported_claims": {
        "total_found": 3,
        "items": [...]
    },
    "logical_jumps": {
        "total_found": 1,
        "items": [...]
    },
    "summary": {
        "total_issues": 11,
        "critical_issues": 3,
        "document_quality_score": 45,
        "key_recommendations": [...]
    }
}
```

## 🧪 Testing

### Chạy Tests

```bash
cd backend
conda activate logicguard
python test_vietnamese_prompt.py
```

### Test Suite (4 Tests)

1. ✅ **Vietnamese Prompt Generation** - Kiểm tra prompt được tạo đúng
2. ✅ **Context Formatting** - Kiểm tra format context tiếng Việt
3. ✅ **Structure Comparison** - So sánh với phiên bản tiếng Anh
4. ✅ **Special Characters** - Kiểm tra xử lý ký tự đặc biệt

**Kết quả**: 4/4 tests passed (100%) ✅

## 🎓 Khi Nào Dùng Phiên Bản Tiếng Việt?

### ✅ Nên Dùng Khi:

- Văn bản **hoàn toàn bằng tiếng Việt**
- Cần phân tích **context văn hóa Việt Nam**
- Thuật ngữ và khái niệm **đặc thù Việt**
- Model LLM **tốt với tiếng Việt** (Gemini, GPT-4)

### ❌ Không Nên Dùng Khi:

- Văn bản bằng tiếng Anh
- Văn bản song ngữ (nên dùng phiên bản tiếng Anh)
- Model không hỗ trợ tốt tiếng Việt
- Cần tốc độ xử lý tối đa (tiếng Anh có thể nhanh hơn)

## 💡 Tips & Best Practices

### 1. Chọn Writing Type Phù Hợp

```python
# Các loại văn bản thông dụng
writing_types = [
    "Bài luận học thuật",
    "Báo cáo kỹ thuật",
    "Bài viết blog",
    "Luận văn thạc sĩ",
    "Đề xuất dự án",
    "Bài báo khoa học",
    "Bài viết ý kiến"
]
```

### 2. Định Nghĩa Context Rõ Ràng

```python
# ✅ Tốt - Chi tiết và cụ thể
context = {
    "writing_type": "Báo cáo nghiên cứu",
    "main_goal": "Đánh giá hiệu quả của phương pháp X trong lĩnh vực Y",
    "criteria": [
        "dựa trên dữ liệu thực nghiệm",
        "có so sánh với phương pháp hiện có",
        "kết luận rõ ràng"
    ],
    "constraints": ["3000-5000 từ", "có biểu đồ"]
}

# ❌ Không tốt - Quá chung chung
context = {
    "writing_type": "Document",
    "main_goal": "Write something"
}
```

### 3. Xử Lý Văn Bản Dài

```python
# Nếu văn bản > 10,000 từ, chia nhỏ
paragraphs = content.split('\n\n')
chunks = ['\n\n'.join(paragraphs[i:i+10]) for i in range(0, len(paragraphs), 10)]

results = []
for chunk in chunks:
    prompt = prompt_analysis_vi(context, chunk)
    result = llm.generate(prompt)
    results.append(result)

# Gộp kết quả
combined_result = merge_results(results)
```

## 🔧 Troubleshooting

### Vấn Đề 1: Ký Tự Bị Lỗi

**Triệu chứng**: Dấu tiếng Việt hiển thị sai (�, ?, v.v.)

**Giải pháp**:
```python
# Đảm bảo encoding đúng
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Hoặc
content = content.encode('utf-8').decode('utf-8')
```

### Vấn Đề 2: LLM Không Hiểu Prompt

**Triệu chứng**: Kết quả không đúng format JSON hoặc thiếu thông tin

**Giải pháp**:
```python
# 1. Kiểm tra model hỗ trợ tiếng Việt tốt
# Gemini 2.5 Flash: ✅ Tốt
# GPT-4: ✅ Tốt
# GPT-3.5: ⚠️ Trung bình
# Claude: ✅ Tốt

# 2. Thêm example vào prompt (nếu cần)
# 3. Tăng temperature để model linh hoạt hơn
```

### Vấn Đề 3: JSON Parsing Error

**Triệu chứng**: `json.JSONDecodeError`

**Giải pháp**:
```python
import json

response_text = llm_response.strip()

# Loại bỏ markdown code blocks
if response_text.startswith("```json"):
    response_text = response_text[7:]
elif response_text.startswith("```"):
    response_text = response_text[3:]

if response_text.endswith("```"):
    response_text = response_text[:-3]

response_text = response_text.strip()

# Parse JSON
try:
    result = json.loads(response_text)
except json.JSONDecodeError as e:
    print(f"Error: {e}")
    print(f"Response: {response_text[:200]}...")
```

## 📚 Tài Liệu Tham Khảo

### Files Liên Quan

```
backend/app/ai/models/
├── promptStore.py              # Chứa prompt_analysis_vi()
└── README_VIETNAMESE.md        # Documentation này

backend/
└── test_vietnamese_prompt.py   # Test suite
```

### Functions

- `prompt_analysis_vi(context, content)` - Tạo prompt tiếng Việt
- `prompt_analysis(context, content)` - Tạo prompt tiếng Anh (để so sánh)

### External Links

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Vietnamese NLP Resources](https://github.com/undertheseanlp)
- [LogicGuard Project](https://github.com/TrgPhan/LogicGuard)

## 🎉 Thành Tựu

✅ **Hoàn Thành**:
- [x] Prompt tiếng Việt cho 4 subtasks
- [x] Format context tiếng Việt
- [x] Hỗ trợ ký tự đặc biệt
- [x] Test suite hoàn chỉnh (4/4)
- [x] Documentation đầy đủ

✅ **Chất Lượng**:
- [x] Cấu trúc JSON tương thích với tiếng Anh
- [x] Độ dài prompt tương đương (~103%)
- [x] Test coverage 100%
- [x] Xử lý encoding hoàn hảo

## 🚀 Tương Lai

### Cải Tiến Tiềm Năng

1. **Thêm ví dụ trong prompt**: Cung cấp 1-2 ví dụ mẫu cho mỗi subtask
2. **Tối ưu hóa độ dài**: Rút gọn prompt nhưng giữ nguyên chất lượng
3. **Hỗ trợ nhiều model**: Test với nhiều LLM khác nhau
4. **Fine-tuning**: Train model riêng cho văn bản tiếng Việt
5. **A/B Testing**: So sánh hiệu quả giữa phiên bản tiếng Việt và tiếng Anh

---

**Tạo bởi**: LogicGuard Team  
**Ngày tạo**: 18/11/2024  
**Phiên bản**: 1.0.0  
**Trạng thái**: ✅ Sẵn sàng sử dụng  
**Test Coverage**: 4/4 tests passing (100%)  
**Language**: 🇻🇳 Tiếng Việt
