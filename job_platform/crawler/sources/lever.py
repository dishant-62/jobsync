"""Lever ATS crawler for job boards."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

import httpx

from job_platform.crawler.base import BaseCrawler, NormalizedJob

LEVER_API_URL = "https://api.lever.co/v0/postings"
MAX_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 1.0


def _parse_posted_date(iso_str: str) -> datetime:
    """Parse ISO 8601 timestamp to timezone-aware datetime."""
    try:
        if isinstance(iso_str, (int, float)):
            # Unix timestamp in milliseconds
            return datetime.fromtimestamp(iso_str / 1000, tz=UTC)
        
        # ISO string
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
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


async def _get_jobs_json(
    client: httpx.AsyncClient, url: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """GET JSON with retries on transient errors."""
    backoff = INITIAL_BACKOFF_SECONDS
    last_error: BaseException | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            # Check if response is JSON
            try:
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError("API returned non-object JSON root")
                return payload
            except ValueError:
                # Response is not JSON (probably HTML error page)
                # Treat as 404 - company doesn't exist on Lever
                raise httpx.HTTPStatusError(
                    "Not JSON response (likely 404 page)", 
                    request=response.request, 
                    response=response
                )
                
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


class LeverCrawler(BaseCrawler):
    """Crawler for Lever-hosted job boards."""

    def __init__(self):
        super().__init__("lever")

    async def fetch_jobs_from_company(
        self, company: str, client: httpx.AsyncClient
    ) -> list[NormalizedJob]:
        """
        Fetch jobs from Lever API.
        
        Args:
            company: Company identifier (e.g., "netflix")
            client: Async HTTP client
            
        Returns:
            List of normalized jobs
        """
        token = company.strip()
        if not token:
            raise ValueError("Company identifier must be non-empty")

        url = f"{LEVER_API_URL}/{token}"
        params = {"mode": "json"}

        try:
            payload = await _get_jobs_json(client, url, params)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Company doesn't exist on Lever - return empty list
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Company {token} not found on Lever (404)")
                return []
            raise
        except Exception as e:
            # Log other errors but don't fail the entire crawl
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch from Lever {token}: {e}")
            return []

        jobs_raw = payload.get("postings")
        if not isinstance(jobs_raw, list):
            return []

        normalized_jobs: list[NormalizedJob] = []
        for item in jobs_raw:
            if not isinstance(item, dict):
                continue

            job = self._normalize_job(item, token)
            if job and self._validate_normalized_job(job):
                normalized_jobs.append(job)

        return normalized_jobs

    def _normalize_job(self, raw: dict[str, Any], company_name: str) -> NormalizedJob | None:
        """
        Normalize raw Lever job object.
        
        Expected fields: text, categories, description, hostedUrl, createdAt
        """
        title = raw.get("text")
        if not isinstance(title, str) or not title.strip():
            return None

        apply_url = raw.get("hostedUrl")
        if not isinstance(apply_url, str) or not apply_url.strip():
            return None

        created_at = raw.get("createdAt")
        if created_at is None:
            return None

        try:
            posted_date = _parse_posted_date(created_at)
        except (ValueError, TypeError):
            return None

        # Extract location from categories
        categories = raw.get("categories", {})
        location = ""
        if isinstance(categories, dict):
            loc = categories.get("location")
            if isinstance(loc, str):
                location = loc

        # Get description
        description = raw.get("description", "")
        if not isinstance(description, str):
            description = ""

        return NormalizedJob(
            title=title.strip(),
            location=location,
            apply_url=apply_url.strip(),
            description=description,
            posted_date=posted_date,
            company_name=company_name,
        )
