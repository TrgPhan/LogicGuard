from pydantic import BaseModel, field_serializer
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class WritingTypeResponse(BaseModel):
    id: UUID
    name: str
    display_name: str
    description: Optional[str]
    default_checks: Dict[str, Any]
    structure_template: Dict[str, Any]

    @field_serializer('name')
    def serialize_name(self, value):
        # Convert enum to string value if needed
        return value.value if hasattr(value, 'value') else value

    class Config:
        from_attributes = True


class WritingTypeDetailResponse(BaseModel):
    id: UUID
    name: str
    display_name: str
    description: Optional[str]
    default_checks: Dict[str, Any]
    structure_template: Dict[str, Any]
    created_at: datetime

    @field_serializer('name')
    def serialize_name(self, value):
        # Convert enum to string value if needed
        return value.value if hasattr(value, 'value') else value

    class Config:
        from_attributes = True
