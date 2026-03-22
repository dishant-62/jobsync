"""Job HTTP routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from job_platform.api.deps import JobRepositoryDep
from job_platform.schemas.job import JobListResponse, JobRead

router = APIRouter(tags=["jobs"])

_DEFAULT_LIMIT = 20
_MAX_LIMIT = 100


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    repo: JobRepositoryDep,
    q: str | None = Query(
        default=None,
        description="Search in title and description (case-insensitive, substring).",
    ),
    location: str | None = Query(
        default=None,
        description="Filter by location (case-insensitive, substring).",
    ),
    limit: int = Query(default=_DEFAULT_LIMIT, ge=1, le=_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
) -> JobListResponse:
    """List jobs with optional text search and pagination."""
    total = await repo.count_jobs(q=q, location=location)
    rows = await repo.search_jobs(q=q, location=location, limit=limit, offset=offset)
    return JobListResponse(
        jobs=[JobRead.model_validate(j) for j in rows],
        total=total,
    )


@router.get("/jobs/{job_id}", response_model=JobRead)
async def get_job(job_id: uuid.UUID, repo: JobRepositoryDep) -> JobRead:
    """Return a single job by id."""
    job = await repo.get_job_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobRead.model_validate(job)
