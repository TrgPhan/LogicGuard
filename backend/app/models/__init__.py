"""
SQLAlchemy models package
"""
from app.models.user import User
from app.models.goal import Goal, WritingType, RubricCriterion, CriterionCoverage
from app.models.document import Document, DocumentSection, Paragraph, Sentence
from app.models.analysis import AnalysisRun, WritingSession
from app.models.error import LogicError
from app.models.feedback import Feedback, UserErrorPattern

__all__ = [
    "User",
    "Goal",
    "WritingType",
    "RubricCriterion",
    "CriterionCoverage",
    "Document",
    "DocumentSection",
    "Paragraph",
    "Sentence",
    "AnalysisRun",
    "WritingSession",
    "LogicError",
    "Feedback",
    "UserErrorPattern",
]
