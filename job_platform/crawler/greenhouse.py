"""Async client for the Greenhouse Job Board API."""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import UTC, datetime
from typing import Any

import httpx

JOBS_URL_TEMPLATE = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
CONTENT_PARAM = {"content": "true"}

MAX_ATTEMPTS = 3
INITIAL_BACKOFF_SECONDS = 1.0
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


def _parse_posted_date(updated_at: str) -> datetime:
    """Parse Greenhouse ``updated_at`` into a timezone-aware ``datetime``."""
    normalized = updated_at[:-1] + "+00:00" if updated_at.endswith("Z") else updated_at
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def _normalize_job(raw: dict[str, Any]) -> dict[str, Any] | None:
    """
    Map a raw Greenhouse job object to the normalized shape.

    Expected raw fields: title, location.name, absolute_url, content, updated_at.
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

    return {
        "title": title.strip(),
        "location": location_name,
        "apply_url": apply_url.strip(),
        "description": description,
        "posted_date": posted_date,
    }


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


async def fetch_jobs(
    company: str,
    *,
    client: httpx.AsyncClient | None = None,
    timeout: httpx.Timeout | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch and normalize published jobs for a Greenhouse board token.

    Board token is the path segment from ``https://boards.greenhouse.io/{token}``.

    Each dict has keys: ``title``, ``location``, ``apply_url``, ``description``,
    ``posted_date`` (timezone-aware ``datetime`` from ``updated_at``).
    """
    token = company.strip()
    if not token:
        raise ValueError("company board token must be non-empty")

    url = JOBS_URL_TEMPLATE.format(company=token)
    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=timeout or DEFAULT_TIMEOUT)
        close_client = True

    try:
        payload = await _get_jobs_json(client, url)
        jobs_raw = payload.get("jobs")
        if not isinstance(jobs_raw, list):
            return []

        out: list[dict[str, Any]] = []
        for item in jobs_raw:
            if isinstance(item, dict):
                normalized = _normalize_job(item)
                if normalized is not None:
                    out.append(normalized)
        return out
    finally:
        if close_client:
            await client.aclose()


def _print_company_block(company: str, jobs: list[dict[str, Any]]) -> None:
    print(f"\n{'=' * 60}", file=sys.stdout)
    print(company.upper(), file=sys.stdout)
    print(f"{'=' * 60}", file=sys.stdout)
    print(f"Total normalized jobs: {len(jobs)}", file=sys.stdout)
    preview = jobs[:3]
    print(json.dumps(preview, indent=2, default=str), file=sys.stdout)
    if len(jobs) > len(preview):
        print(f"... ({len(jobs) - len(preview)} more not shown — full list omitted)", file=sys.stdout)


async def _run_demo() -> None:
    # Public board tokens; ``notion`` is not a valid token on the Job Board API (404).
    companies = ("stripe", "airbnb", "figma")
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        for company in companies:
            try:
                jobs = await fetch_jobs(company, client=client)
                _print_company_block(company, jobs)
            except httpx.HTTPStatusError as exc:
                print(f"\n{'=' * 60}", file=sys.stdout)
                print(company.upper(), file=sys.stdout)
                print(f"{'=' * 60}", file=sys.stdout)
                detail = (
                    " (no public Greenhouse board at this token — try another slug)"
                    if exc.response.status_code == 404
                    else ""
                )
                print(
                    f"HTTP {exc.response.status_code} for {exc.request.url!r}: {exc!r}{detail}",
                    file=sys.stdout,
                )
            except (httpx.RequestError, httpx.TimeoutException) as exc:
                print(f"\n{'=' * 60}", file=sys.stdout)
                print(company.upper(), file=sys.stdout)
                print(f"{'=' * 60}", file=sys.stdout)
                print(f"Network error after retries: {exc!r}", file=sys.stdout)


def main() -> None:
    asyncio.run(_run_demo())


if __name__ == "__main__":
    main()
