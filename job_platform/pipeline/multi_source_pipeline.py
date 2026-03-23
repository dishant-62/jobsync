"""Unified pipeline for ingesting jobs from multiple sources."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import httpx

from job_platform.config import get_settings
from job_platform.crawler.sources.config import SourceConfig, get_sources
from job_platform.crawler.sources.registry import get_crawler
from job_platform.db.session import session_factory
from job_platform.repositories.company import CompanyRepository
from job_platform.repositories.job import JobRepository
from job_platform.utils.logging import configure_logging, get_logger

logger = get_logger("job_platform.pipeline.multi_source_pipeline")

# Align with ``Job`` column sizes
_MAX_TITLE_LEN = 500
_MAX_LOCATION_LEN = 255
_MAX_APPLY_URL_LEN = 2048


def _clip(text: str, max_len: int) -> str:
    """Truncate text to max length."""
    if len(text) <= max_len:
        return text
    return text[:max_len]


def _posted_date_only(value: datetime | date) -> date:
    """Extract date from datetime or return date as-is."""
    if isinstance(value, datetime):
        return value.date()
    return value


@dataclass(frozen=True, slots=True)
class SourceIngestResult:
    """Result of ingesting one job source."""

    source_name: str
    source_type: str
    fetched: int
    inserted: int
    skipped_duplicates: int
    error: str | None = None


@dataclass(frozen=True, slots=True)
class PipelineRunResult:
    """Summary of entire pipeline run."""

    total_sources: int
    successful_sources: int
    failed_sources: int
    total_fetched: int
    total_inserted: int
    total_duplicates: int
    source_results: list[SourceIngestResult]


async def ingest_single_source(
    source: SourceConfig,
    http_client: httpx.AsyncClient,
) -> SourceIngestResult:
    """
    Ingest jobs from a single source.
    
    Args:
        source: Source configuration
        http_client: Async HTTP client
        
    Returns:
        Result of ingestion
    """
    try:
        crawler = get_crawler(source.source_type)
        
        # Fetch jobs from source
        jobs = []
        if source.company:
            jobs = await crawler.fetch_jobs_from_company(source.company, http_client)
        elif source.url:
            jobs = await crawler.fetch_jobs_from_url(
                source.url, http_client, **source.config
            )
        else:
            raise ValueError(f"Source {source.name} has no company or url configured")

        logger.info(
            "source_jobs_fetched",
            source_name=source.name,
            source_type=source.source_type,
            count=len(jobs),
        )

        # Insert into database
        inserted = 0
        skipped_duplicates = 0

        async with session_factory() as session:
            company_repo = CompanyRepository(session)
            job_repo = JobRepository(session)

            # Get or create company record
            identifier = source.company or source.url or "unknown"
            db_company = await company_repo.get_or_create_for_source(
                source_type=source.source_type,
                identifier=identifier,
                display_name=source.name,
            )

            # Insert each job
            for normalized_job in jobs:
                apply_url = str(normalized_job.apply_url)
                apply_url = _clip(apply_url, _MAX_APPLY_URL_LEN)

                # Check for duplicates
                existing = await job_repo.get_job_by_url(apply_url)
                if existing is not None:
                    skipped_duplicates += 1
                    continue

                # Normalize dates
                posted_raw = normalized_job.posted_date
                if not isinstance(posted_raw, (datetime, date)):
                    posted_raw = datetime.fromisoformat(str(posted_raw))
                posted_date = _posted_date_only(posted_raw)

                # Clip text fields to DB limits
                title = _clip(str(normalized_job.title), _MAX_TITLE_LEN)
                location = _clip(str(normalized_job.location), _MAX_LOCATION_LEN)
                description = str(normalized_job.description)

                await job_repo.create_job(
                    company_id=db_company.id,
                    title=title,
                    location=location,
                    description=description,
                    apply_url=apply_url,
                    posted_date=posted_date,
                )
                inserted += 1

            # Commit transaction
            await session.commit()

        return SourceIngestResult(
            source_name=source.name,
            source_type=source.source_type,
            fetched=len(jobs),
            inserted=inserted,
            skipped_duplicates=skipped_duplicates,
        )

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(
            "source_ingest_error",
            source_name=source.name,
            source_type=source.source_type,
            error=error_msg,
        )
        return SourceIngestResult(
            source_name=source.name,
            source_type=source.source_type,
            fetched=0,
            inserted=0,
            skipped_duplicates=0,
            error=error_msg,
        )


async def run_all_sources(
    sources: list[SourceConfig] | None = None,
    timeout: httpx.Timeout | None = None,
    parallel: bool = True,
    max_concurrent: int = 3,
) -> PipelineRunResult:
    """
    Ingest jobs from all configured sources.
    
    Args:
        sources: List of sources to ingest (defaults to all configured sources)
        timeout: Optional HTTP timeout
        parallel: Run sources in parallel (respects max_concurrent)
        max_concurrent: Max concurrent source ingestions (when parallel=True)
        
    Returns:
        Summary of pipeline run
    """
    if sources is None:
        sources = get_sources()

    if not sources:
        logger.warning("No sources configured")
        return PipelineRunResult(
            total_sources=0,
            successful_sources=0,
            failed_sources=0,
            total_fetched=0,
            total_inserted=0,
            total_duplicates=0,
            source_results=[],
        )

    logger.info("pipeline_start", total_sources=len(sources))

    # Create HTTP client with optional timeout
    default_timeout = httpx.Timeout(30.0, connect=10.0)
    http_timeout = timeout or default_timeout

    async with httpx.AsyncClient(timeout=http_timeout) as client:
        if parallel:
            # Run sources concurrently with semaphore to limit concurrency
            semaphore = asyncio.Semaphore(max_concurrent)

            async def run_with_semaphore(source: SourceConfig) -> SourceIngestResult:
                async with semaphore:
                    return await ingest_single_source(source, client)

            results = await asyncio.gather(
                *[run_with_semaphore(source) for source in sources],
                return_exceptions=False,
            )
        else:
            # Run sources sequentially
            results = []
            for source in sources:
                result = await ingest_single_source(source, client)
                results.append(result)

    # Aggregate results
    successful = sum(1 for r in results if r.error is None)
    failed = sum(1 for r in results if r.error is not None)
    total_fetched = sum(r.fetched for r in results)
    total_inserted = sum(r.inserted for r in results)
    total_duplicates = sum(r.skipped_duplicates for r in results)

    logger.info(
        "pipeline_complete",
        total_sources=len(sources),
        successful=successful,
        failed=failed,
        total_fetched=total_fetched,
        total_inserted=total_inserted,
        total_duplicates=total_duplicates,
    )

    return PipelineRunResult(
        total_sources=len(sources),
        successful_sources=successful,
        failed_sources=failed,
        total_fetched=total_fetched,
        total_inserted=total_inserted,
        total_duplicates=total_duplicates,
        source_results=results,
    )


async def run_sources_by_type(
    source_type: str,
    timeout: httpx.Timeout | None = None,
) -> PipelineRunResult:
    """
    Run pipeline for sources of a specific type.
    
    Args:
        source_type: Filter by crawler type
        timeout: Optional HTTP timeout
        
    Returns:
        Pipeline run result
    """
    from job_platform.crawler.sources.config import get_sources_by_type
    
    sources = get_sources_by_type(source_type)
    logger.info("pipeline_start_by_type", source_type=source_type, count=len(sources))
    return await run_all_sources(sources=sources, timeout=timeout, parallel=False)
