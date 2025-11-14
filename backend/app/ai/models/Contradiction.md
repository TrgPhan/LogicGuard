# Hướng dẫn sử dụng Contradiction Detection (Optimized Version)

## 🚀 Cách sử dụng

### 1️⃣ **Cơ bản - Single Text**

```python
from app.ai.models.contradictions import check_contradictions

text = """
Minh nói chưa bao giờ rời khỏi Việt Nam.
Anh kể lần đầu đến Nhật Bản là năm 2019.
"""

result = check_contradictions(
    text=text,
    mode="finetuned"  # hoặc "base"
)

if result['success']:
    print(f"Tìm thấy {result['total_contradictions']} mâu thuẫn")
    for c in result['contradictions']:
        print(f"- {c['sentence1']}")
        print(f"- {c['sentence2']}")
        print(f"  Confidence: {c['confidence']:.2%}\n")
```


### 2️⃣ **Tối ưu - Multiple Texts**

```python
from app.ai.models.contradictions import check_contradictions, clear_model_cache

texts = [
    "Text 1...",
    "Text 2...",
    "Text 3...",
]

# Process nhiều texts - model chỉ load 1 lần
for text in texts:
    result = check_contradictions(text, mode="finetuned")
    # Xử lý result...

# Clear cache khi xong
clear_model_cache()
```

**Performance:**
- Text 1: ~10s (load models)
- Text 2: ~2s (cached)
- Text 3: ~2s (cached)
- **Speedup: 5x faster!** 

---

### 3️⃣ **Production - API Endpoint**

```python
# app/routers/analysis.py
from fastapi import APIRouter
from app.ai.models.contradictions import check_contradictions

router = APIRouter()

@router.post("/analyze")
async def analyze_text(text: str, mode: str = "finetuned"):
    """
    API endpoint - model cached across requests
    Mỗi request chỉ mất ~1-3s thay vì ~10-15s
    """
    result = check_contradictions(text, mode=mode)
    return result
```

**Lợi ích:**
- Request đầu: ~10s (load models 1 lần)
- Các request sau: ~1-3s (dùng cache)
- Không cần restart server
- Auto memory management

---

### 4️⃣ **Advanced - Custom Parameters**

```python
result = check_contradictions(
    text=text,
    mode="finetuned",           # "base" | "finetuned"
    threshold=0.75,              # Ngưỡng confidence (0.0-1.0)
    use_embeddings_filter=True,  # Lọc cặp câu bằng embedding
    top_k=50,                    # Số cặp tối đa cho mỗi câu
    sim_min=0.30,                # Độ tương đồng tối thiểu
    sim_max=0.98,                # Độ tương đồng tối đa
    batch_size=8,                # Kích thước batch
    max_length=128,              # Độ dài tối đa của câu
)
```

---

## 🔧 Quản lý Cache

### Clear cache thủ công

```python
from app.ai.models.contradictions import clear_model_cache

# Xóa toàn bộ cached models
clear_model_cache()
```

**Khi nào cần clear?**
- ✅ Khi đổi mode (base ↔ finetuned) nhiều lần
- ✅ Khi hết dùng và muốn giải phóng RAM/GPU
- ✅ Khi chạy batch job xong
- ❌ Không cần clear giữa các requests (API sẽ tự quản lý)

### Auto memory management

Code tự động kiểm tra và clear cache khi:
- GPU memory usage > 80%
- Tránh OOM (Out of Memory)

---

## 📊 Response Format

```json
{
  "success": true,
  "mode": "finetuned",
  "model_path": "duowng/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7-for-vietnamese",
  "text": "...",
  "total_sentences": 10,
  "sentences": ["Câu 1", "Câu 2", ...],
  "total_contradictions": 5,
  "contradictions": [
    {
      "id": 1,
      "sentence1_index": 0,
      "sentence2_index": 1,
      "sentence1": "Câu mâu thuẫn thứ nhất",
      "sentence2": "Câu mâu thuẫn thứ hai",
      "confidence": 0.9523,
      "boosted": false
    }
  ],
  "metadata": {
    "analyzed_at": "2025-10-27T10:30:00",
    "threshold": 0.75,
    "error": null
  }
}
```

---

## 💡 Best Practices

### ✅ DO

```python
# 1. Tái sử dụng function cho nhiều texts
for text in texts:
    result = check_contradictions(text, mode="finetuned")

# 2. Clear cache sau khi xong batch
clear_model_cache()

# 3. Dùng mode="finetuned" cho tiếng Việt
result = check_contradictions(text, mode="finetuned")
```

### ❌ DON'T

```python
# 1. Đừng clear cache giữa các requests
result1 = check_contradictions(text1)
clear_model_cache()  # ❌ Sai - làm chậm request tiếp theo
result2 = check_contradictions(text2)

# 2. Đừng load lại model mỗi lần
# Code cũ:
model = load_model()  # ❌ Chậm
result = analyze(text, model)

# Code mới:
result = check_contradictions(text)  # ✅ Nhanh (cached)
```

---

## 🎯 Performance Comparison

| Scenario | Before (No Cache) | After (With Cache) | Speedup |
|----------|-------------------|-------------------|---------|
| Single text | ~10-15s | ~10-15s | 1x |
| 10 texts | ~100-150s | ~25-35s | **4-5x** ⚡ |
| API (100 req) | ~1000-1500s | ~150-250s | **5-7x** 🚀 |

---

## 🐛 Troubleshooting

### Model không load?
```python
# Check Hugging Face connection
from transformers import AutoModel
model = AutoModel.from_pretrained("duowng/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7-for-vietnamese")
```

### Out of Memory?
```python
# Clear cache thủ công
from app.ai.models.contradictions import clear_model_cache
clear_model_cache()
```

### Code chạy chậm?
- Lần đầu: Bình thường (~10-15s load models)
- Lần sau vẫn chậm: Check xem có clear cache giữa chừng không?

---

## 📞 Support

- Documentation: `Contradiction.md`
- Test script: `aiTest.py`
- Optimized example: `testOptimized.py`

---

**Version:** 2.0 (Optimized with Caching)  
**Last Updated:** 2025-10-27
