"""Domain models for job entities."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, HttpUrl, Field


class RawJob(BaseModel):
    """
    Standardized job representation across all crawlers.

    This model ensures consistent schema regardless of source (Greenhouse, Lever, Workday, etc.).
    All crawlers must output this unified format.
    """

    title: str = Field(..., min_length=1, description="Job title")
    company: str = Field(..., min_length=1, description="Company name")
    location: str | None = Field(None, description="Job location (optional)")
    description: str = Field("", description="Job description (HTML cleaned)")
    apply_url: HttpUrl = Field(..., description="URL to apply for the job")
    posted_date: datetime | None = Field(None, description="When the job was posted (optional)")
    source: str = Field(..., min_length=1, description="Source crawler (greenhouse, lever, workday, etc.)")

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def to_dict(self) -> dict[str, str | datetime | None]:
        """Convert to dictionary for database operations."""
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location or "",
            "description": self.description,
            "apply_url": str(self.apply_url),
            "posted_date": self.posted_date,
            "source": self.source,
        }