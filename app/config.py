"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration for API and database."""

    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "books_user"
    db_password: str = "books_password"
    db_name: str = "books_db"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_environment: Literal["development", "production"] = "development"

    # Allows running tests without Docker/PostgreSQL.
    use_sqlite_for_tests: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """Return the SQLAlchemy URL for the active database."""
        if self.use_sqlite_for_tests:
            return "sqlite:///./test.db"

        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def async_database_url(self) -> str:
        """Return async database URL (not used yet, but ready for future use)."""
        if self.use_sqlite_for_tests:
            return "sqlite+aiosqlite:///./test.db"

        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Create settings once and reuse them across the process."""
    return Settings()
