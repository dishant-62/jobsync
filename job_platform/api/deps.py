"""FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from job_platform.db.session import get_db_session
from job_platform.repositories.job import JobRepository

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_job_repository(session: DbSession) -> JobRepository:
    return JobRepository(session)


JobRepositoryDep = Annotated[JobRepository, Depends(get_job_repository)]
