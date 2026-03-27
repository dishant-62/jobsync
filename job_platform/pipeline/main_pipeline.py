"""Integrated pipeline: crawler → scraper → parser → DB."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import httpx
import structlog

from job_platform.config import get_settings
from job_platform.crawler.sources.config import SourceConfig, get_sources
from job_platform.crawler.sources.registry import get_crawler
from job_platform.db.session import session_factory
from job_platform.models.domain.job import FinalJob
from job_platform.parser.job_parser import parse_job_description
from job_platform.repositories.company import CompanyRepository
from job_platform.repositories.job import JobRepository
from job_platform.scraper.unified_scraper import normalize_raw_job
from job_platform.utils.job_id import generate_job_id
from job_platform.utils.logging import configure_logging, get_logger
from job_platform.utils.ranking import calculate_job_score

logger = get_logger("job_platform.pipeline.main_pipeline")

# Align with Job column sizes
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
class JobProcessingResult:
    """Result of processing a single job through the pipeline."""

    source_name: str
    job_title: str
    raw_normalized: bool
    parsed_success: bool
    inserted: bool
    duplicate: bool
    error: str | None = None


@dataclass(frozen=True, slots=True)
class SourceProcessingResult:
    """Result of processing jobs from a single source."""

    source_name: str
    source_type: str
    fetched: int
    processed: int
    raw_success: int
    parsed_success: int
    inserted: int
    duplicates: int
    errors: int
    job_results: list[JobProcessingResult]


@dataclass(frozen=True, slots=True)
class PipelineMetrics:
    """Metrics collected during pipeline run."""

    jobs_processed: int
    parsing_success: int
    parsing_failures: int
    insert_success: int
    insert_failures: int
    duplicates_found: int
    sources_processed: int
    sources_successful: int
    sources_failed: int


@dataclass(frozen=True, slots=True)
class PipelineRunResult:
    """Summary of entire pipeline run."""

    metrics: PipelineMetrics
    source_results: list[SourceProcessingResult]


async def process_single_job(
    raw_job_data: dict[str, Any],
    source_name: str,
    source_type: str,    source_identifier: str,    company_repo: CompanyRepository,
    job_repo: JobRepository,
) -> JobProcessingResult:
    """
    Process a single job through the complete pipeline: scraper → parser → DB.

    Args:
        raw_job_data: Raw job data from crawler (dict or NormalizedJob)
        source_name: Name of the source
        source_type: Type of the source
        company_repo: Company repository
        job_repo: Job repository

    Returns:
        Result of job processing
    """
    # Handle both dict and NormalizedJob objects
    if hasattr(raw_job_data, 'to_dict'):
        # It's a NormalizedJob object
        job_dict = raw_job_data.to_dict()
        job_title = raw_job_data.title
    else:
        # It's already a dict
        job_dict = raw_job_data
        job_title = job_dict.get("title", "Unknown Title")

    try:
        # Step 1: Normalize raw job data using unified scraper
        raw_job = await normalize_raw_job(job_dict, source_type)

        if raw_job is None:
            logger.warning(
                "job_raw_normalization_failed",
                source=source_name,
                title=job_title,
                reason="validation_error"
            )
            return JobProcessingResult(
                source_name=source_name,
                job_title=job_title,
                raw_normalized=False,
                parsed_success=False,
                inserted=False,
                duplicate=False,
                error="raw_normalization_failed"
            )

        logger.info(
            "job_raw_normalized",
            source=source_name,
            title=raw_job.title,
            company=raw_job.company
        )

        # Step 2: Parse job description
        parsed_info = parse_job_description(raw_job.description)

        parsed_success = len(parsed_info.skills) > 0 or parsed_info.experience_level is not None

        if parsed_success:
            logger.info(
                "job_parsed_success",
                source=source_name,
                title=raw_job.title,
                skills_count=len(parsed_info.skills),
                experience_level=parsed_info.experience_level,
                salary_range=f"{parsed_info.salary_min}-{parsed_info.salary_max}" if parsed_info.salary_min else None,
                is_remote=parsed_info.is_remote
            )
        else:
            logger.warning(
                "job_parsed_no_data",
                source=source_name,
                title=raw_job.title,
                reason="no_structured_data_found"
            )

        # Step 3: Merge into FinalJob
        final_job_data = {**raw_job.model_dump(), **parsed_info.model_dump()}
        final_job = FinalJob(**final_job_data)

        # Step 4: Generate deterministic job_id
        apply_url = str(final_job.apply_url)
        apply_url = _clip(apply_url, _MAX_APPLY_URL_LEN)
        job_id = generate_job_id(source_identifier, apply_url)

        # Step 5: Get or create company
        db_company = await company_repo.get_or_create_for_source(
            source_type=source_type,
            identifier=source_identifier,
            display_name=source_name,
        )

        # Step 6: Normalize dates
        posted_raw = final_job.posted_date
        if not isinstance(posted_raw, (datetime, date)):
            posted_raw = datetime.fromisoformat(str(posted_raw))
        posted_date = _posted_date_only(posted_raw)

        # Step 7: Clip text fields to DB limits
        title = _clip(str(final_job.title), _MAX_TITLE_LEN)
        location = _clip(str(final_job.location or ""), _MAX_LOCATION_LEN)
        description = str(final_job.description)

        # Step 8: Calculate job ranking score
        score = calculate_job_score(
            posted_date=posted_date,
            salary_min=final_job.salary_min,
            salary_max=final_job.salary_max,
            is_remote=final_job.is_remote,
            description=description,
            skills=final_job.skills,
        )

        # Step 9: Upsert into database
        db_job, created = await job_repo.upsert_job(
            job_id=job_id,
            company_id=db_company.id,
            title=title,
            location=location,
            description=description,
            apply_url=apply_url,
            posted_date=posted_date,
            skills=final_job.skills,
            experience_level=final_job.experience_level,
            salary_min=final_job.salary_min,
            salary_max=final_job.salary_max,
            is_remote=final_job.is_remote,
            score=score,
        )

        if created:
            logger.info(
                "job_inserted_success",
                source=source_name,
                title=final_job.title,
                job_id=job_id,
                skills_count=len(final_job.skills or []),
                experience_level=final_job.experience_level,
                is_remote=final_job.is_remote
            )
        else:
            logger.info(
                "job_updated_success",
                source=source_name,
                title=final_job.title,
                job_id=job_id,
                skills_count=len(final_job.skills or []),
                experience_level=final_job.experience_level,
                is_remote=final_job.is_remote
            )

        return JobProcessingResult(
            source_name=source_name,
            job_title=final_job.title,
            raw_normalized=True,
            parsed_success=parsed_success,
            inserted=created,
            duplicate=not created
        )

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(
            "job_processing_error",
            source=source_name,
            title=job_title,
            error=error_msg,
            exc_info=True
        )
        return JobProcessingResult(
            source_name=source_name,
            job_title=job_title,
            raw_normalized=False,
            parsed_success=False,
            inserted=False,
            duplicate=False,
            error=error_msg
        )


async def process_source_jobs(
    source: SourceConfig,
    http_client: httpx.AsyncClient,
) -> SourceProcessingResult:
    """
    Process all jobs from a single source through the complete pipeline.

    Args:
        source: Source configuration
        http_client: Async HTTP client

    Returns:
        Result of source processing
    """
    try:
        crawler = get_crawler(source.source_type)

        # Fetch raw jobs from source
        raw_jobs = []
        if source.company:
            raw_jobs = await crawler.fetch_jobs_from_company(source.company, http_client)
        elif source.url:
            raw_jobs = await crawler.fetch_jobs_from_url(
                source.url, http_client, **source.config
            )
        else:
            raise ValueError(f"Source {source.name} has no company or url configured")

        logger.info(
            "source_jobs_fetched",
            source_name=source.name,
            source_type=source.source_type,
            count=len(raw_jobs),
        )

        if not raw_jobs:
            return SourceProcessingResult(
                source_name=source.name,
                source_type=source.source_type,
                fetched=0,
                processed=0,
                raw_success=0,
                parsed_success=0,
                inserted=0,
                duplicates=0,
                errors=0,
                job_results=[]
            )

        # Process each job
        job_results = []

        async with session_factory() as session:
            company_repo = CompanyRepository(session)
            job_repo = JobRepository(session)

            for raw_job_data in raw_jobs:
                result = await process_single_job(
                    raw_job_data, source.name, source.source_type, source.company or source.url or source.name,
                    company_repo, job_repo
                )
                job_results.append(result)

            # Commit all changes
            await session.commit()

        # Aggregate results
        processed = len(job_results)
        raw_success = sum(1 for r in job_results if r.raw_normalized)
        parsed_success = sum(1 for r in job_results if r.parsed_success)
        inserted = sum(1 for r in job_results if r.inserted)
        duplicates = sum(1 for r in job_results if r.duplicate)
        errors = sum(1 for r in job_results if r.error is not None)

        logger.info(
            "source_processing_complete",
            source_name=source.name,
            fetched=len(raw_jobs),
            processed=processed,
            raw_success=raw_success,
            parsed_success=parsed_success,
            inserted=inserted,
            duplicates=duplicates,
            errors=errors
        )

        return SourceProcessingResult(
            source_name=source.name,
            source_type=source.source_type,
            fetched=len(raw_jobs),
            processed=processed,
            raw_success=raw_success,
            parsed_success=parsed_success,
            inserted=inserted,
            duplicates=duplicates,
            errors=errors,
            job_results=job_results
        )

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(
            "source_processing_error",
            source_name=source.name,
            source_type=source.source_type,
            error=error_msg,
            exc_info=True
        )
        return SourceProcessingResult(
            source_name=source.name,
            source_type=source.source_type,
            fetched=0,
            processed=0,
            raw_success=0,
            parsed_success=0,
            inserted=0,
            duplicates=0,
            errors=1,
            job_results=[]
        )


async def run_main_pipeline(
    sources: list[SourceConfig] | None = None,
    timeout: httpx.Timeout | None = None,
    parallel: bool = True,
    max_concurrent: int = 3,
) -> PipelineRunResult:
    """
    Run the complete pipeline: crawler → scraper → parser → DB.

    Args:
        sources: List of sources to process (defaults to all configured sources)
        timeout: Optional HTTP timeout
        parallel: Run sources in parallel (respects max_concurrent)
        max_concurrent: Max concurrent source processing (when parallel=True)

    Returns:
        Summary of pipeline run with metrics
    """
    if sources is None:
        sources = get_sources()

    if not sources:
        logger.warning("no_sources_configured")
        empty_metrics = PipelineMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)
        return PipelineRunResult(empty_metrics, [])

    logger.info("pipeline_start", total_sources=len(sources))

    # Create HTTP client with optional timeout
    default_timeout = httpx.Timeout(30.0, connect=10.0)
    http_timeout = timeout or default_timeout

    async with httpx.AsyncClient(timeout=http_timeout) as client:
        if parallel:
            # Run sources concurrently with semaphore to limit concurrency
            semaphore = asyncio.Semaphore(max_concurrent)

            async def run_with_semaphore(source: SourceConfig) -> SourceProcessingResult:
                async with semaphore:
                    return await process_source_jobs(source, client)

            source_results = await asyncio.gather(
                *[run_with_semaphore(source) for source in sources],
                return_exceptions=False,
            )
        else:
            # Run sources sequentially
            source_results = []
            for source in sources:
                result = await process_source_jobs(source, client)
                source_results.append(result)

    # Calculate metrics
    total_jobs_processed = sum(r.processed for r in source_results)
    total_parsing_success = sum(r.parsed_success for r in source_results)
    total_parsing_failures = total_jobs_processed - total_parsing_success
    total_insert_success = sum(r.inserted for r in source_results)
    total_insert_failures = total_jobs_processed - total_insert_success - sum(r.duplicates for r in source_results)
    total_duplicates = sum(r.duplicates for r in source_results)
    total_sources = len(source_results)
    successful_sources = sum(1 for r in source_results if r.errors == 0)
    failed_sources = total_sources - successful_sources

    metrics = PipelineMetrics(
        jobs_processed=total_jobs_processed,
        parsing_success=total_parsing_success,
        parsing_failures=total_parsing_failures,
        insert_success=total_insert_success,
        insert_failures=total_insert_failures,
        duplicates_found=total_duplicates,
        sources_processed=total_sources,
        sources_successful=successful_sources,
        sources_failed=failed_sources
    )

    logger.info(
        "pipeline_complete",
        jobs_processed=total_jobs_processed,
        parsing_success=total_parsing_success,
        parsing_failures=total_parsing_failures,
        insert_success=total_insert_success,
        insert_failures=total_insert_failures,
        duplicates_found=total_duplicates,
        sources_processed=total_sources,
        sources_successful=successful_sources,
        sources_failed=failed_sources
    )

    return PipelineRunResult(metrics, source_results)