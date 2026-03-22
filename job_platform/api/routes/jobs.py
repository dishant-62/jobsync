"""Job HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter

from job_platform.api.deps import JobRepositoryDep
from job_platform.schemas.job import JobRead

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=list[JobRead])
async def list_jobs(repo: JobRepositoryDep) -> list[JobRead]:
    """Return all jobs, newest first."""
    jobs = await repo.list_jobs()
    return [JobRead.model_validate(j) for j in jobs]
