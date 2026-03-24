#!/usr/bin/env python3
"""
Script to run the job crawler pipeline with extended company coverage.

This script loads the updated source configuration with 50+ additional companies
for Greenhouse and Lever ATS systems, then executes the integrated pipeline:
crawler → scraper → parser → database.

Logs comprehensive metrics including companies added, jobs fetched per ATS,
and insertion results.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from job_platform.crawler.sources.config import get_sources, get_sources_by_type
from job_platform.pipeline.main_pipeline import run_main_pipeline
from job_platform.utils.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger("job_platform.extended_crawler")

async def run_extended_crawler():
    """Run the crawler with extended company coverage."""

    logger.info("starting_extended_crawler")

    # Load and validate sources
    try:
        sources = get_sources()
        greenhouse_sources = get_sources_by_type("greenhouse")
        lever_sources = get_sources_by_type("lever")

        logger.info(
            "sources_loaded",
            total_sources=len(sources),
            greenhouse_companies=len(greenhouse_sources),
            lever_companies=len(lever_sources),
        )

        print("🚀 Starting Extended Job Crawler"        print(f"📊 Total Sources: {len(sources)}")
        print(f"🌱 Greenhouse Companies: {len(greenhouse_sources)}")
        print(f"⚡ Lever Companies: {len(lever_sources)}")
        print()

    except Exception as e:
        logger.error("config_load_error", error=str(e))
        print(f"❌ Configuration error: {e}")
        return 1

    # Run the integrated pipeline
    try:
        print("🔄 Running integrated pipeline: Crawler → Scraper → Parser → DB")
        print("This may take several minutes depending on the number of sources...")
        print()

        result = await run_main_pipeline(parallel=True, max_concurrent=3)

        # Log summary metrics
        metrics = result.metrics
        logger.info(
            "pipeline_completed",
            sources_processed=metrics.sources_processed,
            sources_successful=metrics.sources_successful,
            sources_failed=metrics.sources_failed,
            jobs_processed=metrics.jobs_processed,
            parsing_success=metrics.parsing_success,
            parsing_failures=metrics.parsing_failures,
            insert_success=metrics.insert_success,
            insert_failures=metrics.insert_failures,
            duplicates_found=metrics.duplicates_found,
        )

        # Print formatted summary
        print("📈 PIPELINE SUMMARY"        print("=" * 50)
        print(f"Sources Processed:  {metrics.sources_processed}")
        print(f"Sources Successful: {metrics.sources_successful}")
        print(f"Sources Failed:     {metrics.sources_failed}")
        print()
        print(f"Jobs Processed:     {metrics.jobs_processed}")
        print(f"Parsing Success:    {metrics.parsing_success}")
        print(f"Parsing Failures:   {metrics.parsing_failures}")
        print(f"Insert Success:     {metrics.insert_success}")
        print(f"Insert Failures:    {metrics.insert_failures}")
        print(f"Duplicates Found:   {metrics.duplicates_found}")
        print()

        # Print per-ATS breakdown
        greenhouse_results = [r for r in result.source_results if r.source_type == "greenhouse"]
        lever_results = [r for r in result.source_results if r.source_type == "lever"]

        if greenhouse_results:
            greenhouse_fetched = sum(r.fetched for r in greenhouse_results)
            greenhouse_inserted = sum(r.inserted for r in greenhouse_results)
            print(f"🌱 Greenhouse ATS: {greenhouse_fetched} jobs fetched, {greenhouse_inserted} inserted")

        if lever_results:
            lever_fetched = sum(r.fetched for r in lever_results)
            lever_inserted = sum(r.inserted for r in lever_results)
            print(f"⚡ Lever ATS: {lever_fetched} jobs fetched, {lever_inserted} inserted")

        success = metrics.sources_failed == 0
        print()
        print("✅ SUCCESS" if success else "⚠️  PARTIAL SUCCESS")
        print(f"Extended crawler completed with {metrics.sources_failed} source failures")

        return 0 if success else 1

    except Exception as e:
        logger.error("pipeline_error", error=str(e))
        print(f"❌ Pipeline error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_extended_crawler())
    sys.exit(exit_code)