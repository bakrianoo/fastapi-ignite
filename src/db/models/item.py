"""
Example Item model
"""
from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TableNameMixin, TimestampMixin, UUIDMixin


class Item(Base, UUIDMixin, TableNameMixin, TimestampMixin):
    """
    Example Item model that demonstrates SQLAlchemy features
    """
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    def __repr__(self) -> str:
        return f"<Item {self.name}>"
