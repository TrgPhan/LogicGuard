"""
term_normalizer.py

Spell & Term Normalization (safe + lightweight)
----------------------------------------------
Mục tiêu:
- Không thay đổi mạnh văn bản
- Chỉ chuẩn hóa nhẹ
- Xuất ra cấu trúc NormalizationResult mà Analysis.py yêu cầu:
    * spelling_corrections
    * term_mappings
    * normalized_text
    * original_text
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any
import re


@dataclass
class NormalizationResult:
    """
    Chuẩn hóa văn bản mức nhẹ.
    """
    original_text: str
    normalized_text: str

    # 2 field cần cho Analysis.py
    spelling_corrections: List[Dict[str, Any]]
    term_mappings: List[Dict[str, Any]]

    # field dùng để debug / hiển thị lịch sử thay thế
    mappings: List[Dict[str, Any]]


# ====== BASIC REPLACEMENTS ======
# Có thể mở rộng dần theo nhu cầu thực tế.
# EN: lỗi chính tả / ghép từ tiếng Anh
BASIC_REPLACEMENTS_EN: Dict[str, str] = {
    # Deep learning / AI
    "deeplearnnig": "deep learning",
    "deep learnnig": "deep learning",
    "maching learning": "machine learning",
    "artifical inteligence": "artificial intelligence",
    "aritificial inteligence": "artificial intelligence",
    "Aritificial Inteligence": "Artificial Intelligence",

    # Vector database / embeddings
    "vector databaes": "vector database",
    "databaes": "database",
    "embeding": "embedding",
    "emebding": "embedding",

    # Thương hiệu / từ phổ biến
    "samsungg": "Samsung",
}

# VI: lỗi chính tả / dấu tiếng Việt
BASIC_REPLACEMENTS_VI: Dict[str, str] = {
    "trí tuệ nhân tạoo": "trí tuệ nhân tạo",
    "tri tue nhan tao": "trí tuệ nhân tạo",
    "cong nghe": "công nghệ",
    "khoa hoc du lieu": "khoa học dữ liệu",
}


def _apply_basic_replacements(text: str, replacements: Dict[str, str]) -> NormalizationResult:
    """
    Áp dụng rule thay thế cơ bản trên chuỗi `text`.
    Trả về NormalizationResult với:
      - normalized_text: text sau khi thay
      - spelling_corrections / term_mappings / mappings: log các thay thế.
    """
    original_text = text
    normalized_text = text

    spelling_corrections: List[Dict[str, Any]] = []
    term_mappings: List[Dict[str, Any]] = []
    mappings: List[Dict[str, Any]] = []

    for wrong, correct in replacements.items():
        # regex ignore-case, tìm vị trí để báo về FE
        for m in re.finditer(re.escape(wrong), original_text, flags=re.IGNORECASE):
            start = m.start()
            end = m.end()

            record = {
                "original": original_text[start:end],
                "normalized": correct,
                "start_pos": start,
                "end_pos": end,
                "reason": "basic_replacement",
            }

            # Ở bản MVP: coi tất cả là spelling correction.
            spelling_corrections.append(record)
            # Nếu sau này muốn tách term_mappings riêng thì chỉnh lại chỗ này.
            term_mappings.append(record)
            mappings.append(record)

        # Thực hiện thay trong normalized_text (case-sensitive để đơn giản)
        normalized_text = normalized_text.replace(wrong, correct)

    return NormalizationResult(
        original_text=original_text,
        normalized_text=normalized_text,
        spelling_corrections=spelling_corrections,
        term_mappings=term_mappings,
        mappings=mappings,
    )


def normalize_text(text: str, language: str = "vi") -> NormalizationResult:
    """
    Hàm gọi chính — dùng trong Analysis.py

    - Không can thiệp mạnh vào văn bản người dùng.
    - Chủ yếu dùng để:
        + Gợi ý các lỗi chính tả / từ sai phổ biến (EN + VI)
        + Log lại vị trí thay thế để FE có thể highlight nếu muốn.
    """
    if not text:
        return NormalizationResult(
            original_text="",
            normalized_text="",
            spelling_corrections=[],
            term_mappings=[],
            mappings=[],
        )

    # 1) Chuẩn hóa xuống dòng & space (nhẹ)
    original_text = text
    working = text.strip()
    # Gộp nhiều whitespace thành 1 space để việc match dễ hơn
    working = re.sub(r"\s+", " ", working)

    # 2) Chọn bộ replacements
    # Hiện tại: dùng chung cả EN + VI cho mọi language,
    # vì bài viết thường trộn tiếng Việt + thuật ngữ tiếng Anh.
    # Sau này nếu muốn tách riêng theo language thì chỉnh ở đây.
    all_replacements: Dict[str, str] = {}
    all_replacements.update(BASIC_REPLACEMENTS_EN)
    all_replacements.update(BASIC_REPLACEMENTS_VI)

    basic = _apply_basic_replacements(working, all_replacements)

    # 3) Trả về kết quả, nhưng giữ original_text thật (nguyên văn user nhập)
    return NormalizationResult(
        original_text=original_text,
        normalized_text=basic.normalized_text,
        spelling_corrections=basic.spelling_corrections,
        term_mappings=basic.term_mappings,
        mappings=basic.mappings,
    )
