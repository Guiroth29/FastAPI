"""Pydantic schemas for request validation and response serialization."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    """Common book fields shared between create and response schemas."""

    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: str = Field(..., min_length=10, max_length=20)
    description: Optional[str] = None
    pages: Optional[int] = Field(None, ge=1)
    published_year: Optional[int] = None


class BookCreate(BookBase):
    """Payload for creating a book."""


class BookUpdate(BaseModel):
    """Payload for full/partial updates."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, min_length=10, max_length=20)
    description: Optional[str] = None
    pages: Optional[int] = Field(None, ge=1)
    published_year: Optional[int] = None


class BookResponse(BookBase):
    """Book payload returned by API."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")


class PaginatedBooksResponse(BaseModel):
    """Paginated book list response."""

    model_config = ConfigDict(populate_by_name=True)

    current_page: int = Field(..., ge=1, alias="currentPage")
    page_size: int = Field(..., ge=1, alias="pageSize")
    total_pages: int = Field(..., ge=0, alias="totalPages")
    total_records: int = Field(..., ge=0, alias="totalRecords")
    data: list[BookResponse] = Field(default_factory=list)


class HealthCheckResponse(BaseModel):
    """Health check response payload."""

    status: str
    database: str
