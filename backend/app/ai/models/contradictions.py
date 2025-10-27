from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import re, numpy as np, itertools, torch, gc
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
from app.utils.nlp import extract_sentences


# Model paths
BASE_MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
FINETUNED_MODEL = "duowng/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7-for-vietnamese"

# Global cache cho models
_cached_embedding_model = None
_cached_embedding_model_name = None
_cached_nli_model = None
_cached_nli_tokenizer = None
_cached_nli_model_path = None
_cached_nli_device = None
_cached_contra_idx = None


def clear_model_cache():
    """Xóa toàn bộ cache models để giải phóng bộ nhớ"""
    global _cached_embedding_model, _cached_embedding_model_name
    global _cached_nli_model, _cached_nli_tokenizer, _cached_nli_model_path
    global _cached_nli_device, _cached_contra_idx
    
    _cached_embedding_model = None
    _cached_embedding_model_name = None
    _cached_nli_model = None
    _cached_nli_tokenizer = None
    _cached_nli_model_path = None
    _cached_nli_device = None
    _cached_contra_idx = None
    
    # Force garbage collection
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    print("Model cache cleared")


def _check_memory_and_clear_if_needed():
    """Kiểm tra bộ nhớ GPU và tự động clear cache nếu cần"""
    if torch.cuda.is_available():
        # Lấy memory usage
        allocated = torch.cuda.memory_allocated() / 1024**3  # GB
        reserved = torch.cuda.memory_reserved() / 1024**3    # GB
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
        
        usage_percent = (allocated / total) * 100
        
        # Nếu usage > 80%, clear cache
        if usage_percent > 80:
            print(f"GPU memory usage: {usage_percent:.1f}% - Clearing cache...")
            torch.cuda.empty_cache()
            gc.collect()


def _load_embedding_model(model_name: str) -> SentenceTransformer:
    """Cache và load embedding model"""
    global _cached_embedding_model, _cached_embedding_model_name
    
    if _cached_embedding_model_name != model_name:
        print(f"Loading embedding model: {model_name}")
        _cached_embedding_model = SentenceTransformer(model_name, device="cpu")
        _cached_embedding_model.eval()
        _cached_embedding_model_name = model_name
    
    return _cached_embedding_model


def _load_nli_model(model_path: str, device: Optional[str] = None):
    """Cache và load NLI model + tokenizer"""
    global _cached_nli_model, _cached_nli_tokenizer, _cached_nli_model_path
    global _cached_nli_device, _cached_contra_idx
    
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Nếu model đã load và đúng path + device → return cache
    if (_cached_nli_model_path == model_path and 
        _cached_nli_device == device and
        _cached_nli_model is not None):
        return _cached_nli_tokenizer, _cached_nli_model, _cached_contra_idx, device
    
    # Check memory trước khi load model mới
    _check_memory_and_clear_if_needed()
    
    print(f"📦 Loading NLI model: {model_path} on {device}")
    
    # Load model mới
    _cached_nli_tokenizer = AutoTokenizer.from_pretrained(model_path)
    _cached_nli_model = AutoModelForSequenceClassification.from_pretrained(model_path)
    _cached_nli_model.eval()
    _cached_nli_model.to(device)
    
    # Lưu metadata
    _cached_nli_model_path = model_path
    _cached_nli_device = device
    _cached_contra_idx = _get_contradiction_idx_from_config(_cached_nli_model)
    
    return _cached_nli_tokenizer, _cached_nli_model, _cached_contra_idx, device


def _get_contradiction_idx_from_config(model) -> int:
    """Lấy index của label 'contradiction' từ model config"""
    if hasattr(model, "config") and hasattr(model.config, "id2label"):
        mapping = {int(k): v.lower() for k, v in model.config.id2label.items()}
        for idx, lab in mapping.items():
            if "contradiction" in lab:
                return int(idx)
    return 0


def _contains_number_or_time_conflict(text1: str, text2: str) -> bool:
    """Kiểm tra xung đột về số liệu hoặc thời gian"""
    nums1 = set(re.findall(r"\b\d+(?:[.,]\d+)?\b", text1))
    nums2 = set(re.findall(r"\b\d+(?:[.,]\d+)?\b", text2))

    date_patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # dd/mm/yyyy
        r"\b\d{1,2}[/-]\d{1,2}\b",             # dd/mm
        r"\b\d{1,2}:\d{2}(?::\d{2})?\b",       # HH:MM:SS
        r"\bQ[1-4]\b",                          # Quarters
        r"\b(?:20)?\d{2}\b"                     # Năm
    ]
    
    def grab_dates(t: str):
        s = set()
        for p in date_patterns:
            s.update(re.findall(p, t))
        return s

    dates1, dates2 = grab_dates(text1), grab_dates(text2)
    has_both_nums = bool(nums1) and bool(nums2)
    has_both_dates = bool(dates1) and bool(dates2)
    return has_both_nums or has_both_dates


