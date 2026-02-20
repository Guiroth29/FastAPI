"""SQLAlchemy ORM models."""

from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, DateTime, Integer, String, Text, Uuid

from app.database import Base


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class Book(Base):
    """Book table used by the API."""

    __tablename__ = "books"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    isbn = Column(String(20), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    pages = Column(Integer, nullable=True)
    published_year = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title={self.title!r}, author={self.author!r})>"
