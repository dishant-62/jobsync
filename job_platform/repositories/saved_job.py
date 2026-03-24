"""Saved job persistence operations."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from job_platform.db.models import SavedJob


class SavedJobRepository:
    """Async repository for ``SavedJob`` entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_job(self, *, user_id: str, job_id: str) -> SavedJob:
        """Save a job for a user. Returns the saved job record."""
        saved_job = SavedJob(
            user_id=user_id,
            job_id=job_id,
        )
        self._session.add(saved_job)
        await self._session.flush()
        await self._session.refresh(saved_job)
        return saved_job

    async def unsave_job(self, *, user_id: str, job_id: str) -> bool:
        """Remove a saved job for a user. Returns True if a job was removed."""
        stmt = delete(SavedJob).where(
            SavedJob.user_id == user_id,
            SavedJob.job_id == job_id
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def is_job_saved(self, *, user_id: str, job_id: str) -> bool:
        """Check if a job is saved by a user."""
        stmt = select(SavedJob).where(
            SavedJob.user_id == user_id,
            SavedJob.job_id == job_id
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_saved_jobs(self, *, user_id: str) -> Sequence[SavedJob]:
        """Get all saved jobs for a user, with job details eagerly loaded."""
        stmt = select(SavedJob).options(
            selectinload(SavedJob.job).selectinload("company")
        ).where(
            SavedJob.user_id == user_id
        ).order_by(SavedJob.created_at.desc())

        result = await self._session.execute(stmt)
        return result.scalars().all()