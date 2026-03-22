"""Generic job board crawler using CSS selectors and HTML parsing."""

from __future__ import annotations

import asyncio
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx

from job_platform.crawler.base import BaseCrawler, NormalizedJob

# HTML parsing with fallback
try:
    from html.parser import HTMLParser
    from urllib.request import urlopen
    HAS_HTML_PARSER = True
except ImportError:
    HAS_HTML_PARSER = False

MAX_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 1.0


def _should_retry_status(status_code: int) -> bool:
    """Retry on transient errors."""
    if status_code == 429:
        return True
    return status_code >= 500


async def _get_with_retries(
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


def _extract_text(html: str, selector_path: str) -> str:
    """
    Simple text extraction from HTML.
    
    This is a basic implementation. For production, use BeautifulSoup or lxml.
    """
    # Very basic regex-based extraction
    # For real HTML parsing, integrate BeautifulSoup or lxml
    return ""


class JobBoardCrawler(BaseCrawler):
    """Generic crawler for job board websites using CSS selectors."""

    def __init__(self):
        super().__init__("job_board")

    async def fetch_jobs_from_url(
        self,
        url: str,
        client: httpx.AsyncClient,
        **kwargs: Any,
    ) -> list[NormalizedJob]:
        """
        Fetch jobs from a generic job board URL.
        
        Args:
            url: Base URL of the job board
            client: Async HTTP client
            **kwargs: Configuration including:
                - selectors: Dict of CSS selectors for job fields
                - company_name: Fallback company name
                
        Returns:
            List of normalized jobs
        """
        if not url.strip():
            raise ValueError("URL must be non-empty")

        selectors = kwargs.get("selectors", {})
        company_name = kwargs.get("company_name", _extract_domain(url))

        try:
            html = await _get_with_retries(client, url)
            
            # Parse HTML and extract jobs
            # This is a template - actual parsing depends on site structure
            jobs = self._parse_jobs_from_html(html, url, selectors, company_name)
            
            return jobs
        except httpx.RequestError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to fetch from {url}: {e}")
            return []

    def fetch_jobs_from_url_sync(
        self,
        url: str,
        selectors: dict[str, str] | None = None,
        company_name: str | None = None,
    ) -> list[NormalizedJob]:
        """
        Synchronous version for testing or simple use cases.
        
        Args:
            url: Job board URL
            selectors: CSS selectors for job fields
            company_name: Company name
            
        Returns:
            List of normalized jobs
        """
        import httpx
        
        with httpx.Client() as client:
            loop = asyncio.new_event_loop()
            try:
                kwargs = {"selectors": selectors or {}}
                if company_name:
                    kwargs["company_name"] = company_name
                result = loop.run_until_complete(
                    self.fetch_jobs_from_url(url, client, **kwargs)
                )
                return result
            finally:
                loop.close()

    def _parse_jobs_from_html(
        self,
        html: str,
        base_url: str,
        selectors: dict[str, str],
        company_name: str,
    ) -> list[NormalizedJob]:
        """
        Parse jobs from HTML content.
        
        This is a template method. Actual implementation depends on site structure.
        For production, use BeautifulSoup:
        
        ```
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        for job_elem in soup.select(selectors.get('job_item', '.job')):
            title = job_elem.select_one(selectors.get('title', 'h2'))
            ...
        ```
        """
        # Placeholder: return empty for now
        # Site-specific selectors should be provided in config
        return []


def _extract_domain(url: str) -> str:
    """Extract company name from domain."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "").split(".")[0]
        return domain.replace("-", " ").title()
    except Exception:
        return "Unknown"
