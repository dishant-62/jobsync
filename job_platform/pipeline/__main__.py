"""CLI entry point for job pipeline."""

from job_platform.pipeline.run_all_sources import main_sync

if __name__ == "__main__":
    exit(main_sync())