def _model_supports_amp(model) -> bool:
    """Kiểm tra model có hỗ trợ AMP không"""
    name = getattr(model, "name_or_path", "").lower()
    if "mdeberta" in name:
        return False
    return True


def check_contradictions(
    text: str,
    mode: str = "finetuned",
    threshold: float = 0.75,
    use_embeddings_filter: bool = True,
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    top_k: int = 50,
    sim_min: float = 0.30,
    sim_max: float = 0.98,
    batch_size: int = 8,
    max_length: int = 128,
) -> Dict[str, Any]:
    """
    Phân tích mâu thuẫn trong văn bản với 2 chế độ model
    
    Args:
        text: Đoạn văn bản cần phân tích
        mode: Chế độ sử dụng model
            - "base": Sử dụng base model (MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7)
            - "finetuned": Sử dụng fine-tuned model (từ Hugging Face)
        threshold: Ngưỡng confidence để coi là contradiction (0.0-1.0)
        use_embeddings_filter: Có dùng embedding để lọc cặp câu không
        embedding_model_name: Tên model embedding
        top_k: Số lượng cặp tối đa cho mỗi câu
        sim_min: Độ tương đồng tối thiểu
        sim_max: Độ tương đồng tối đa
        batch_size: Kích thước batch
        max_length: Độ dài tối đa của câu
        
    Returns:
        Dict[str, Any]: Kết quả phân tích
        {
            "success": bool,
            "mode": str,
            "model_path": str,
            "text": str,
            "total_sentences": int,
            "sentences": List[str],
            "total_contradictions": int,
            "contradictions": [...],
            "metadata": {
                "analyzed_at": str,
                "threshold": float,
                "error": Optional[str]
            }
        }
    """
    
    # Validate mode
    if mode not in ["base", "finetuned"]:
        return {
            "success": False,
            "error": f"Mode '{mode}' không hợp lệ. Chỉ chấp nhận 'base' hoặc 'finetuned'.",
            "mode": mode,
            "text": text
        }
    
    result = {
        "success": False,
        "mode": mode,
        "model_path": None,
        "text": text,
        "total_sentences": 0,
        "sentences": [],
        "total_contradictions": 0,
        "contradictions": [],
        "metadata": {
            "analyzed_at": datetime.utcnow().isoformat(),
            "threshold": threshold,
            "error": None
        }
    }
    
    try:
        # Bước 1: Tách câu
        sentences = extract_sentences(text)
        result["sentences"] = sentences
        result["total_sentences"] = len(sentences)
        if len(sentences) < 2:
            result["success"] = True
            result["metadata"]["error"] = "Cần ít nhất 2 câu để phân tích"
            print("\nCần ít nhất 2 câu để phân tích mâu thuẫn")
            return result
        
        # Bước 2: Chọn và load NLI model (cached)
        model_path = FINETUNED_MODEL if mode == "finetuned" else BASE_MODEL
        result["model_path"] = model_path
        
        tokenizer, model, contra_idx, device = _load_nli_model(model_path)
        
        # Bước 3: Lọc cặp câu bằng embedding (nếu bật)
        if use_embeddings_filter:
            embedding_model = _load_embedding_model(embedding_model_name)
            sentence_pairs = _filter_sentence_pairs_by_embedding(
                sentences, embedding_model, sim_min, sim_max, top_k
            )
        else:
            sentence_pairs = list(itertools.combinations(range(len(sentences)), 2))
        
        if not sentence_pairs:
            result["success"] = True
            return result
        
        # Bước 4: Phân tích NLI cho từng batch
        contradictions_list = _analyze_nli_batches(
            sentences, sentence_pairs, tokenizer, model, device,
            contra_idx, batch_size, max_length, threshold
        )
        
        # Bước 5: Loại bỏ trùng lặp và format kết quả
        final_contradictions = _deduplicate_and_format(contradictions_list)
        
        result["success"] = True
        result["total_contradictions"] = len(final_contradictions)
        result["contradictions"] = final_contradictions
        
        # Check memory sau khi xử lý
        _check_memory_and_clear_if_needed()
        
    except Exception as e:
        result["metadata"]["error"] = str(e)
        print(f"Error: {e}")
    
    return result


