# app/services/__init__.py

"""
Service layer exports.

Chỉ export các singleton/service class để chỗ khác import:
    from app.services import ai_analysis_service, llm_service
"""

from app.services.llm_service import llm_service
from app.services.ai_analysis_service import ai_analysis_service

# Nếu bạn có DocumentCanvasSyncService hay service khác,
# import thêm ở đây, ví dụ:
# from app.services.document_sync import DocumentCanvasSyncService

__all__ = [
    "llm_service",
    "ai_analysis_service",
    # "DocumentCanvasSyncService",
]
