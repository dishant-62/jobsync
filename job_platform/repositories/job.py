"""Job persistence operations."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import ColumnElement, and_, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from job_platform.db.models import Job


def _job_search_conditions(
    q: str | None,
    location: str | None,
    experience_level: str | None,
    is_remote: bool | None,
    skills: list[str] | None,
) -> ColumnElement[bool] | None:
    """Build WHERE fragments for text search and filtering."""
    conditions: list[ColumnElement[bool]] = []
    if q is not None and q.strip():
        pattern = f"%{q.strip()}%"
        conditions.append(or_(Job.title.ilike(pattern), Job.description.ilike(pattern)))
    if location is not None and location.strip():
        loc_pattern = f"%{location.strip()}%"
        conditions.append(Job.location.ilike(loc_pattern))
    if experience_level is not None and experience_level.strip():
        conditions.append(Job.experience_level.ilike(experience_level.strip()))
    if is_remote is True:
        conditions.append(Job.is_remote == True)
    
    # Note: Skills filtering is disabled for now due to JSON array complexity
    # To enable: implement PostgreSQL JSON operators or denormalize skills data
    # if skills and len(skills) > 0:
    #     # Would require: Job.skills.op('&&')(skills) for PostgreSQL overlap operator
    #     pass
    
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

    async def upsert_job(
        self,
        *,
        job_id: str,
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
        score: float = 0.0,
    ) -> tuple[Job, bool]:
        """Upsert a job by job_id. Returns (job, created) where created is True if inserted, False if updated."""
        # Check if job exists before upsert
        existing = await self.get_job_by_id(job_id)
        was_created = existing is None
        
        # Use PostgreSQL ON CONFLICT to upsert
        stmt = insert(Job).values(
            job_id=job_id,
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
            score=score,
        ).on_conflict_do_update(
            index_elements=["job_id"],
            set_={
                "title": title,
                "location": location,
                "description": description,
                "apply_url": apply_url,
                "posted_date": posted_date,
                "skills": skills,
                "experience_level": experience_level,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "is_remote": is_remote,
                "score": score,
            }
        ).returning(Job)

        result = await self._session.execute(stmt)
        job = result.scalar_one()
        return job, was_created

    async def get_job_by_url(self, apply_url: str) -> Job | None:
        result = await self._session.execute(select(Job).where(Job.apply_url == apply_url))
        return result.scalar_one_or_none()

    async def get_job_by_id(self, job_id: str | uuid.UUID) -> Job | None:
        """Get job by either job_id (SHA256 hash string) or UUID id."""
        # Eagerly load company to avoid lazy-load MissingGreenlet errors
        if isinstance(job_id, uuid.UUID):
            stmt = select(Job).options(selectinload(Job.company)).where(Job.id == job_id)
        elif len(job_id) == 64:
            # 64-char hex → SHA256 job_id
            stmt = select(Job).options(selectinload(Job.company)).where(Job.job_id == job_id)
        else:
            # Attempt UUID parse (e.g. 36-char UUID string from frontend)
            try:
                uid = uuid.UUID(job_id)
                stmt = select(Job).options(selectinload(Job.company)).where(Job.id == uid)
            except ValueError:
                # Not a valid UUID – try as job_id string anyway
                stmt = select(Job).options(selectinload(Job.company)).where(Job.job_id == job_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_jobs(
        self,
        *,
        q: str | None,
        location: str | None,
        experience_level: str | None = None,
        is_remote: bool | None = None,
        skills: list[str] | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Job)
        where_clause = _job_search_conditions(q, location, experience_level, is_remote, skills)
        if where_clause is not None:
            stmt = stmt.where(where_clause)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())

    async def search_jobs(
        self,
        *,
        q: str | None,
        location: str | None,
        experience_level: str | None = None,
        is_remote: bool | None = None,
        skills: list[str] | None = None,
        limit: int,
        offset: int,
    ) -> list[Job]:
        stmt = select(Job)
        # Eagerly load company relationship to avoid lazy loading issues
        stmt = stmt.options(selectinload(Job.company))
        where_clause = _job_search_conditions(q, location, experience_level, is_remote, skills)
        if where_clause is not None:
            stmt = stmt.where(where_clause)
        stmt = stmt.order_by(Job.score.desc(), Job.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_jobs(self) -> Sequence[Job]:
        result = await self._session.execute(select(Job).order_by(Job.score.desc(), Job.created_at.desc()))
        return result.scalars().all()
