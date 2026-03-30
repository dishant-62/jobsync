"""Enhanced crawler engine with detailed logging and scalability fixes."""

from __future__ import annotations

import asyncio
import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

from job_platform.config import get_settings
from job_platform.crawler.sources.config import get_sources
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

# Configuration
DEBUG = True  # Set to True for detailed API response logging
MAX_CONCURRENT_SOURCES = 20  # Increased from 3 for better performance
HTTP_TIMEOUT = httpx.Timeout(30.0, connect=10.0)

logger = get_logger("job_platform.crawler.engine")


@dataclass(frozen=True, slots=True)
class CrawlResult:
    """Result of crawling a single source."""

    source_name: str
    source_type: str
    fetched: int
    processed: int
    inserted: int
    duplicates: int
    errors: int
    duration_seconds: float
    api_response_size: int | None = None
    first_jobs_sample: list[dict[str, Any]] | None = None


@dataclass(frozen=True, slots=True)
class CrawlSummary:
    """Summary of entire crawl operation."""

    total_sources: int
    successful_sources: int
    failed_sources: int
    total_fetched: int
    total_inserted: int
    total_duplicates: int
    total_errors: int
    total_duration_seconds: float
    sources_by_type: dict[str, int]


class EnhancedCrawlerEngine:
    """Enhanced crawler engine with detailed logging and performance optimizations."""

    def __init__(self):
        self.start_time = time.time()
        self.results: list[CrawlResult] = []

    async def crawl_all_sources(self) -> CrawlSummary:
        """Crawl all configured sources with enhanced logging and concurrency."""
        logger.info("🚀 STARTING ENHANCED CRAWLER ENGINE")
        logger.info("=" * 80)

        sources = get_sources()
        logger.info(f"📊 Total sources configured: {len(sources)}")

        # Group sources by type for reporting
        sources_by_type = defaultdict(int)
        for source in sources:
            sources_by_type[source.source_type] += 1

        logger.info("📋 Sources by type:", extra=sources_by_type)

        # Create HTTP client
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            # Process sources concurrently with higher concurrency
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_SOURCES)

            async def crawl_with_semaphore(source):
                async with semaphore:
                    return await self._crawl_single_source(source, client)

            logger.info(f"⚡ Processing {len(sources)} sources with concurrency={MAX_CONCURRENT_SOURCES}")

            # Process all sources
            tasks = [crawl_with_semaphore(source) for source in sources]
            self.results = await asyncio.gather(*tasks, return_exceptions=False)

        # Calculate summary
        successful_sources = sum(1 for r in self.results if r.errors == 0)
        failed_sources = len(self.results) - successful_sources
        total_fetched = sum(r.fetched for r in self.results)
        total_inserted = sum(r.inserted for r in self.results)
        total_duplicates = sum(r.duplicates for r in self.results)
        total_errors = sum(r.errors for r in self.results)
        total_duration = time.time() - self.start_time

        summary = CrawlSummary(
            total_sources=len(sources),
            successful_sources=successful_sources,
            failed_sources=failed_sources,
            total_fetched=total_fetched,
            total_inserted=total_inserted,
            total_duplicates=total_duplicates,
            total_errors=total_errors,
            total_duration_seconds=total_duration,
            sources_by_type=dict(sources_by_type)
        )

        self._print_final_summary(summary)
        return summary

    async def _crawl_single_source(self, source, client: httpx.AsyncClient) -> CrawlResult:
        """Crawl a single source with detailed logging."""
        source_start_time = time.time()

        logger.info(f"🔍 Starting crawl: {source.name} ({source.source_type})")

        try:
            # Get the appropriate crawler
            crawler = get_crawler(source.source_type)

            # Fetch raw jobs from source
            raw_jobs = []
            api_response_size = None

            if source.company:
                logger.info(f"🏢 Fetching from company: {source.company}")
                raw_jobs = await crawler.fetch_jobs_from_company(source.company, client)
            elif source.url:
                logger.info(f"🌐 Fetching from URL: {source.url}")
                raw_jobs = await crawler.fetch_jobs_from_url(
                    source.url, client, **source.config
                )
            else:
                raise ValueError(f"Source {source.name} has no company or url configured")

            # Log API response details
            api_response_size = len(raw_jobs)
            logger.info(f"📥 API Response: {api_response_size} jobs fetched from {source.name}")

            if DEBUG and raw_jobs:
                first_jobs = [job.to_dict() if hasattr(job, 'to_dict') else job for job in raw_jobs[:2]]
                logger.info(f"🔍 DEBUG: First 2 jobs from {source.name}:", extra={"jobs": first_jobs})

            # Process jobs through pipeline
            processed, inserted, duplicates, errors = await self._process_jobs_for_source(
                raw_jobs, source.name, source.source_type, source.company or source.url or source.name
            )

            duration = time.time() - source_start_time
            logger.info(
                f"✅ Completed {source.name}: {processed} processed, {inserted} inserted, {duplicates} duplicates, {errors} errors ({duration:.1f}s)"
            )

            first_jobs_sample = None
            if DEBUG and raw_jobs:
                first_jobs_sample = [job.to_dict() if hasattr(job, 'to_dict') else job for job in raw_jobs[:2]]

            return CrawlResult(
                source_name=source.name,
                source_type=source.source_type,
                fetched=len(raw_jobs),
                processed=processed,
                inserted=inserted,
                duplicates=duplicates,
                errors=errors,
                duration_seconds=duration,
                api_response_size=api_response_size,
                first_jobs_sample=first_jobs_sample
            )

        except Exception as e:
            duration = time.time() - source_start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"❌ Failed {source.name}: {error_msg} ({duration:.1f}s)", exc_info=True)

            return CrawlResult(
                source_name=source.name,
                source_type=source.source_type,
                fetched=0,
                processed=0,
                inserted=0,
                duplicates=0,
                errors=1,
                duration_seconds=duration
            )

    async def _process_jobs_for_source(
        self, raw_jobs: list, source_name: str, source_type: str, source_identifier: str
    ) -> tuple[int, int, int, int]:
        """Process jobs for a source through the complete pipeline."""
        processed = 0
        inserted = 0
        duplicates = 0
        errors = 0

        async with session_factory() as session:
            company_repo = CompanyRepository(session)
            job_repo = JobRepository(session)

            for raw_job_data in raw_jobs:
                try:
                    processed += 1

                    # Normalize raw job data
                    raw_job = await normalize_raw_job(raw_job_data, source_type)
                    if raw_job is None:
                        logger.warning(f"⚠️  Raw normalization failed for job in {source_name}")
                        errors += 1
                        continue

                    # Parse job description
                    parsed_info = parse_job_description(raw_job.description)
                    parsed_success = len(parsed_info.skills) > 0 or parsed_info.experience_level is not None

                    # Create final job
                    final_job_data = {**raw_job.model_dump(), **parsed_info.model_dump()}
                    final_job = FinalJob(**final_job_data)

                    # Validate required fields (only title and apply_url are required)
                    if not final_job.title or not final_job.apply_url:
                        logger.warning(f"⚠️  Missing required fields for job in {source_name}: title={bool(final_job.title)}, apply_url={bool(final_job.apply_url)}")
                        errors += 1
                        continue

                    # Generate job ID
                    apply_url = str(final_job.apply_url)
                    job_id = generate_job_id(source_identifier, apply_url)

                    # Get or create company
                    db_company = await company_repo.get_or_create_for_source(
                        source_type=source_type,
                        identifier=source_identifier,
                        display_name=source_name,
                    )

                    # Process dates
                    posted_date = final_job.posted_date
                    if isinstance(posted_date, datetime):
                        posted_date = posted_date.date()

                    # Calculate score
                    score = calculate_job_score(
                        posted_date=posted_date,
                        salary_min=final_job.salary_min,
                        salary_max=final_job.salary_max,
                        is_remote=final_job.is_remote,
                        description=final_job.description,
                        skills=final_job.skills,
                    )

                    # Upsert job
                    db_job, created = await job_repo.upsert_job(
                        job_id=job_id,
                        company_id=db_company.id,
                        title=str(final_job.title)[:500],  # Clip to DB limits
                        location=str(final_job.location or "")[:255],
                        description=str(final_job.description),
                        apply_url=apply_url[:2048],
                        posted_date=posted_date,
                        skills=final_job.skills,
                        experience_level=final_job.experience_level,
                        salary_min=final_job.salary_min,
                        salary_max=final_job.salary_max,
                        is_remote=final_job.is_remote,
                        score=score,
                    )

                    if created:
                        inserted += 1
                        logger.debug(f"✨ Inserted new job: {final_job.title} ({source_name})")
                    else:
                        duplicates += 1
                        logger.debug(f"🔄 Updated existing job: {final_job.title} ({source_name})")

                except Exception as e:
                    errors += 1
                    logger.error(f"❌ Error processing job in {source_name}: {e}", exc_info=True)

            # Commit all changes
            await session.commit()

        return processed, inserted, duplicates, errors

    def _print_final_summary(self, summary: CrawlSummary):
        """Print comprehensive final summary."""
        logger.info("=" * 80)
        logger.info("🎯 CRAWLER ENGINE SUMMARY")
        logger.info("=" * 80)

        print(f"\n🎯 FINAL CRAWLER SUMMARY")
        print("=" * 60)
        print(f"Total Sources:           {summary.total_sources}")
        print(f"Successful Sources:      {summary.successful_sources}")
        print(f"Failed Sources:          {summary.failed_sources}")
        print(f"Total Jobs Fetched:      {summary.total_fetched}")
        print(f"Total Jobs Inserted:     {summary.total_inserted}")
        print(f"Total Duplicates:        {summary.total_duplicates}")
        print(f"Total Errors:            {summary.total_errors}")
        print(f"Total Duration:          {summary.total_duration_seconds:.1f}s")
        print()

        # Per-source-type breakdown
        print("📊 Breakdown by Source Type:")
        for source_type, count in summary.sources_by_type.items():
            type_results = [r for r in self.results if r.source_type == source_type]
            if type_results:
                fetched = sum(r.fetched for r in type_results)
                inserted = sum(r.inserted for r in type_results)
                print(f"  {source_type.upper()}: {count} sources → {fetched} fetched → {inserted} inserted")

        print()
        print("✅ CRAWL COMPLETED" if summary.failed_sources == 0 else "⚠️  CRAWL COMPLETED WITH ERRORS")


async def main():
    """Main entry point for the enhanced crawler engine."""
    # Configure logging
    settings = get_settings()
    configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)

    # Run the enhanced crawler
    engine = EnhancedCrawlerEngine()
    summary = await engine.crawl_all_sources()

    # Exit with appropriate code
    return 0 if summary.failed_sources == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)