"""
term_normalizer.py

Spell & Term Normalization (safe + lightweight)
----------------------------------------------
Mục tiêu:
- Không thay đổi mạnh văn bản người dùng
- Chỉ chuẩn hóa nhẹ, dựa trên một số pattern phổ biến
- Xuất ra NormalizationResult cho Analysis.py:
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
    Kết quả chuẩn hóa văn bản mức nhẹ.
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

# VI: lỗi chính tả / cụm sai thường gặp trong ngữ cảnh học thuật / logic
BASIC_REPLACEMENTS_VI: Dict[str, str] = {
    # AI / công nghệ
    "trí tuệ nhân tạoo": "trí tuệ nhân tạo",
    "tri tue nhan tao": "trí tuệ nhân tạo",
    "cong nghe": "công nghệ",
    "khoa hoc du lieu": "khoa học dữ liệu",

    # Các lỗi bạn đang test trong ví dụ logic
    "sức khẻ": "sức khỏe",
    "bằng trứng khoa học": "bằng chứng khoa học",
    "nướt tăng lực": "nước tăng lực",
    "nướt hồi sinh": "nước hồi sinh",
    "chồng cây": "trồng cây",
    "kích hoặt năng lượng não bộ": "kích hoạt năng lượng não bộ",
    "kích hoặt": "kích hoạt",
    "khởi hoạc luồng trí tuệ sâu": "khởi hoạt luồng trí tuệ sâu",
    "khởi hoạc": "khởi hoạt",
    "cơ thẻ": "cơ thể",
    "tái tạo trỉ": "tái tạo chỉ",
    "nghiên cứ": "nghiên cứu",
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

            # MVP: coi tất cả là spelling correction + term mapping
            spelling_corrections.append(record)
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

    - KHÔNG còn bóp méo whitespace để giữ vị trí (start_pos / end_pos)
      khớp với CHUỖI GỐC mà user gửi.
    - Chủ yếu dùng để:
        + Gợi ý các lỗi chính tả / cụm sai phổ biến (EN + VI)
        + Log lại vị trí để FE có thể highlight nếu muốn.
    """
    if not text:
        return NormalizationResult(
            original_text="",
            normalized_text="",
            spelling_corrections=[],
            term_mappings=[],
            mappings=[],
        )

    original_text = text

    # Không re.sub \s+ nữa để không lệch index
    working = text

    # Dùng chung cả EN + VI, vì văn bản thường trộn 2 thứ tiếng
    all_replacements: Dict[str, str] = {}
    all_replacements.update(BASIC_REPLACEMENTS_EN)
    all_replacements.update(BASIC_REPLACEMENTS_VI)

    basic = _apply_basic_replacements(working, all_replacements)

    # Trả về: original_text là đúng văn bản gốc, normalized_text là bản đã sửa nhẹ
    return NormalizationResult(
        original_text=original_text,
        normalized_text=basic.normalized_text,
        spelling_corrections=basic.spelling_corrections,
        term_mappings=basic.term_mappings,
        mappings=basic.mappings,
    )
