"""Saved job HTTP routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from job_platform.api.deps import DbSession
from job_platform.repositories.saved_job import SavedJobRepository
from job_platform.schemas.job import JobRead

logger = logging.getLogger(__name__)
router = APIRouter(tags=["saved-jobs"])

# TODO: Replace with real user ID extracted from JWT (see backend/auth server).
# All users currently share the same saved-job list. This is non-production.
_MOCK_USER_ID = "guest"


@router.post("/jobs/{job_id}/save", status_code=status.HTTP_201_CREATED)
async def save_job(job_id: str, session: DbSession) -> dict[str, str]:
    """Save a job for the current user."""
    repo = SavedJobRepository(session)

    # Check if job exists
    from job_platform.repositories.job import JobRepository
    job_repo = JobRepository(session)
    job = await job_repo.get_job_by_id(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check if already saved
    already_saved = await repo.is_job_saved(user_id=_MOCK_USER_ID, job_id=job_id)
    if already_saved:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job already saved"
        )

    # Save the job
    await repo.save_job(user_id=_MOCK_USER_ID, job_id=job_id)

    logger.info("job_saved", user_id=_MOCK_USER_ID, job_id=job_id)
    return {"message": "Job saved successfully"}


@router.delete("/jobs/{job_id}/save", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_job(job_id: str, session: DbSession):
    """Remove a saved job for the current user."""
    repo = SavedJobRepository(session)

    # Check if job exists
    from job_platform.repositories.job import JobRepository
    job_repo = JobRepository(session)
    job = await job_repo.get_job_by_id(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Remove the saved job
    removed = await repo.unsave_job(user_id=_MOCK_USER_ID, job_id=job_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not saved"
        )

    logger.info("job_unsaved", user_id=_MOCK_USER_ID, job_id=job_id)


@router.get("/saved-jobs", response_model=list[JobRead])
async def get_saved_jobs(session: DbSession) -> list[JobRead]:
    """Get all saved jobs for the current user."""
    repo = SavedJobRepository(session)

    saved_jobs = await repo.get_saved_jobs(user_id=_MOCK_USER_ID)

    # Convert to JobRead format
    jobs = []
    for saved_job in saved_jobs:
        if saved_job.job:
            job_read = JobRead.model_validate(saved_job.job)
            jobs.append(job_read)

    logger.debug(f"Retrieved {len(jobs)} saved jobs for user {_MOCK_USER_ID}")
    return jobs