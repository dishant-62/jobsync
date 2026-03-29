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
    """GET JSON with retries on transient errors.

    The Lever v0 API returns a JSON **array** of posting objects, so this
    function returns ``list | dict`` (the caller must handle both).
    """
    backoff = INITIAL_BACKOFF_SECONDS
    last_error: BaseException | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()

            try:
                payload = response.json()
            except ValueError:
                # Response is not valid JSON (HTML error page, etc.)
                raise httpx.HTTPStatusError(
                    "Not JSON response (likely 404 page)",
                    request=response.request,
                    response=response,
                )

            # Lever v0 returns a list; accept both list and dict
            if isinstance(payload, (list, dict)):
                return payload

            raise httpx.HTTPStatusError(
                f"Unexpected JSON type: {type(payload).__name__}",
                request=response.request,
                response=response,
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
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Company {token} not found on Lever (404)")
                return []
            raise
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch from Lever {token}: {e}")
            return []

        # Lever v0 API returns a JSON array of postings directly,
        # but some endpoints may wrap in {"postings": [...]}.
        if isinstance(payload, list):
            jobs_raw = payload
        elif isinstance(payload, dict):
            jobs_raw = payload.get("postings") or payload.get("jobs") or []
        else:
            jobs_raw = []

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
