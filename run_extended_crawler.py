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

from job_platform.crawler.sources.config import (
    get_sources, 
    validate_sources_batch, 
    save_failed_sources_to_file
)
from job_platform.pipeline.main_pipeline import run_main_pipeline
from job_platform.utils.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger("job_platform.extended_crawler")

async def run_extended_crawler():
    """Run the crawler with extended company coverage and validation."""

    logger.info("starting_extended_crawler")

    # Load and validate sources
    try:
        all_sources = get_sources()
        logger.info(
            "sources_loaded",
            total_sources=len(all_sources),
        )

        print("🚀 Starting Extended Job Crawler with Validation"        print(f"📊 Total Sources: {len(all_sources)}")
        print()

    except Exception as e:
        logger.error("config_load_error", error=str(e))
        print(f"❌ Configuration error: {e}")
        return 1

    # Step 1: Pre-validation of sources
    print("🔍 Step 1: Pre-validating source availability...")
    print("This checks if ATS endpoints are accessible before full crawling")
    print()

    try:
        active_sources, failed_results = await validate_sources_batch(
            all_sources, 
            batch_size=20,  # Validate 20 sources concurrently
            delay=2.0       # 2 second delay between batches
        )
        
        print(f"✅ Validation complete: {len(active_sources)} active, {len(failed_results)} failed")
        print()

        # Save failed sources for debugging
        if failed_results:
            save_failed_sources_to_file(failed_results)
            print("💾 Failed sources saved to 'failed_sources.json'")
            print()

    except Exception as e:
        logger.error("validation_error", error=str(e))
        print(f"❌ Validation error: {e}")
        return 1

    if not active_sources:
        print("❌ No active sources found. Cannot proceed with crawling.")
        return 1

    # Step 2: Run pipeline on active sources with batching
    print("🔄 Step 2: Running integrated pipeline on active sources...")
    print("Processing in batches to ensure reliability")
    print()

    try:
        # Run pipeline with batching (already implemented in main_pipeline)
        result = await run_main_pipeline(
            sources=active_sources,
            parallel=True, 
            max_concurrent=3  # Conservative concurrency
        )

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

        # Print comprehensive summary
        print("📈 FINAL SUMMARY"        print("=" * 60)
        print(f"Total Companies Configured:  {len(all_sources)}")
        print(f"Active Sources Validated:    {len(active_sources)}")
        print(f"Failed Sources:              {len(failed_results)}")
        print()
        print(f"Sources Processed:           {metrics.sources_processed}")
        print(f"Sources Successful:          {metrics.sources_successful}")
        print(f"Sources Failed:              {metrics.sources_failed}")
        print()
        print(f"Jobs Processed:              {metrics.jobs_processed}")
        print(f"Parsing Success:             {metrics.parsing_success}")
        print(f"Parsing Failures:            {metrics.parsing_failures}")
        print(f"Insert Success:              {metrics.insert_success}")
        print(f"Insert Failures:             {metrics.insert_failures}")
        print(f"Duplicates Found:            {metrics.duplicates_found}")
        print()

        # Per-ATS breakdown
        greenhouse_results = [r for r in result.source_results if r.source_type == "greenhouse"]
        lever_results = [r for r in result.source_results if r.source_type == "lever"]
        workday_results = [r for r in result.source_results if r.source_type == "workday"]

        if greenhouse_results:
            gh_fetched = sum(r.fetched for r in greenhouse_results)
            gh_inserted = sum(r.inserted for r in greenhouse_results)
            print(f"🌱 Greenhouse ATS: {gh_fetched} jobs fetched, {gh_inserted} inserted")

        if lever_results:
            lv_fetched = sum(r.fetched for r in lever_results)
            lv_inserted = sum(r.inserted for r in lever_results)
            print(f"⚡ Lever ATS: {lv_fetched} jobs fetched, {lv_inserted} inserted")

        if workday_results:
            wd_fetched = sum(r.fetched for r in workday_results)
            wd_inserted = sum(r.inserted for r in workday_results)
            print(f"🏢 Workday ATS: {wd_fetched} jobs fetched, {wd_inserted} inserted")

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