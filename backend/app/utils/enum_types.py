"""
Custom SQLAlchemy types for enum handling
Ensures enum values (not names) are stored in database
"""
from sqlalchemy import TypeDecorator, Text
import enum


class EnumValueType(TypeDecorator):
    """Custom type that ensures enum values (not names) are stored"""
    impl = Text
    cache_ok = True
    
    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, enum.Enum):
            return value.value
        if isinstance(value, str):
            # Validate it's a valid enum value
            valid_values = [e.value for e in self.enum_class]
            if value in valid_values:
                return value
            # If it's an enum name, convert to value
            try:
                enum_member = self.enum_class[value]
                return enum_member.value
            except KeyError:
                return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return self.enum_class(value)
        except ValueError:
            return value

