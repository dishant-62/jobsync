"""Async SQLAlchemy engine and session factory."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from job_platform.config import get_settings

import logging as _logging

_settings = get_settings()
_db_logger = _logging.getLogger(__name__)

# Log the DB URL at module load (mask password for safety)
_masked_url = str(_settings.database_url)
if "@" in _masked_url:
    _prefix, _suffix = _masked_url.split("@", 1)
    _scheme_user = _prefix.rsplit(":", 1)[0]
    _masked_url = f"{_scheme_user}:****@{_suffix}"
_db_logger.info("DATABASE URL (masked): %s", _masked_url)
print(f"\n🔌 DATABASE URL: {_masked_url}\n")

engine: AsyncEngine = create_async_engine(
    _settings.database_url,
    pool_pre_ping=True,
)

session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    Yield an ``AsyncSession`` for the request and commit on success.

    Rolls back on exception. Suitable for FastAPI ``Depends``.
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
