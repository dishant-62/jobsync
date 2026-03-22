"""Ingest Greenhouse board jobs into the application database."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import httpx

from job_platform.config import get_settings
from job_platform.crawler.greenhouse import DEFAULT_TIMEOUT, fetch_jobs
from job_platform.db.session import session_factory
from job_platform.repositories.company import CompanyRepository
from job_platform.repositories.job import JobRepository
from job_platform.utils.logging import configure_logging, get_logger

logger = get_logger("job_platform.pipeline.greenhouse_pipeline")

# Align with ``Job`` column sizes (``description`` is Text — unbounded).
_MAX_TITLE_LEN = 500
_MAX_LOCATION_LEN = 255
_MAX_APPLY_URL_LEN = 2048


def _clip(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len]


def _posted_date_only(value: datetime | date) -> date:
    if isinstance(value, datetime):
        return value.date()
    return value


@dataclass(frozen=True, slots=True)
class GreenhousePipelineResult:
    """Counters for a single board ingest run."""

    board_token: str
    fetched: int
    inserted: int
    skipped_duplicates: int


async def run_greenhouse_pipeline(company: str) -> GreenhousePipelineResult:
    """
    Fetch jobs from Greenhouse for ``company`` (board token) and insert new rows.

    Skips jobs whose ``apply_url`` already exists (via ``JobRepository.get_job_by_url``).
    """
    board = company.strip()
    if not board:
        raise ValueError("company board token must be non-empty")

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as http_client:
        jobs: list[dict[str, Any]] = await fetch_jobs(board, client=http_client)

    logger.info("greenhouse_jobs_fetched", board=board, count=len(jobs))

    inserted = 0
    skipped_duplicates = 0

    async with session_factory() as session:
        company_repo = CompanyRepository(session)
        job_repo = JobRepository(session)

        db_company = await company_repo.get_or_create_for_greenhouse_board(board)

        for job in jobs:
            apply_url = str(job["apply_url"])
            apply_url = _clip(apply_url, _MAX_APPLY_URL_LEN)

            existing = await job_repo.get_job_by_url(apply_url)
            if existing is not None:
                skipped_duplicates += 1
                continue

            posted_raw = job["posted_date"]
            if not isinstance(posted_raw, (datetime, date)):
                posted_raw = datetime.fromisoformat(str(posted_raw))
            posted_date = _posted_date_only(posted_raw)

            title = _clip(str(job["title"]), _MAX_TITLE_LEN)
            location = _clip(str(job.get("location", "")), _MAX_LOCATION_LEN)
            description = str(job.get("description", ""))

            await job_repo.create_job(
                company_id=db_company.id,
                title=title,
                location=location,
                description=description,
                apply_url=apply_url,
                posted_date=posted_date,
            )
            inserted += 1

        await session.commit()

    logger.info(
        "greenhouse_pipeline_complete",
        board=board,
        jobs_inserted=inserted,
        duplicates_skipped=skipped_duplicates,
    )

    return GreenhousePipelineResult(
        board_token=board,
        fetched=len(jobs),
        inserted=inserted,
        skipped_duplicates=skipped_duplicates,
    )


async def _run_cli() -> None:
    settings = get_settings()
    configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)

    for board in ("stripe", "airbnb"):
        await run_greenhouse_pipeline(board)


def main() -> None:
    asyncio.run(_run_cli())


if __name__ == "__main__":
    main()
