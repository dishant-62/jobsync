"""Greenhouse ATS crawler implemented as BaseCrawler."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

import httpx

from job_platform.crawler.base import BaseCrawler, NormalizedJob

JOBS_URL_TEMPLATE = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
CONTENT_PARAM = {"content": "true"}
MAX_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 1.0


def _parse_posted_date(updated_at: str) -> datetime:
    """Parse Greenhouse ``updated_at`` into a timezone-aware ``datetime``."""
    normalized = updated_at[:-1] + "+00:00" if updated_at.endswith("Z") else updated_at
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def _should_retry_status(status_code: int) -> bool:
    """Retry only on likely-transient HTTP statuses."""
    if status_code == 429:
        return True
    return status_code >= 500


async def _get_jobs_json(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    """GET JSON with retries on timeouts, transport errors, and 5xx/429."""
    backoff = INITIAL_BACKOFF_SECONDS
    last_error: BaseException | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = await client.get(url, params=CONTENT_PARAM)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("Greenhouse API returned non-object JSON root")
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

    assert last_error is not None
    raise last_error


class GreenhouseCrawler(BaseCrawler):
    """Crawler for Greenhouse-hosted job boards."""

    def __init__(self):
        super().__init__("greenhouse")

    async def fetch_jobs_from_company(
        self, company: str, client: httpx.AsyncClient
    ) -> list[NormalizedJob]:
        """
        Fetch jobs from Greenhouse board.
        
        Args:
            company: Greenhouse board token (e.g., "stripe", "airbnb")
            client: Async HTTP client
            
        Returns:
            List of normalized jobs
        """
        token = company.strip()
        if not token:
            raise ValueError("Company board token must be non-empty")

        url = JOBS_URL_TEMPLATE.format(company=token)
        payload = await _get_jobs_json(client, url)
        jobs_raw = payload.get("jobs")
        if not isinstance(jobs_raw, list):
            return []

        normalized_jobs: list[NormalizedJob] = []
        for item in jobs_raw:
            if isinstance(item, dict):
                job = self._normalize_job(item, token)
                if job and self._validate_normalized_job(job):
                    normalized_jobs.append(job)

        return normalized_jobs

    def _normalize_job(self, raw: dict[str, Any], company_name: str) -> NormalizedJob | None:
        """
        Normalize raw Greenhouse job object.
        
        Expected fields: title, location.name, absolute_url, content, updated_at
        """
        title = raw.get("title")
        if not isinstance(title, str) or not title.strip():
            return None

        apply_url = raw.get("absolute_url")
        if not isinstance(apply_url, str) or not apply_url.strip():
            return None

        updated_at = raw.get("updated_at")
        if not isinstance(updated_at, str) or not updated_at.strip():
            return None

        try:
            posted_date = _parse_posted_date(updated_at.strip())
        except ValueError:
            return None

        location_block = raw.get("location")
        location_name = ""
        if isinstance(location_block, dict):
            name = location_block.get("name")
            if isinstance(name, str):
                location_name = name

        content = raw.get("content")
        description = content if isinstance(content, str) else ""

        return NormalizedJob(
            title=title.strip(),
            location=location_name,
            apply_url=apply_url.strip(),
            description=description,
            posted_date=posted_date,
            company_name=company_name,
        )
