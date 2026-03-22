"""CLI entry point for configuration management."""

import sys
from job_platform.crawler.sources.manage import main

if __name__ == "__main__":
    sys.exit(main())
