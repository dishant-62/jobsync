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
# BATCHED ATS COMPANY CONFIGURATIONS
# ==============================================================================

# Greenhouse public board tokens - Batched for scalability
# https://boards.greenhouse.io/{token}
GREENHOUSE_BATCH_1 = [
    "stripe", "airbnb", "notion", "robinhood", "discord", "coinbase",
    "shopify", "datadog", "snowflake", "figma", "canva", "dropbox",
    "slack", "pinterest", "square", "reddit", "twilio", "instacart",
    "yelp", "asana", "affirm", "benchling", "brex", "checkr", "chime"
]

GREENHOUSE_BATCH_2 = [
    "cloverhealth", "coursera", "cruise", "ginkgo", "gusto", "hashicorp",
    "intercom", "khanacademy", "lime", "loom", "lyft", "medium",
    "mixpanel", "okta", "opendoor", "pagerduty", "palantir", "plaid",
    "postman", "quora", "segment", "snap", "uber", "zapier", "atlassian"
]

GREENHOUSE_BATCH_3 = [
    "box", "cloudera", "databricks", "elastic", "fastly", "github",
    "grafana", "hackerone", "jetbrains", "kong", "launchdarkly", "linear",
    "mattermost", "newrelic", "observable", "planetscale", "prisma",
    "quickbooks", "replit", "sentry", "temporal", "vercel", "adobe"
]

GREENHOUSE_BATCH_4 = [
    "salesforce", "oracle", "sap", "ibm", "intel", "amd", "nvidia",
    "qualcomm", "broadcom", "cisco", "juniper", "arista", "paloaltonetworks",
    "checkpoint", "f5", "akamai", "cloudflare", "fastly", "imperva",
    "zscaler", "crowdstrike", "paloaltonetworks", "fortinet"
]

# Combine and deduplicate Greenhouse companies
ALL_GREENHOUSE = list(set(
    GREENHOUSE_BATCH_1 + GREENHOUSE_BATCH_2 + GREENHOUSE_BATCH_3 + GREENHOUSE_BATCH_4
))

# Lever public career pages - Batched
# https://careers.{company}.com or api.lever.co/v0/postings/{company}
LEVER_BATCH_1 = [
    "netflix", "uber", "lyft", "palantir", "rippling", "brex",
    "scaleai", "flexport", "coursera", "gusto", "coinbase", "airtable",
    "superhuman", "productboard", "webflow", "figma", "discord", "postman",
    "notion", "asana", "zapier", "segment", "loom", "intercom", "datadog"
]

LEVER_BATCH_2 = [
    "hashicorp", "stripe", "shopify", "slack", "snowflake", "twilio",
    "reddit", "pinterest", "square", "dropbox", "airbnb", "robinhood",
    "canva", "instacart", "yelp", "atlassian", "box", "cloudera",
    "databricks", "elastic", "fastly", "github", "grafana", "hackerone"
]

LEVER_BATCH_3 = [
    "jetbrains", "kong", "launchdarkly", "linear", "mattermost", "newrelic",
    "observable", "planetscale", "prisma", "quickbooks", "replit", "sentry",
    "temporal", "vercel", "affirm", "benchling", "checkr", "chime",
    "cloverhealth", "cruise", "ginkgo", "khanacademy", "lime", "medium"
]

LEVER_BATCH_4 = [
    "mixpanel", "okta", "opendoor", "pagerduty", "plaid", "quora",
    "snap", "adobe", "salesforce", "oracle", "sap", "ibm", "intel",
    "amd", "nvidia", "qualcomm", "broadcom", "cisco", "juniper", "arista"
]

# Combine and deduplicate Lever companies
ALL_LEVER = list(set(
    LEVER_BATCH_1 + LEVER_BATCH_2 + LEVER_BATCH_3 + LEVER_BATCH_4
))

# Workday company identifiers - Batched
# https://{company}.myworkdayjobs.com/en-US/
WORKDAY_BATCH_1 = [
    "microsoft", "meta", "amazon", "google", "apple", "tesla",
    "nvidia", "oracle", "salesforce", "adobe", "autodesk", "servicenow"
]

WORKDAY_BATCH_2 = [
    "vmware", "splunk", "okta", "crowdstrike", "paloaltonetworks", "zscaler",
    "fortinet", "checkpoint", "f5", "akamai", "cloudflare", "fastly",
    "imperva", "qualys", "tenable", "rapid7", "darktrace", "cisco"
]

# Combine and deduplicate Workday companies
ALL_WORKDAY = list(set(
    WORKDAY_BATCH_1 + WORKDAY_BATCH_2
))

# Legacy single lists for backward compatibility
GREENHOUSE_COMPANIES = ALL_GREENHOUSE
LEVER_COMPANIES = ALL_LEVER
WORKDAY_COMPANIES = ALL_WORKDAY

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


