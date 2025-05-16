"""
Base SQLAlchemy models for the application
"""
import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Convention for constraint naming to avoid SQLAlchemy warnings
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    metadata = metadata
    
    # Common model serialization method
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dict"""
        result = {}
        for key in self.__mapper__.c.keys():
            value = getattr(self, key)
            # Handle UUID conversion
            if isinstance(value, uuid.UUID):
                value = str(value)
            # Handle datetime conversion
            elif isinstance(value, datetime):
                value = value.isoformat()
            result[key] = value
        return result


class TimestampMixin:
    """Mixin to add created_at and updated_at fields to models"""
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )


class UUIDMixin:
    """Mixin to add a UUID primary key to models"""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TableNameMixin:
    """Mixin to automatically generate table names"""
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
