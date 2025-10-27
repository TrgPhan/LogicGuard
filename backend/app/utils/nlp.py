"""
Placeholder for NLP and logic analysis utilities
"""
import re


def extract_criteria_from_rubric(rubric_text: str) -> dict:
    """
    Extract criteria from rubric text using NLP
    TODO: Implement actual NLP extraction with spaCy or similar
    
    For now, this is a simple rule-based extraction:
    - Looks for numbered lists
    - Looks for bullet points
    - Extracts key phrases
    """
    criteria = []
    
    # Split by newlines and common separators
    lines = rubric_text.split('\n')
    
    # Pattern matching for numbered lists (1., 2., etc.) or bullets (-, *, •)
    pattern = r'^[\s]*(?:[\d]+\.|[-*•])\s*(.+)$'
    
    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        match = re.match(pattern, line)
        if match:
            criterion_text = match.group(1).strip()
            # Extract weight if mentioned (e.g., "30%" or "weight: 0.3")
            weight_match = re.search(r'(\d+)%|weight:\s*([\d.]+)', criterion_text, re.IGNORECASE)
            weight = float(weight_match.group(1) or weight_match.group(2)) / 100 if weight_match and weight_match.group(1) else (float(weight_match.group(2)) if weight_match and weight_match.group(2) else 1.0)
            
            # Check if marked as optional
            is_mandatory = 'optional' not in criterion_text.lower()
            
            criteria.append({
                "label": criterion_text[:100],  # Truncate label
                "description": criterion_text,
                "weight": weight,
                "is_mandatory": is_mandatory
            })
        elif len(line) > 20:  # Assume longer lines are criteria descriptions
            criteria.append({
                "label": line[:100],
                "description": line,
                "weight": 1.0,
                "is_mandatory": True
            })
    
    # If no criteria found, create a default one
    if not criteria:
        criteria.append({
            "label": "General Requirements",
            "description": rubric_text[:500],
            "weight": 1.0,
            "is_mandatory": True
        })
    
    return {
        "criteria": criteria,
        "total_criteria": len(criteria),
        "extraction_method": "rule_based"  # Will be 'nlp' when implemented
    }


def analyze_text_logic(text: str) -> dict:
    """
    Placeholder for logic analysis
    TODO: Implement actual NLP logic checking
    """
    return {
        "errors_found": 0,
        "suggestions": []
    }


def extract_paragraphs(text: str) -> list:
    """Extract paragraphs from text"""
    return [p.strip() for p in text.split('\n\n') if p.strip()]


def extract_sentences(text: str) -> list:
    """
    Extract sentences from text using improved sentence splitting
    Works better for Vietnamese and English text
    """
    import re
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Split by sentence endings: . ! ? followed by space and capital letter or quote
    # Also handles Vietnamese specific patterns
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"\'])', text)
    
    # Clean and filter
    result = []
    for s in sentences:
        s = s.strip()
        # Keep sentences with at least 3 words
        if s and len(s.split()) >= 3:
            # Remove trailing punctuation for consistency
            s = re.sub(r'[.!?]+$', '', s).strip()
            if s:
                result.append(s)
    
    return result


def calculate_word_count(text: str) -> int:
    """Calculate word count"""
    return len(text.split())
