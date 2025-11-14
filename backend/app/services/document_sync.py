from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional

from bs4 import BeautifulSoup, NavigableString, Tag
from sqlalchemy.orm import Session

from sqlalchemy import select

from app.models.document import Document, DocumentSection, Paragraph, Sentence, SectionType


class DocumentCanvasSyncService:
    """Normalize TipTap HTML into structured document entities."""

    SECTION_KEYWORDS = {
        "introduction": SectionType.INTRO.value,
        "intro": SectionType.INTRO.value,
        "background": SectionType.BODY.value,
        "body": SectionType.BODY.value,
        "analysis": SectionType.BODY.value,
        "discussion": SectionType.BODY.value,
        "results": SectionType.BODY.value,
        "conclusion": SectionType.CONCLUSION.value,
        "closing": SectionType.CONCLUSION.value,
        "summary": SectionType.CONCLUSION.value,
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def sync(self, document: Document, html_content: Optional[str]) -> None:
        """Synchronize DocumentSection/Paragraph/Sentence tables with canvas content."""
        normalized_html = (html_content or "").strip()
        sections = self._parse_sections(normalized_html)

        # Remove previous structure (respect FK constraints by deleting child sentences first)
        paragraph_subquery = select(Paragraph.id).where(Paragraph.document_id == document.id)
        self.db.query(Sentence).filter(Sentence.paragraph_id.in_(paragraph_subquery)).delete(synchronize_session=False)
        self.db.query(Paragraph).filter(Paragraph.document_id == document.id).delete(synchronize_session=False)
        self.db.query(DocumentSection).filter(DocumentSection.document_id == document.id).delete(synchronize_session=False)
        self.db.flush()

        total_word_count = 0
        summary: List[Dict[str, object]] = []
        paragraph_index = 0

        for order_index, section in enumerate(sections):
            section_model = DocumentSection(
                document_id=document.id,
                section_type=section["type"],
                section_label=section["label"],
                order_index=order_index,
            )
            self.db.add(section_model)
            self.db.flush()

            paragraph_ids: List[str] = []

            for paragraph in section["paragraphs"]:
                paragraph_index += 1
                para_model = Paragraph(
                    document_id=document.id,
                    section_id=section_model.id,
                    p_index=paragraph_index,
                    text=paragraph["html"],
                    hash=paragraph["hash"],
                    word_count=paragraph["word_count"],
                )
                self.db.add(para_model)
                self.db.flush()
                paragraph_ids.append(str(para_model.id))
                total_word_count += paragraph["word_count"]

                for s_index, sentence in enumerate(paragraph["sentences"]):
                    sent_model = Sentence(
                        paragraph_id=para_model.id,
                        s_index=s_index,
                        text=sentence["text"],
                        hash=sentence["hash"],
                        role=None,
                        confidence_score=None,
                    )
                    self.db.add(sent_model)

            summary.append(
                {
                    "section_id": str(section_model.id),
                    "label": section_model.section_label,
                    "type": section_model.section_type,
                    "paragraph_ids": paragraph_ids,
                }
            )

        document.word_count = total_word_count
        document.structure_json = {
            "sections": summary,
            "synchronized_at": datetime.utcnow().isoformat(),
        }

    # ---------------------------------------------------------------------
    # Parsing helpers
    # ---------------------------------------------------------------------
    def _parse_sections(self, html: str) -> List[Dict[str, object]]:
        soup = BeautifulSoup(html or "", "html.parser")
        container = soup.body or soup

        sections: List[Dict[str, object]] = []
        current_section = self._new_section("Main Section", SectionType.CUSTOM.value)
        sections.append(current_section)

        for node in container.children:
            if isinstance(node, NavigableString):
                text = node.strip()
                if not text:
                    continue
                current_section["paragraphs"].extend(self._paragraph_from_text(text))
                continue

            if not isinstance(node, Tag):
                continue

            if node.name in {"h1", "h2", "h3"}:
                label = node.get_text(" ", strip=True) or f"Section {len(sections)}"
                resolved_type = self._infer_section_type(label)
                current_section = self._new_section(label, resolved_type)
                sections.append(current_section)
                continue

            paragraphs = self._extract_paragraphs(node)
            if paragraphs:
                current_section["paragraphs"].extend(paragraphs)

        # Ensure each section has at least one placeholder paragraph
        for section in sections:
            if not section["paragraphs"]:
                section["paragraphs"].extend(self._paragraph_from_text(""))

        return sections

    def _extract_paragraphs(self, node: Tag) -> List[Dict[str, object]]:
        if node.name in {"p", "blockquote"}:
            return [self._build_paragraph_from_node(node)]

        if node.name in {"ul", "ol"}:
            list_type = "bullet" if node.name == "ul" else "ordered"
            paragraphs: List[Dict[str, object]] = []
            for li in node.find_all("li", recursive=False):
                paragraphs.append(self._build_paragraph_from_node(li, list_type=list_type))
            return paragraphs

        if node.name == "hr":
            return [self._build_paragraph_from_text("", html="<hr />", metadata={"divider": True})]

        if node.name in {"div", "section", "article"}:
            paragraphs: List[Dict[str, object]] = []
            for child in node.children:
                if isinstance(child, (Tag, NavigableString)):
                    paragraphs.extend(
                        self._extract_paragraphs(child) if isinstance(child, Tag) else self._paragraph_from_text(child)
                    )
            return paragraphs

        text = node.get_text(" ", strip=True)
        if text:
            return [self._build_paragraph_from_node(node)]

        return []

    def _build_paragraph_from_node(self, node: Tag, list_type: Optional[str] = None) -> Dict[str, object]:
        html_repr = self._node_to_html(node, list_type)
        plain_text = node.get_text(" ", strip=True)
        return self._build_paragraph_data(html_repr, plain_text)

    def _paragraph_from_text(self, text: NavigableString | str) -> List[Dict[str, object]]:
        return self._build_paragraph_from_text(str(text))

    def _build_paragraph_from_text(self, text: str, html: Optional[str] = None, metadata: Optional[Dict[str, object]] = None) -> List[Dict[str, object]]:
        html_repr = html or f"<p>{text}</p>"
        return [self._build_paragraph_data(html_repr, text, metadata=metadata)]

    def _build_paragraph_data(self, html_repr: str, plain_text: str, metadata: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        sentences = self._split_sentences(plain_text)
        sentence_payload = [
            {
                "text": sentence,
                "hash": hashlib.md5(sentence.encode("utf-8")).hexdigest(),
                "role": None,
            }
            for sentence in sentences
        ]
        payload: Dict[str, object] = {
            "html": html_repr,
            "plain_text": plain_text,
            "word_count": len(plain_text.split()) if plain_text else 0,
            "hash": hashlib.md5((plain_text or html_repr).encode("utf-8")).hexdigest(),
            "sentences": sentence_payload,
        }
        if metadata:
            payload["metadata"] = metadata
        return payload

    def _split_sentences(self, text: str) -> List[str]:
        clean = text.strip()
        if not clean:
            return []
        parts = re.split(r"(?<=[.!?])\s+", clean)
        return [part.strip() for part in parts if part.strip()]

    def _node_to_html(self, node: Tag, list_type: Optional[str]) -> str:
        if list_type:
            inner = node.decode_contents().strip()
            return f"<p data-list-type=\"{list_type}\">{inner}</p>"

        if node.name in {"p", "blockquote", "li"}:
            return str(node)

        inner_html = node.decode_contents().strip() or node.get_text(" ", strip=True)
        return f"<p>{inner_html}</p>"

    def _infer_section_type(self, label: str) -> str:
        normalized = label.lower()
        for keyword, section_value in self.SECTION_KEYWORDS.items():
            if keyword in normalized:
                return section_value
        return SectionType.CUSTOM.value

    def _new_section(self, label: str, section_type: str) -> Dict[str, object]:
        return {"label": label, "type": section_type, "paragraphs": []}


__all__ = ["DocumentCanvasSyncService"]
