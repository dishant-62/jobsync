"""Registry mapping crawler types to implementations."""

from __future__ import annotations

from typing import Any

from job_platform.crawler.base import BaseCrawler
from job_platform.crawler.sources.greenhouse import GreenhouseCrawler
from job_platform.crawler.sources.lever import LeverCrawler
from job_platform.crawler.sources.workday import WorkdayCrawler
from job_platform.crawler.sources.job_board import JobBoardCrawler
from job_platform.crawler.sources.remote_jobs import RemoteJobsCrawler
from job_platform.crawler.sources.wellfound import WellfoundCrawler


class CrawlerRegistry:
    """Registry for crawler implementations keyed by type."""

    def __init__(self):
        """Initialize registry with all crawler implementations."""
        self._crawlers: dict[str, BaseCrawler] = {
            "greenhouse": GreenhouseCrawler(),
            "lever": LeverCrawler(),
            "workday": WorkdayCrawler(),
            "job_board": JobBoardCrawler(),
            "remote_jobs": RemoteJobsCrawler(),
            "wellfound": WellfoundCrawler(),
        }

    def get(self, crawler_type: str) -> BaseCrawler:
        """
        Get crawler by type.
        
        Args:
            crawler_type: Crawler type identifier
            
        Returns:
            Crawler instance
            
        Raises:
            ValueError: If crawler type is not registered
        """
        if crawler_type not in self._crawlers:
            raise ValueError(
                f"Unknown crawler type: {crawler_type}. "
                f"Available: {list(self._crawlers.keys())}"
            )
        return self._crawlers[crawler_type]

    def register(self, crawler_type: str, crawler: BaseCrawler) -> None:
        """
        Register a new crawler type.
        
        Args:
            crawler_type: Unique crawler identifier
            crawler: Crawler instance
        """
        if crawler_type in self._crawlers:
            raise ValueError(f"Crawler type {crawler_type} already registered")
        self._crawlers[crawler_type] = crawler

    def list_crawlers(self) -> list[str]:
        """
        List all registered crawler types.
        
        Returns:
            List of crawler type identifiers
        """
        return list(self._crawlers.keys())


# Global registry instance
_REGISTRY = CrawlerRegistry()


def get_registry() -> CrawlerRegistry:
    """
    Get the global crawler registry.
    
    Returns:
        Shared registry instance
    """
    return _REGISTRY


def get_crawler(crawler_type: str) -> BaseCrawler:
    """
    Get a crawler from the global registry.
    
    Args:
        crawler_type: Crawler type identifier
        
    Returns:
        Crawler instance
        
    Raises:
        ValueError: If crawler type is not registered
    """
    return _REGISTRY.get(crawler_type)
