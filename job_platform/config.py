"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings sourced from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = Field(..., description="Async SQLAlchemy / asyncpg database URL.")
    redis_url: str = Field(..., description="Redis connection URL for async clients.")
    environment: str = Field(default="development", description="Deployment environment name.")
    log_level: str = Field(
        default="INFO",
        description="Root logging level (e.g. DEBUG, INFO, WARNING).",
    )
    json_logs: bool = Field(
        default=False,
        description="When true, emit structlog as JSON; otherwise colored console output.",
    )

    @property
    def is_production(self) -> bool:
        """Return True when running in a production-like environment."""
        return self.environment.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (suitable for dependency injection)."""
    return Settings()
