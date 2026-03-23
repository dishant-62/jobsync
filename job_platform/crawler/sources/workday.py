"""Workday ATS crawler for job boards."""

from __future__ import annotations

import asyncio
import re
from datetime import UTC, datetime
from typing import Any

import httpx

from job_platform.crawler.base import BaseCrawler, NormalizedJob

# Workday uses pattern: /careers-{company}/jobs/job/{id} or similar
# We'll need company's career URL as input
MAX_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 1.0


def _parse_posted_date(date_str: str | None) -> datetime:
    """Parse various date formats from Workday."""
    if not date_str:
        return datetime.now(tz=UTC)
    
    try:
        # Try ISO format
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except (ValueError, TypeError):
        return datetime.now(tz=UTC)


def _should_retry_status(status_code: int) -> bool:
    """Retry on transient errors."""
    if status_code == 429:
        return True
    return status_code >= 500


async def _get_json_with_retries(
    client: httpx.AsyncClient, url: str
) -> dict[str, Any]:
    """GET JSON with retries."""
    backoff = INITIAL_BACKOFF_SECONDS
    last_error: BaseException | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("API returned non-object JSON root")
            return payload
        except httpx.HTTPStatusError as exc:
            last_error = exc
            if not _should_retry_status(exc.response.status_code):
                raise
        except (httpx.TimeoutException, httpx.TransportError, httpx.RequestError) as exc:
            last_error = exc

        if attempt < MAX_ATTEMPTS - 1:
            await asyncio.sleep(backoff)
            backoff *= 2.0

    if last_error:
        raise last_error
    raise RuntimeError("Failed to fetch jobs after retries")


class WorkdayCrawler(BaseCrawler):
    """Crawler for Workday-hosted job boards."""

    def __init__(self):
        super().__init__("workday")

    async def fetch_jobs_from_company(
        self, company: str, client: httpx.AsyncClient
    ) -> list[NormalizedJob]:
        """
        Fetch jobs from Workday JSON API.
        
        Args:
            company: Company identifier or career page URL
            client: Async HTTP client
            
        Returns:
            List of normalized jobs
        """
        identifier = company.strip()
        if not identifier:
            raise ValueError("Company identifier must be non-empty")

        # Try to construct standard Workday API endpoint
        # Pattern: https://{company}.myworkdayjobs.com/en-US/
        if not identifier.startswith("http"):
            url = f"https://{identifier}.myworkdayjobs.com/en-US/SearchJobs"
        else:
            url = identifier

        try:
            payload = await _get_json_with_retries(client, url)
            jobs_raw = payload.get("jobPostings")
            if not isinstance(jobs_raw, list):
                return []

            normalized_jobs: list[NormalizedJob] = []
            for item in jobs_raw:
                if not isinstance(item, dict):
                    continue

                job = self._normalize_job(item, identifier)
                if job and self._validate_normalized_job(job):
                    normalized_jobs.append(job)

            return normalized_jobs
        except httpx.RequestError as e:
            # Log but don't fail - Workday APIs are complex
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch from Workday {identifier}: {e}")
            return []

    def _normalize_job(self, raw: dict[str, Any], company_name: str) -> NormalizedJob | None:
        """
        Normalize raw Workday job posting.
        
        Expected fields vary, but typically include:
        - title, description, jobPostingUrl
        - locationCity, locationCountry
        """
        title = raw.get("title") or raw.get("jobTitle")
        if not isinstance(title, str) or not title.strip():
            return None

        apply_url = raw.get("jobPostingUrl") or raw.get("externalJobPostingUrl")
        if not isinstance(apply_url, str) or not apply_url.strip():
            return None

        # Build location from city/state/country
        location_parts = []
        for key in ["locationCity", "locationState", "locationCountry"]:
            loc = raw.get(key)
            if isinstance(loc, str) and loc.strip():
                location_parts.append(loc.strip())
        location = ", ".join(location_parts)

        description = raw.get("description") or raw.get("jobDescription", "")
        if not isinstance(description, str):
            description = ""

        posted_date_str = raw.get("postedDate") or raw.get("datePosted")
        posted_date = _parse_posted_date(posted_date_str)

        return NormalizedJob(
            title=title.strip(),
            location=location,
            apply_url=apply_url.strip(),
            description=description,
            posted_date=posted_date,
            company_name=_extract_company_name(company_name),
        )


def _extract_company_name(identifier: str) -> str:
    """Extract company name from Workday identifier."""
    if identifier.startswith("http"):
        # Extract from URL
        match = re.search(r"https://([^.]+)", identifier)
        if match:
            return match.group(1).replace("-", " ").title()
        return "Unknown"
    return identifier.replace("-", " ").title()
