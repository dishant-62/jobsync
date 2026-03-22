"""Source configuration for job crawlers.

Define all job sources here. Each source specifies:
- type: Crawler type identifier
- company: For ATS-based sources (company board token)
- url: For URL-based sources
- selectors: For generic job board selectors (CSS)
- kwargs: Additional configuration specific to the source
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceConfig:
    """Configuration for a single job source."""

    name: str
    """Human-readable name (e.g., "Stripe Greenhouse")"""
    
    source_type: str
    """Crawler type: greenhouse, lever, workday, job_board, remote_jobs, wellfound"""
    
    company: str | None = None
    """Company identifier for ATS-based sources (board token, company domain, etc.)"""
    
    url: str | None = None
    """URL for URL-based sources (job boards, aggregators)"""
    
    selectors: dict[str, str] = field(default_factory=dict)
    """CSS selectors for generic job board parsing"""
    
    config: dict[str, Any] = field(default_factory=dict)
    """Additional source-specific configuration"""

    def validate(self) -> None:
        """Validate source configuration."""
        if self.source_type not in {
            "greenhouse",
            "lever",
            "workday",
            "job_board",
            "remote_jobs",
            "wellfound",
        }:
            raise ValueError(f"Unknown source type: {self.source_type}")

        # Company-based sources need company identifier
        if self.source_type in {"greenhouse", "lever", "workday", "wellfound"}:
            if not self.company:
                raise ValueError(
                    f"{self.source_type} requires 'company' field"
                )

        # URL-based sources need URL
        if self.source_type in {"job_board", "remote_jobs"}:
            if not self.url:
                raise ValueError(f"{self.source_type} requires 'url' field")


# ==============================================================================
# EXAMPLE CONFIGURATIONS - ADD YOUR SOURCES HERE
# ==============================================================================

SOURCES: list[SourceConfig] = [
    # =========================================================================
    # Greenhouse Boards
    # =========================================================================
    SourceConfig(
        name="Stripe Greenhouse",
        source_type="greenhouse",
        company="stripe",
    ),
    SourceConfig(
        name="Airbnb Greenhouse",
        source_type="greenhouse",
        company="airbnb",
    ),
    SourceConfig(
        name="Figma Greenhouse",
        source_type="greenhouse",
        company="figma",
    ),
    
    # =========================================================================
    # Lever Boards
    # =========================================================================
    SourceConfig(
        name="Netflix Lever",
        source_type="lever",
        company="netflix",
    ),
    SourceConfig(
        name="Notion Lever",
        source_type="lever",
        company="notion",
    ),
    
    # =========================================================================
    # Workday
    # =========================================================================
    SourceConfig(
        name="Microsoft Workday",
        source_type="workday",
        company="microsoft",
    ),
    SourceConfig(
        name="Meta Workday",
        source_type="workday",
        company="meta",
    ),
    
    # =========================================================================
    # Remote Job Aggregators
    # =========================================================================
    SourceConfig(
        name="RemoteOK Jobs",
        source_type="remote_jobs",
        url="https://remoteok.com",
        config={"category": "tech"},
    ),
    SourceConfig(
        name="WeWork Remotely",
        source_type="remote_jobs",
        url="https://weworkremotely.com",
        config={"category": "tech"},
    ),
    
    # =========================================================================
    # Generic Job Boards (with CSS selectors)
    # =========================================================================
    # Example: HackerNews Job Postings (would need real selectors)
    # SourceConfig(
    #     name="HackerNews Jobs",
    #     source_type="job_board",
    #     url="https://news.ycombinator.com/jobs",
    #     selectors={
    #         "job_item": ".athing",
    #         "title": ".titleline > a",
    #         "url": ".titleline > a[href]",
    #         "company": ".subtext",
    #     },
    # ),
    
    # =========================================================================
    # Wellfound (Startup Jobs)
    # =========================================================================
    SourceConfig(
        name="Wellfound Jobs",
        source_type="wellfound",
        url="https://wellfound.com",
        config={"roles": ["software-engineer"], "locations": ["remote", "us"]},
    ),
]


def get_sources() -> list[SourceConfig]:
    """
    Get all configured sources.
    
    Returns:
        List of source configurations
        
    Raises:
        ValueError: If any source has invalid configuration
    """
    for source in SOURCES:
        source.validate()
    return SOURCES


def get_sources_by_type(source_type: str) -> list[SourceConfig]:
    """
    Get all sources of a specific type.
    
    Args:
        source_type: Crawler type identifier
        
    Returns:
        List of matching source configurations
    """
    return [s for s in get_sources() if s.source_type == source_type]


def get_source_by_name(name: str) -> SourceConfig | None:
    """
    Get a specific source by name.
    
    Args:
        name: Source name
        
    Returns:
        Source configuration or None if not found
    """
    for source in get_sources():
        if source.name == name:
            return source
    return None
