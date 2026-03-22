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


class ParsedJob(BaseModel):
    """
    Structured information extracted from job descriptions.

    Contains parsed fields like skills, experience level, salary range, and remote work status.
    """

    skills: list[str] = Field(default_factory=list, description="List of technical skills mentioned")
    experience_level: str | None = Field(None, description="Experience level (entry, mid, senior)")
    salary_min: int | None = Field(None, description="Minimum salary (in USD)")
    salary_max: int | None = Field(None, description="Maximum salary (in USD)")
    is_remote: bool = Field(False, description="Whether the job allows remote work")

    def to_dict(self) -> dict[str, list[str] | str | int | bool | None]:
        """Convert to dictionary for database operations."""
        return {
            "skills": self.skills,
            "experience_level": self.experience_level,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "is_remote": self.is_remote,
        }


class FinalJob(RawJob, ParsedJob):
    """
    Complete job representation combining raw data and parsed information.

    Inherits from both RawJob and ParsedJob to provide comprehensive job data.
    """

    pass