def _filter_sentence_pairs_by_embedding(
    sentences: List[str],
    embedding_model: SentenceTransformer,
    sim_min: float,
    sim_max: float,
    top_k: int
) -> List[Tuple[int, int]]:
    """Lọc cặp câu dựa trên embedding similarity"""
    with torch.no_grad():
        embs = embedding_model.encode(
            sentences, convert_to_tensor=True,
            normalize_embeddings=True,
            show_progress_bar=False, device="cpu"
        )
    
    sim = torch.matmul(embs, embs.T).cpu().numpy()
    np.fill_diagonal(sim, -1.0)
    
    sentence_pairs = []
    n = len(sentences)
    for i in range(n):
        idxs = [j for j in range(n) if sim_min <= sim[i, j] <= sim_max]
        if len(idxs) > top_k:
            idxs = sorted(idxs, key=lambda j: sim[i, j], reverse=True)[:top_k]
        for j in idxs:
            if j > i:
                sentence_pairs.append((i, j))
    
    return sentence_pairs


def _analyze_nli_batches(
    sentences: List[str],
    sentence_pairs: List[Tuple[int, int]],
    tokenizer,
    model,
    device: str,
    contra_idx: int,
    batch_size: int,
    max_length: int,
    threshold: float
) -> List[Dict[str, Any]]:
    """Phân tích NLI cho các batches của sentence pairs"""
    contradictions_list = []
    
    for b in range(0, len(sentence_pairs), batch_size):
        batch = sentence_pairs[b:b+batch_size]
        
        # A->B
        premises = [sentences[i] for (i, j) in batch]
        hyps = [sentences[j] for (i, j) in batch]
        inputs_f = tokenizer(premises, hyps, return_tensors="pt",
                            truncation=True, padding=True, max_length=max_length).to(device)
        # B->A
        premises_r = hyps
        hyps_r = premises
        inputs_b = tokenizer(premises_r, hyps_r, return_tensors="pt",
                            truncation=True, padding=True, max_length=max_length).to(device)
        
        with torch.no_grad():
            use_amp = (device == "cuda") and _model_supports_amp(model)
            if use_amp:
                with torch.amp.autocast('cuda'):
                    logits_f = model(**inputs_f).logits
                    logits_b = model(**inputs_b).logits
            else:
                logits_f = model(**inputs_f).logits
                logits_b = model(**inputs_b).logits
        
        probs_f = F.softmax(logits_f.float(), dim=-1).cpu().numpy()
        probs_b = F.softmax(logits_b.float(), dim=-1).cpu().numpy()
        
        for (i, (si, sj)) in enumerate(batch):
            p1 = float(probs_f[i, contra_idx])
            p2 = float(probs_b[i, contra_idx])
            
            # Boost nếu có xung đột số/thời gian
            boost = 0.05 if _contains_number_or_time_conflict(sentences[si], sentences[sj]) else 0.0
            conf1 = min(p1 + boost, 1.0)
            conf2 = min(p2 + boost, 1.0)
            conf = max(conf1, conf2)
            
            if conf >= threshold:
                direction = (si, sj) if conf1 >= conf2 else (sj, si)
                contradictions_list.append({
                    "sentence1_index": int(direction[0]),
                    "sentence2_index": int(direction[1]),
                    "sentence1": sentences[direction[0]],
                    "sentence2": sentences[direction[1]],
                    "confidence": round(conf, 4),
                    "boosted": boost > 0
                })
        
        # Clear GPU cache mỗi batch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    return contradictions_list


def _deduplicate_and_format(contradictions_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Loại bỏ trùng lặp và format kết quả"""
    dedup = {}
    for r in contradictions_list:
        a, b = r["sentence1_index"], r["sentence2_index"]
        key = (min(a, b), max(a, b))
        if key not in dedup or r["confidence"] > dedup[key]["confidence"]:
            dedup[key] = r
    
    final_contradictions = sorted(dedup.values(), key=lambda x: x["confidence"], reverse=True)
    for idx, contradiction in enumerate(final_contradictions):
        contradiction["id"] = idx + 1
    
    return final_contradictions
