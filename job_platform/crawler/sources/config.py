"""Source configuration for job crawlers.

Supports bulk company ingestion for ATS-based sources with automatic
SOURCES list generation, validation, and logging.

Define company lists per ATS type, and the system automatically generates
the complete SOURCES configuration with validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from job_platform.utils.logging import get_logger

logger = get_logger("job_platform.crawler.sources.config")


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
        if self.source_type in {"greenhouse", "lever", "workday"}:
            if not self.company:
                raise ValueError(
                    f"{self.source_type} requires 'company' field"
                )

        # URL-based sources need URL
        if self.source_type in {"job_board", "remote_jobs"}:
            if not self.url:
                raise ValueError(f"{self.source_type} requires 'url' field")


# ==============================================================================
# BULK ATS COMPANY CONFIGURATIONS
# ==============================================================================

# Greenhouse public board tokens
# https://boards.greenhouse.io/{token}
GREENHOUSE_COMPANIES = [
    "stripe",
    "airbnb",
    "notion",
    "robinhood",
    "discord",
    "coinbase",
    "shopify",
    "datadog",
    "snowflake",
    "figma",
    "canva",
    "dropbox",
    "slack",
    "pinterest",
    "square",
    "reddit",
    "twilio",
    "instacart",
    "yelp",
    "asana",
    # Extended list - 50+ additional companies
    "affirm", "benchling", "brex", "checkr", "chime", "cloverhealth",
    "coursera", "cruise", "ginkgo", "gusto", "hashicorp", "intercom",
    "khanacademy", "lime", "loom", "lyft", "medium", "mixpanel",
    "mongodb", "okta", "opendoor", "pagerduty", "palantir", "plaid",
    "postman", "quora", "segment", "snap", "uber", "zapier",
    "atlassian", "box", "cloudera", "databricks", "elastic", "fastly",
    "github", "grafana", "hackerone", "jetbrains", "kong", "launchdarkly",
    "linear", "mattermost", "mongodb", "newrelic", "observable", "planetscale",
    "prisma", "quickbooks", "replit", "sentry", "temporal", "vercel",
]

# Lever public career pages
# https://careers.{company}.com or api.lever.co/v0/postings/{company}
LEVER_COMPANIES = [
    "netflix",
    "uber",
    "lyft",
    "palantir",
    "rippling",
    "brex",
    "scaleai",
    "flexport",
    "coursera",
    "gusto",
    # Extended list - 50+ additional companies
    "coinbase", "airtable", "superhuman", "productboard", "webflow",
    "figma", "discord", "postman", "notion", "asana", "zapier",
    "segment", "loom", "intercom", "datadog", "hashicorp", "stripe",
    "shopify", "slack", "snowflake", "twilio", "reddit", "pinterest",
    "square", "dropbox", "airbnb", "robinhood", "canva", "instacart",
    "yelp", "atlassian", "box", "cloudera", "databricks", "elastic",
    "fastly", "github", "grafana", "hackerone", "jetbrains", "kong",
    "launchdarkly", "linear", "mattermost", "newrelic", "observable",
    "planetscale", "prisma", "quickbooks", "replit", "sentry",
    "temporal", "vercel", "affirm", "benchling", "checkr", "chime",
    "cloverhealth", "cruise", "ginkgo", "khanacademy", "lime", "medium",
    "mixpanel", "mongodb", "okta", "opendoor", "pagerduty", "plaid",
    "quora", "snap",
]

# Workday company identifiers
# https://{company}.myworkdayjobs.com/en-US/
WORKDAY_COMPANIES = [
    "microsoft",
    "meta",
    "amazon",
    "google",
    "apple",
]

# Static URL-based sources (non-ATS)
URL_SOURCES = [
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
    SourceConfig(
        name="Wellfound Jobs",
        source_type="wellfound",
        url="https://wellfound.com",
        config={"roles": ["software-engineer"], "locations": ["remote", "us"]},
    ),
]


# ==============================================================================
# INTERNAL: Helper functions for bulk generation
# ==============================================================================

def _generate_greenhouse_sources() -> list[SourceConfig]:
    """Generate SourceConfig list from Greenhouse companies."""
    return [
        SourceConfig(
            name=f"{company.title()} Greenhouse",
            source_type="greenhouse",
            company=company.lower(),
        )
        for company in GREENHOUSE_COMPANIES
    ]


def _generate_lever_sources() -> list[SourceConfig]:
    """Generate SourceConfig list from Lever companies."""
    return [
        SourceConfig(
            name=f"{company.title()} Lever",
            source_type="lever",
            company=company.lower(),
        )
        for company in LEVER_COMPANIES
    ]


def _generate_workday_sources() -> list[SourceConfig]:
    """Generate SourceConfig list from Workday companies."""
    return [
        SourceConfig(
            name=f"{company.title()} Workday",
            source_type="workday",
            company=company.lower(),
        )
        for company in WORKDAY_COMPANIES
    ]


def _remove_duplicates(sources: list[SourceConfig]) -> list[SourceConfig]:
    """
    Remove duplicate sources by (source_type, company, url).
    
    Args:
        sources: List of source configurations
        
    Returns:
        Deduplicated source list (preserves first occurrence order)
    """
    seen: set[tuple[str, str | None, str | None]] = set()
    unique_sources: list[SourceConfig] = []
    
    for source in sources:
        key = (source.source_type, source.company, source.url)
        if key not in seen:
            seen.add(key)
            unique_sources.append(source)
    
    return unique_sources


def _validate_company_names(company_list: list[str], source_type: str) -> list[str]:
    """
    Validate company names (basic checks).
    
    Args:
        company_list: List of company identifiers
        source_type: ATS type for error messages
        
    Returns:
        Validated company list
        
    Raises:
        ValueError: If company names are invalid
    """
    invalid_companies = [c for c in company_list if not c or not isinstance(c, str)]
    if invalid_companies:
        raise ValueError(
            f"{source_type}: Invalid company identifiers: {invalid_companies}"
        )
    
    # Check for duplicates within the list
    seen = set()
    duplicates = [c for c in company_list if c in seen or seen.add(c)]
    if duplicates:
        logger.warning(
            "duplicate_companies_in_list",
            source_type=source_type,
            duplicates=duplicates,
        )
    
    return company_list


# ==============================================================================
# AUTO-GENERATED SOURCES LIST
# ==============================================================================

def _generate_all_sources() -> list[SourceConfig]:
    """
    Generate complete SOURCES list from all company configurations.
    
    Returns:
        Complete, validated, deduplicated SOURCES list
    """
    # Validate company lists
    _validate_company_names(GREENHOUSE_COMPANIES, "greenhouse")
    _validate_company_names(LEVER_COMPANIES, "lever")
    _validate_company_names(WORKDAY_COMPANIES, "workday")
    
    # Generate sources from company lists
    all_sources: list[SourceConfig] = []
    
    all_sources.extend(_generate_greenhouse_sources())
    all_sources.extend(_generate_lever_sources())
    all_sources.extend(_generate_workday_sources())
    all_sources.extend(URL_SOURCES)
    
    # Remove duplicates
    unique_sources = _remove_duplicates(all_sources)
    
    # Log generation summary
    greenhouse_count = len(GREENHOUSE_COMPANIES)
    lever_count = len(LEVER_COMPANIES)
    workday_count = len(WORKDAY_COMPANIES)
    url_count = len(URL_SOURCES)
    total_count = len(unique_sources)
    
    logger.info(
        "sources_generated",
        greenhouse=greenhouse_count,
        lever=lever_count,
        workday=workday_count,
        static_urls=url_count,
        total=total_count,
    )
    
    return unique_sources


# Initialize SOURCES list from generation function
SOURCES: list[SourceConfig] = _generate_all_sources()


# ==============================================================================
# PUBLIC API FUNCTIONS
# ==============================================================================

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


def get_sources_by_company(company: str) -> list[SourceConfig]:
    """
    Get all sources for a specific company.
    
    Args:
        company: Company identifier (case-insensitive)
        
    Returns:
        List of matching source configurations for this company
    """
    company_lower = company.lower()
    return [s for s in get_sources() if s.company and s.company.lower() == company_lower]


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


def get_source_stats() -> dict[str, int]:
    """
    Get statistics about configured sources.
    
    Returns:
        Dictionary with counts per source type
    """
    sources = get_sources()
    stats: dict[str, int] = {}
    
    for source in sources:
        source_type = source.source_type
        stats[source_type] = stats.get(source_type, 0) + 1
    
    stats["total"] = len(sources)
    return stats
