"""CLI for running the multi-source job pipeline."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

import httpx

from job_platform.crawler.sources.config import get_sources, get_sources_by_type
from job_platform.pipeline.multi_source_pipeline import (
    run_all_sources,
    run_sources_by_type,
)
from job_platform.utils.logging import configure_logging, get_logger

logger = get_logger("job_platform.cli")


def _print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 70}", file=sys.stdout)
    print(f"  {text}", file=sys.stdout)
    print(f"{'=' * 70}", file=sys.stdout)


def _print_source_result(result: Any) -> None:
    """Pretty-print a source ingestion result."""
    status = "✓ SUCCESS" if result.error is None else "✗ FAILED"
    
    print(f"\n  {result.source_name} [{result.source_type}] {status}", file=sys.stdout)
    print(f"    Fetched:           {result.fetched}", file=sys.stdout)
    print(f"    Inserted:          {result.inserted}", file=sys.stdout)
    print(f"    Duplicates:        {result.skipped_duplicates}", file=sys.stdout)
    
    if result.error:
        print(f"    Error:             {result.error}", file=sys.stdout)


def _print_summary(result: Any) -> None:
    """Pretty-print pipeline run summary."""
    _print_header("Pipeline Summary")
    
    print(f"\n  Total Sources:      {result.total_sources}", file=sys.stdout)
    print(f"  Successful:         {result.successful_sources}", file=sys.stdout)
    print(f"  Failed:             {result.failed_sources}", file=sys.stdout)
    print(f"\n  Total Fetched:      {result.total_fetched}", file=sys.stdout)
    print(f"  Total Inserted:     {result.total_inserted}", file=sys.stdout)
    print(f"  Total Duplicates:   {result.total_duplicates}", file=sys.stdout)
    print()


def _print_source_details(result: Any) -> None:
    """Print per-source details."""
    _print_header("Source Details")
    
    for source_result in result.source_results:
        _print_source_result(source_result)
    
    print()


def _list_sources() -> None:
    """List all configured sources."""
    _print_header("Configured Sources")
    
    sources = get_sources()
    if not sources:
        print("\n  No sources configured", file=sys.stdout)
        return
    
    for i, source in enumerate(sources, 1):
        print(f"\n  {i}. {source.name}", file=sys.stdout)
        print(f"     Type:         {source.source_type}", file=sys.stdout)
        if source.company:
            print(f"     Company:      {source.company}", file=sys.stdout)
        if source.url:
            print(f"     URL:          {source.url}", file=sys.stdout)
    
    print()


async def _run_all() -> int:
    """Run all sources."""
    _print_header("Running All Sources")
    
    try:
        result = await run_all_sources(parallel=True, max_concurrent=3)
        _print_summary(result)
        _print_source_details(result)
        
        return 0 if result.failed_sources == 0 else 1
    except Exception as e:
        logger.error("pipeline_error", error=str(e))
        print(f"\nError running pipeline: {e}", file=sys.stderr)
        return 1


async def _run_by_type(source_type: str) -> int:
    """Run sources of a specific type."""
    _print_header(f"Running {source_type.upper()} Sources")
    
    try:
        sources = get_sources_by_type(source_type)
        if not sources:
            print(f"\nNo sources of type '{source_type}' configured", file=sys.stdout)
            return 1
        
        result = await run_sources_by_type(source_type)
        _print_summary(result)
        _print_source_details(result)
        
        return 0 if result.failed_sources == 0 else 1
    except Exception as e:
        logger.error("pipeline_error", error=str(e))
        print(f"\nError running pipeline: {e}", file=sys.stderr)
        return 1


def _print_help() -> None:
    """Print help message."""
    _print_header("Job Pipeline CLI")
    
    print("""
  Usage: python -m job_platform.pipeline.run_all_sources [COMMAND] [OPTIONS]
  
  Commands:
    run             Run all configured sources (default)
    run TYPE        Run sources of a specific type (greenhouse, lever, etc.)
    list            List all configured sources
    help            Show this help message
    
  Examples:
    # Run all sources
    python -m job_platform.pipeline.run_all_sources run
    
    # Run only Greenhouse sources
    python -m job_platform.pipeline.run_all_sources run greenhouse
    
    # List configured sources
    python -m job_platform.pipeline.run_all_sources list
    """, file=sys.stdout)


async def main() -> int:
    """Main CLI entry point."""
    configure_logging()
    
    command = sys.argv[1] if len(sys.argv) > 1 else "run"
    
    if command == "help" or command == "--help" or command == "-h":
        _print_help()
        return 0
    
    if command == "list":
        _list_sources()
        return 0
    
    if command == "run":
        # Check for optional type argument
        source_type = sys.argv[2] if len(sys.argv) > 2 else None
        
        if source_type:
            return await _run_by_type(source_type)
        else:
            return await _run_all()
    
    # Unknown command
    print(f"Unknown command: {command}", file=sys.stderr)
    print("Run with 'help' for usage information", file=sys.stderr)
    return 1


def main_sync() -> int:
    """Synchronous wrapper for async main."""
    try:
        return asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main_sync())
