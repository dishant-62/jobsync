"""Job-related request/response models."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyRead(BaseModel):
    """Company information in job responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class JobRead(BaseModel):
    """Serialized job for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    company: CompanyRead
    title: str
    location: str
    description: str
    apply_url: str  # Changed from HttpUrl to str for better compatibility
    posted_date: date
    created_at: datetime
    skills: list[str] | None = None
    experience_level: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    is_remote: bool = False


class JobListResponse(BaseModel):
    """Paginated job search results."""

    jobs: list[JobRead]
    total: int = Field(..., ge=0, description="Total rows matching filters (ignoring limit/offset).")
