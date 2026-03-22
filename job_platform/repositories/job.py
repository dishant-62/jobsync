"""Job persistence operations."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from job_platform.db.models import Job


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
    ) -> Job:
        job = Job(
            company_id=company_id,
            title=title,
            location=location,
            description=description,
            apply_url=apply_url,
            posted_date=posted_date,
        )
        self._session.add(job)
        await self._session.flush()
        await self._session.refresh(job)
        return job

    async def get_job_by_url(self, apply_url: str) -> Job | None:
        result = await self._session.execute(select(Job).where(Job.apply_url == apply_url))
        return result.scalar_one_or_none()

    async def list_jobs(self) -> Sequence[Job]:
        result = await self._session.execute(select(Job).order_by(Job.created_at.desc()))
        return result.scalars().all()
