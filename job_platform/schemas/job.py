"""Job-related request/response models."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class JobRead(BaseModel):
    """Serialized job for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    title: str
    location: str
    description: str
    apply_url: HttpUrl
    posted_date: date
    created_at: datetime


class JobListResponse(BaseModel):
    """Paginated job search results."""

    jobs: list[JobRead]
    total: int = Field(..., ge=0, description="Total rows matching filters (ignoring limit/offset).")
