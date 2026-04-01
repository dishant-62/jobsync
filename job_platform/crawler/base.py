"""Base crawler abstract class supporting both company and URL-based sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import httpx


class NormalizedJob:
    """
    Normalized job representation across all crawlers.
    
    This ensures consistent schema regardless of source.
    """

    def __init__(
        self,
        title: str,
        location: str,
        apply_url: str,
        description: str,
        posted_date: datetime,
        company_name: str,
    ):
        self.title = title
        self.location = location
        self.apply_url = apply_url
        self.description = description
        self.posted_date = posted_date
        self.company_name = company_name

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for database insertion."""
        return {
            "title": self.title,
            "location": self.location,
            "apply_url": self.apply_url,
            "description": self.description,
            "posted_date": self.posted_date,
            "company": self.company_name,
        }


class BaseCrawler(ABC):
    """
    Abstract base crawler supporting both:
    - Company-based sources (Greenhouse, Lever, Workday)
    - URL-based sources (Job boards, remote job aggregators)
    """

    def __init__(self, name: str, timeout: httpx.Timeout | None = None):
        """
        Initialize crawler.
        
        Args:
            name: Unique crawler identifier (e.g., "greenhouse", "lever")
            timeout: Optional custom timeout for HTTP requests
        """
        self.name = name
        self.timeout = timeout or httpx.Timeout(30.0, connect=10.0)

    async def fetch_jobs_from_company(
        self, company: str, client: httpx.AsyncClient
    ) -> list[NormalizedJob]:
        """
        Fetch jobs for a given company (ATS-based sources like Greenhouse, Lever).
        
        Args:
            company: Company identifier (board token, company domain, etc.)
            client: Async HTTP client
            
        Returns:
            List of normalized jobs
            
        Raises:
            NotImplementedError: If crawler doesn't support company-based fetching
        """
        raise NotImplementedError(f"{self.name} does not support company-based fetching")

    async def fetch_jobs_from_url(
        self, url: str, client: httpx.AsyncClient, **kwargs: Any
    ) -> list[NormalizedJob]:
        """
        Fetch jobs from a given URL (generic job boards, aggregators).
        
        Args:
            url: URL to fetch jobs from
            client: Async HTTP client
            **kwargs: Additional configuration (e.g., CSS selectors)
            
        Returns:
            List of normalized jobs
            
        Raises:
            NotImplementedError: If crawler doesn't support URL-based fetching
        """
        raise NotImplementedError(f"{self.name} does not support URL-based fetching")

    def _validate_normalized_job(self, job: NormalizedJob) -> bool:
        """
        Validate that a normalized job has all required fields.

        Returns:
            True if valid, False otherwise
        """
        return (
            isinstance(job.title, str)
            and job.title.strip()
            and isinstance(job.location, str)
            and isinstance(job.apply_url, str)
            and job.apply_url.strip()
            and isinstance(job.description, str)
            and isinstance(job.posted_date, datetime)
            and isinstance(job.company_name, str)
            and job.company_name.strip()
        )
