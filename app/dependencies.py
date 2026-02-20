"""Dependency injection helpers."""

from typing import Generator

from sqlalchemy.orm import Session

from app.database import get_session as _get_db_session


def get_session() -> Generator[Session, None, None]:
    """Yield a request-scoped DB session and close it after request end."""
    db = _get_db_session()
    try:
        yield db
    finally:
        db.close()
