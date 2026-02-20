"""Database engine and session management."""

from __future__ import annotations

import logging

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)

Base = declarative_base()

engine: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None


def init_db() -> None:
    """Initialize SQLAlchemy engine and session factory once."""
    global engine, SessionLocal

    settings = get_settings()
    db_url = settings.database_url

    engine_kwargs: dict = {
        "echo": settings.api_environment == "development",
    }

    # Pool settings are useful for PostgreSQL but not needed for SQLite tests.
    if not db_url.startswith("sqlite"):
        engine_kwargs.update(
            {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_timeout": 30,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            }
        )

    engine = create_engine(db_url, **engine_kwargs)

    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    logger.info("Database engine initialized")


def get_engine() -> Engine:
    """Return initialized engine."""
    if engine is None:
        init_db()
    return engine


def get_session() -> Session:
    """Return a new database session."""
    global SessionLocal
    if SessionLocal is None:
        init_db()

    if SessionLocal is None:
        raise RuntimeError("Session factory is not initialized")

    return SessionLocal()


def create_all_tables() -> None:
    """Create all tables based on ORM metadata."""
    Base.metadata.create_all(bind=get_engine())


def drop_all_tables() -> None:
    """Drop all tables (used in tests)."""
    Base.metadata.drop_all(bind=get_engine())


def check_db_connection() -> bool:
    """Run a lightweight query to confirm database connectivity."""
    session = None
    try:
        session = get_session()
        session.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Database connection check failed")
        return False
    finally:
        if session is not None:
            session.close()
