"""Job crawler sources package."""

from job_platform.crawler.sources.greenhouse import GreenhouseCrawler
from job_platform.crawler.sources.lever import LeverCrawler
from job_platform.crawler.sources.wellfound import WellfoundCrawler
from job_platform.crawler.sources.workday import WorkdayCrawler
from job_platform.crawler.sources.remote_jobs import RemoteJobsCrawler
from job_platform.crawler.sources.job_board import JobBoardCrawler

from job_platform.crawler.sources.config import (
    SourceConfig,
    get_sources,
    get_sources_by_type,
    get_source_by_name,
    get_source_stats,
    GREENHOUSE_COMPANIES,
    LEVER_COMPANIES,
    WORKDAY_COMPANIES,
)

from job_platform.crawler.sources.config_utils import (
    add_companies,
    remove_companies,
    get_companies,
    print_configuration_summary,
    export_configuration_as_dict,
    validate_all_sources,
)

__all__ = [
    # Crawlers
    "GreenhouseCrawler",
    "LeverCrawler",
    "WorkdayCrawler",
    "JobBoardCrawler",
    "RemoteJobsCrawler",
    "WellfoundCrawler",
    # Config
    "SourceConfig",
    "get_sources",
    "get_sources_by_type",
    "get_source_by_name",
    "get_source_stats",
    # Company lists
    "GREENHOUSE_COMPANIES",
    "LEVER_COMPANIES",
    "WORKDAY_COMPANIES",
    # Config utilities
    "add_companies",
    "remove_companies",
    "get_companies",
    "print_configuration_summary",
    "export_configuration_as_dict",
    "validate_all_sources",
]
