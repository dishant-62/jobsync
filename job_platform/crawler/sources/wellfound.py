"""Wellfound (formerly AngelList Talent) crawler for startup jobs."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

import httpx

from job_platform.crawler.base import BaseCrawler, NormalizedJob

WELLFOUND_API_URL = "https://api.wellfound.com/v1"
MAX_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 1.0


def _parse_posted_date(date_str: str | None) -> datetime:
    """Parse ISO 8601 timestamp."""
    if not date_str:
        return datetime.now(tz=UTC)

    try:
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
    client: httpx.AsyncClient,
    url: str,
    headers: dict[str, str] | None = None,
) -> dict[str, Any] | list[Any]:
    """GET JSON with retries."""
    backoff = INITIAL_BACKOFF_SECONDS
    last_error: BaseException | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            payload = response.json()
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


class WellfoundCrawler(BaseCrawler):
    """Crawler for Wellfound startup jobs."""

    def __init__(self, api_token: str | None = None):
        """
        Initialize Wellfound crawler.
        
        Args:
            api_token: Optional Wellfound API token for authenticated requests
        """
        super().__init__("wellfound")
        self.api_token = api_token

    async def fetch_jobs_from_url(
        self,
        url: str,
        client: httpx.AsyncClient,
        **kwargs: Any,
    ) -> list[NormalizedJob]:
        """
        Fetch startup jobs from Wellfound.
        
        Args:
            url: Base URL or company domain (e.g., "google" or "https://wellfound.com")
            client: Async HTTP client
            **kwargs: Additional filters (roles, locations, etc.)
            
        Returns:
            List of normalized jobs
        """
        identifier = url.strip()
        if not identifier:
            raise ValueError("URL or company identifier must be non-empty")

        try:
            # Construct Wellfound API endpoint
            if identifier.startswith("http"):
                # If full URL provided, use as-is with API path
                api_url = f"{WELLFOUND_API_URL}/jobs"
            else:
                # Assume it's a company slug
                api_url = f"{WELLFOUND_API_URL}/companies/{identifier}/jobs"

            params: dict[str, Any] = {}
            
            # Add filters from kwargs
            if "roles" in kwargs:
                params["roles"] = kwargs["roles"]
            if "locations" in kwargs:
                params["locations"] = kwargs["locations"]

            # Limit results for rate limiting
            params["limit"] = 50
            params["page"] = 1

            headers = self._get_headers()
            payload = await _get_json_with_retries(client, api_url, headers=headers)

            # Handle paginated responses
            jobs_raw = payload
            if isinstance(payload, dict):
                jobs_raw = payload.get("jobs") or payload.get("data", [])

            if not isinstance(jobs_raw, list):
                return []

            normalized_jobs: list[NormalizedJob] = []
            for item in jobs_raw:
                if not isinstance(item, dict):
                    continue

                job = self._normalize_job(item)
                if job and self._validate_normalized_job(job):
                    normalized_jobs.append(job)

            return normalized_jobs

        except httpx.RequestError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch from Wellfound {identifier}: {e}")
            return []

    async def fetch_jobs_from_company(
        self, company: str, client: httpx.AsyncClient
    ) -> list[NormalizedJob]:
        """
        Fetch jobs for a specific startup company.
        
        Args:
            company: Company slug or identifier (e.g., "stripe", "notion")
            client: Async HTTP client
            
        Returns:
            List of normalized jobs
        """
        return await self.fetch_jobs_from_url(company, client)

    def _get_headers(self) -> dict[str, str]:
        """Build request headers."""
        headers = {
            "User-Agent": "JobSync/1.0 (+http://jobsync.local)",
            "Accept": "application/json",
        }
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def _normalize_job(self, raw: dict[str, Any]) -> NormalizedJob | None:
        """
        Normalize raw Wellfound job object.
        
        Expected fields: title, description, apply_url, created_at, 
                        primary_role, locations, startup
        """
        title = raw.get("title") or raw.get("job_title")
        if not isinstance(title, str) or not title.strip():
            return None

        apply_url = raw.get("apply_url") or raw.get("url")
        if not isinstance(apply_url, str) or not apply_url.strip():
            return None

        created_at = raw.get("created_at")
        try:
            posted_date = _parse_posted_date(created_at)
        except (ValueError, TypeError):
            return None

        # Extract location
        locations = raw.get("locations", [])
        location = ""
        if isinstance(locations, list) and locations:
            first_loc = locations[0]
            if isinstance(first_loc, dict):
                location = first_loc.get("display_name", "")
            elif isinstance(first_loc, str):
                location = first_loc

        # Extract company name
        startup = raw.get("startup")
        company_name = "Unknown Startup"
        if isinstance(startup, dict):
            company_name = startup.get("name", "Unknown Startup")
        elif isinstance(startup, str):
            company_name = startup

        description = raw.get("description", "")
        if not isinstance(description, str):
            description = ""

        return NormalizedJob(
            title=title.strip(),
            location=location,
            apply_url=apply_url.strip(),
            description=description,
            posted_date=posted_date,
            company_name=company_name.strip() if isinstance(company_name, str) else "Unknown Startup",
        )
