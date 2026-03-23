"""Job persistence operations."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import ColumnElement, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from job_platform.db.models import Job


def _job_search_conditions(
    q: str | None,
    location: str | None,
) -> ColumnElement[bool] | None:
    """Build WHERE fragments for text search (used with pg_trgm-backed GIN indexes)."""
    conditions: list[ColumnElement[bool]] = []
    if q is not None and q.strip():
        pattern = f"%{q.strip()}%"
        conditions.append(or_(Job.title.ilike(pattern), Job.description.ilike(pattern)))
    if location is not None and location.strip():
        loc_pattern = f"%{location.strip()}%"
        conditions.append(Job.location.ilike(loc_pattern))
    if not conditions:
        return None
    return and_(*conditions)


class JobRepository:
    """Async repository for ``Job`` entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_job(
        self,
        *,
        company_id: uuid.UUID,
        title: str,
        location: str,
        description: str,
        apply_url: str,
        posted_date: date,
        skills: list[str] | None = None,
        experience_level: str | None = None,
        salary_min: int | None = None,
        salary_max: int | None = None,
        is_remote: bool = False,
    ) -> Job:
        job = Job(
            company_id=company_id,
            title=title,
            location=location,
            description=description,
            apply_url=apply_url,
            posted_date=posted_date,
            skills=skills,
            experience_level=experience_level,
            salary_min=salary_min,
            salary_max=salary_max,
            is_remote=is_remote,
        )
        self._session.add(job)
        await self._session.flush()
        await self._session.refresh(job)
        return job

    async def get_job_by_url(self, apply_url: str) -> Job | None:
        result = await self._session.execute(select(Job).where(Job.apply_url == apply_url))
        return result.scalar_one_or_none()

    async def get_job_by_id(self, job_id: uuid.UUID) -> Job | None:
        result = await self._session.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def count_jobs(self, *, q: str | None, location: str | None) -> int:
        stmt = select(func.count()).select_from(Job)
        where_clause = _job_search_conditions(q, location)
        if where_clause is not None:
            stmt = stmt.where(where_clause)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def search_jobs(
        self,
        *,
        q: str | None,
        location: str | None,
        limit: int,
        offset: int,
    ) -> list[Job]:
        stmt = select(Job)
        where_clause = _job_search_conditions(q, location)
        if where_clause is not None:
            stmt = stmt.where(where_clause)
        stmt = stmt.order_by(Job.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_jobs(self) -> Sequence[Job]:
        result = await self._session.execute(select(Job).order_by(Job.created_at.desc()))
        return result.scalars().all()
