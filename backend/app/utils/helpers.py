"""
Helper utilities
"""
import hashlib


def generate_text_hash(text: str) -> str:
    """Generate a hash for text content"""
    return hashlib.sha256(text.encode()).hexdigest()


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate a string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
