"""Job HTTP routes."""

from __future__ import annotations

import uuid
import logging

from fastapi import APIRouter, HTTPException, Query, status

from job_platform.api.deps import JobRepositoryDep
from job_platform.schemas.job import JobListResponse, JobRead

logger = logging.getLogger(__name__)
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
    experience_level: str | None = Query(
        default=None,
        description="Filter by experience level (e.g., 'Entry Level', 'Mid Level', 'Senior').",
    ),
    is_remote: bool | None = Query(
        default=None,
        description="Filter for remote jobs only.",
    ),
    skills: str | None = Query(
        default=None,
        description="Comma-separated list of skills (filtering coming soon).",
    ),
    limit: int = Query(default=_DEFAULT_LIMIT, ge=1, le=_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
) -> JobListResponse:
    """List jobs with optional text search, filters, and pagination."""
    try:
        # Note: Skills filtering is accepted but not yet implemented
        # (requires PostgreSQL JSON operators or schema restructuring)
        
        total = await repo.count_jobs(
            q=q,
            location=location,
            experience_level=experience_level,
            is_remote=is_remote,
            skills=None,  # Skills filtering disabled for now
        )
        rows = await repo.search_jobs(
            q=q,
            location=location,
            experience_level=experience_level,
            is_remote=is_remote,
            skills=None,  # Skills filtering disabled for now
            limit=limit,
            offset=offset,
        )
        
        logger.debug(f"Retrieved {len(rows)} jobs from database")
        
        # Convert ORM models to Pydantic models
        jobs = []
        for job_orm in rows:
            try:
                job_schema = JobRead.model_validate(job_orm)
                jobs.append(job_schema)
            except Exception as e:
                logger.error(f"Failed to validate job {job_orm.id}: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to serialize job: {str(e)}"
                )
        
        return JobListResponse(jobs=jobs, total=total)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list_jobs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=JobRead)
async def get_job(job_id: uuid.UUID, repo: JobRepositoryDep) -> JobRead:
    """Return a single job by id."""
    job = await repo.get_job_by_id(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobRead.model_validate(job)