# ==============================================================================
# SOURCE VALIDATION AND ACTIVE/FAILED SYSTEM
# ==============================================================================

@dataclass
class ValidationResult:
    """Result of source validation."""
    source: SourceConfig
    is_valid: bool
    error_message: str | None = None
    response_time: float | None = None


async def _validate_source_availability(source: SourceConfig, timeout: float = 10.0) -> ValidationResult:
    """
    Validate if a source is available by making a light request.
    
    Args:
        source: Source configuration to validate
        timeout: Request timeout in seconds
        
    Returns:
        ValidationResult with success/failure status
    """
    import asyncio
    import time
    import httpx
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if source.source_type == "greenhouse":
                # Check Greenhouse board availability
                url = f"https://boards.greenhouse.io/{source.company}"
                response = await client.head(url, follow_redirects=True)
                is_valid = response.status_code == 200
                
            elif source.source_type == "lever":
                # Check Lever API availability
                url = f"https://api.lever.co/v0/postings/{source.company}"
                response = await client.get(url)
                is_valid = response.status_code == 200 and len(response.json()) > 0
                
            elif source.source_type == "workday":
                # Check Workday careers page
                url = f"https://{source.company}.myworkdayjobs.com/en-US/"
                response = await client.head(url, follow_redirects=True)
                is_valid = response.status_code == 200
                
            elif source.source_type in {"job_board", "remote_jobs", "wellfound"}:
                # Check URL-based sources
                if source.url:
                    response = await client.head(source.url, follow_redirects=True)
                    is_valid = response.status_code == 200
                else:
                    is_valid = False
                    
            else:
                is_valid = True  # Unknown types pass validation
                
            response_time = time.time() - start_time
            
            return ValidationResult(
                source=source,
                is_valid=is_valid,
                response_time=response_time
            )
            
    except Exception as e:
        response_time = time.time() - start_time
        return ValidationResult(
            source=source,
            is_valid=False,
            error_message=str(e),
            response_time=response_time
        )


async def validate_sources_batch(sources: list[SourceConfig], batch_size: int = 20, delay: float = 1.0) -> tuple[list[SourceConfig], list[ValidationResult]]:
    """
    Validate sources in batches with delays to avoid rate limiting.
    
    Args:
        sources: List of sources to validate
        batch_size: Number of sources to validate concurrently
        delay: Delay between batches in seconds
        
    Returns:
        Tuple of (active_sources, failed_results)
    """
    active_sources: list[SourceConfig] = []
    failed_results: list[ValidationResult] = []
    
    logger.info("starting_source_validation", total_sources=len(sources), batch_size=batch_size)
    
    for i in range(0, len(sources), batch_size):
        batch = sources[i:i + batch_size]
        logger.info("validating_batch", batch_start=i, batch_end=min(i + batch_size, len(sources)))
        
        # Validate batch concurrently
        tasks = [_validate_source_availability(source) for source in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for j, result in enumerate(results):
            source = batch[j]
            
            if isinstance(result, Exception):
                # Handle unexpected errors
                failed_results.append(ValidationResult(
                    source=source,
                    is_valid=False,
                    error_message=str(result)
                ))
                logger.warning("validation_error", source=source.name, error=str(result))
                
            elif result.is_valid:
                active_sources.append(source)
                logger.info("source_valid", source=source.name, response_time=f"{result.response_time:.2f}s")
                
            else:
                failed_results.append(result)
                logger.warning("source_invalid", 
                             source=source.name, 
                             error=result.error_message,
                             response_time=f"{result.response_time:.2f}s" if result.response_time else None)
        
        # Delay between batches (except for the last one)
        if i + batch_size < len(sources):
            await asyncio.sleep(delay)
    
    logger.info("validation_completed", 
               active=len(active_sources), 
               failed=len(failed_results),
               success_rate=f"{len(active_sources)/len(sources)*100:.1f}%" if sources else "0%")
    
    return active_sources, failed_results


def save_failed_sources_to_file(failed_results: list[ValidationResult], filename: str = "failed_sources.json") -> None:
    """
    Save failed source validation results to JSON file.
    
    Args:
        failed_results: List of failed validation results
        filename: Output filename
    """
    import json
    from pathlib import Path
    
    failed_data = []
    for result in failed_results:
        failed_data.append({
            "name": result.source.name,
            "type": result.source.source_type,
            "company": result.source.company,
            "url": result.source.url,
            "error": result.error_message,
            "response_time": result.response_time
        })
    
    output_path = Path(filename)
    with open(output_path, 'w') as f:
        json.dump(failed_data, f, indent=2)
    
    logger.info("failed_sources_saved", filename=str(output_path), count=len(failed_data))


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
