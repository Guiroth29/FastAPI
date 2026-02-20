"""Service layer for book business rules and persistence operations."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Book
from app.schemas import BookCreate, BookUpdate


class BookService:
    """Encapsulates database operations for books."""

    def __init__(self, db: Session):
        self.db = db

    def get_books(self, page: int = 1, page_size: int = 10) -> tuple[list[Book], int]:
        total = self.db.query(func.count(Book.id)).scalar() or 0
        offset = (page - 1) * page_size
        books = (
            self.db.query(Book)
            .order_by(desc(Book.created_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return books, total

    def get_book_by_id(self, book_id: UUID) -> Optional[Book]:
        return self.db.query(Book).filter(Book.id == book_id).first()

    def get_book_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.db.query(Book).filter(Book.isbn == isbn).first()

    def create_book(self, book_data: BookCreate) -> Book:
        if self.get_book_by_isbn(book_data.isbn):
            raise ValueError(f"Book with ISBN {book_data.isbn} already exists")

        db_book = Book(**book_data.model_dump())
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return db_book

    def update_book(self, book_id: UUID, book_data: BookUpdate) -> Optional[Book]:
        book = self.get_book_by_id(book_id)
        if not book:
            return None

        update_data = book_data.model_dump(exclude_unset=True)
        new_isbn = update_data.get("isbn")
        if new_isbn and new_isbn != book.isbn:
            existing = self.get_book_by_isbn(new_isbn)
            if existing and existing.id != book.id:
                raise ValueError(f"Book with ISBN {new_isbn} already exists")

        for field, value in update_data.items():
            setattr(book, field, value)

        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ValueError("Unable to update book due to database constraint") from exc

        self.db.refresh(book)
        return book

    def delete_book(self, book_id: UUID) -> bool:
        book = self.get_book_by_id(book_id)
        if not book:
            return False

        self.db.delete(book)
        self.db.commit()
        return True

    def search_books(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Book], int]:
        search_filter = (Book.title.ilike(f"%{query}%")) | (Book.author.ilike(f"%{query}%"))
        total = self.db.query(func.count(Book.id)).filter(search_filter).scalar() or 0
        offset = (page - 1) * page_size

        books = (
            self.db.query(Book)
            .filter(search_filter)
            .order_by(desc(Book.created_at))
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return books, total
