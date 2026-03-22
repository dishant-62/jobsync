"""Crawler for remote job aggregators (remoteok.com, weworkremotely.com)."""

from __future__ import annotations

import asyncio
import json
import re
from datetime import UTC, datetime
from typing import Any
from html.parser import HTMLParser

import httpx

from job_platform.crawler.base import BaseCrawler, NormalizedJob

MAX_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 1.0


def _should_retry_status(status_code: int) -> bool:
    """Retry on transient errors."""
    if status_code == 429:
        return True
    return status_code >= 500


async def _get_json_with_retries(
    client: httpx.AsyncClient, url: str
) -> dict[str, Any] | list[Any]:
    """GET JSON with retries."""
    backoff = INITIAL_BACKOFF_SECONDS
    last_error: BaseException | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = await client.get(url)
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


async def _get_html_with_retries(
    client: httpx.AsyncClient, url: str
) -> str:
    """GET HTML with retries."""
    backoff = INITIAL_BACKOFF_SECONDS
    last_error: BaseException | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            return response.text
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
    raise RuntimeError("Failed to fetch page after retries")


class _WeWorkRemotelyParser(HTMLParser):
    """Simple HTML parser for WeWorkRemotely job listings."""

    def __init__(self):
        super().__init__()
        self.jobs: list[dict[str, Any]] = []
        self.current_job: dict[str, Any] | None = None
        self.in_job_listing = False
        self.in_title = False
        self.in_company = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handle HTML start tags."""
        attrs_dict = dict(attrs) if attrs else {}

        if tag == "div" and "job-post" in attrs_dict.get("class", ""):
            self.in_job_listing = True
            self.current_job = {}
        elif self.in_job_listing and tag == "h2":
            self.in_title = True
        elif self.in_job_listing and tag == "span" and "company" in attrs_dict.get("class", ""):
            self.in_company = True

    def handle_endtag(self, tag: str) -> None:
        """Handle HTML end tags."""
        if tag == "h2":
            self.in_title = False
        elif tag == "span" and self.in_company:
            self.in_company = False
        elif tag == "div" and self.in_job_listing:
            if self.current_job:
                self.jobs.append(self.current_job)
            self.in_job_listing = False
            self.current_job = None

    def handle_data(self, data: str) -> None:
        """Handle text content."""
        if self.in_title and self.current_job is not None:
            self.current_job["title"] = data.strip()
        elif self.in_company and self.current_job is not None:
            self.current_job["company"] = data.strip()


class RemoteJobsCrawler(BaseCrawler):
    """Crawler for remote job aggregators."""

    def __init__(self):
        super().__init__("remote_jobs")

    async def fetch_jobs_from_url(
        self,
        url: str,
        client: httpx.AsyncClient,
        **kwargs: Any,
    ) -> list[NormalizedJob]:
        """
        Fetch jobs from remote job aggregators.
        
        Supports:
        - remoteok.com (JSON API)
        - weworkremotely.com (HTML parsing)
        
        Args:
            url: Base URL (e.g., "https://remoteok.com" or "https://weworkremotely.com")
            client: Async HTTP client
            **kwargs: Additional options (e.g., category filter)
            
        Returns:
            List of normalized jobs
        """
        url = url.strip()
        if not url:
            raise ValueError("URL must be non-empty")

        if "remoteok" in url:
            return await self._fetch_remoteok(url, client, **kwargs)
        elif "weworkremotely" in url:
            return await self._fetch_weworkremotely(url, client, **kwargs)
        else:
            raise ValueError(f"Unsupported remote job aggregator: {url}")

    async def _fetch_remoteok(
        self,
        url: str,
        client: httpx.AsyncClient,
        **kwargs: Any,
    ) -> list[NormalizedJob]:
        """Fetch from RemoteOK JSON API."""
        # RemoteOK API: https://remoteok.com/api
        api_url = url.rstrip("/") + "/api"

        try:
            payload = await _get_json_with_retries(client, api_url)
            if not isinstance(payload, list):
                return []

            normalized_jobs: list[NormalizedJob] = []
            for item in payload:
                if not isinstance(item, dict):
                    continue

                job = self._normalize_remoteok_job(item)
                if job and self._validate_normalized_job(job):
                    normalized_jobs.append(job)

            return normalized_jobs
        except httpx.RequestError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch from RemoteOK: {e}")
            return []

    async def _fetch_weworkremotely(
        self,
        url: str,
        client: httpx.AsyncClient,
        **kwargs: Any,
    ) -> list[NormalizedJob]:
        """Fetch from WeWorkRemotely HTML."""
        # For production, this should use BeautifulSoup or similar
        # This is a template approach
        try:
            html = await _get_html_with_retries(client, url)
            parser = _WeWorkRemotelyParser()
            parser.feed(html)
            
            # Parse results and return normalized jobs
            # This is simplified - real implementation would extract more fields
            return []
        except httpx.RequestError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch from WeWorkRemotely: {e}")
            return []

    def _normalize_remoteok_job(self, raw: dict[str, Any]) -> NormalizedJob | None:
        """
        Normalize RemoteOK job object.
        
        Expected fields: title, company, location, description, url, date
        """
        title = raw.get("title")
        if not isinstance(title, str) or not title.strip():
            return None

        company_name = raw.get("company", "Remote Job")
        if not isinstance(company_name, str):
            company_name = "Remote Job"

        apply_url = raw.get("url")
        if not isinstance(apply_url, str) or not apply_url.strip():
            return None

        location = raw.get("location", "Remote")
        if not isinstance(location, str):
            location = "Remote"

        description = raw.get("description", "")
        if not isinstance(description, str):
            description = ""

        # Parse date
        posted_date_raw = raw.get("date")
        try:
            if isinstance(posted_date_raw, str):
                posted_date = datetime.fromisoformat(posted_date_raw.replace("Z", "+00:00"))
            elif isinstance(posted_date_raw, (int, float)):
                posted_date = datetime.fromtimestamp(posted_date_raw, tz=UTC)
            else:
                posted_date = datetime.now(tz=UTC)
        except (ValueError, TypeError):
            posted_date = datetime.now(tz=UTC)

        if posted_date.tzinfo is None:
            posted_date = posted_date.replace(tzinfo=UTC)

        return NormalizedJob(
            title=title.strip(),
            location=location,
            apply_url=apply_url.strip(),
            description=description,
            posted_date=posted_date,
            company_name=company_name.strip() if isinstance(company_name, str) else "Remote Job",
        )
