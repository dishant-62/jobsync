"""Utilities for managing bulk ATS company configurations."""

from __future__ import annotations

from typing import Literal

from job_platform.crawler.sources.config import (
    GREENHOUSE_COMPANIES,
    LEVER_COMPANIES,
    WORKDAY_COMPANIES,
    get_sources,
    get_source_stats,
)
from job_platform.utils.logging import get_logger

logger = get_logger("job_platform.crawler.sources.config_utils")

AtsType = Literal["greenhouse", "lever", "workday"]


def add_companies(
    ats_type: AtsType,
    companies: list[str],
    validate: bool = True,
) -> None:
    """
    Add companies to an ATS type configuration.
    
    Updates the configuration list in place.
    
    Args:
        ats_type: ATS type ("greenhouse", "lever", "workday")
        companies: List of company identifiers to add
        validate: Whether to validate company names
        
    Raises:
        ValueError: If ATS type is unknown or validation fails
    """
    if ats_type not in {"greenhouse", "lever", "workday"}:
        raise ValueError(f"Unknown ATS type: {ats_type}")
    
    if validate:
        invalid = [c for c in companies if not c or not isinstance(c, str)]
        if invalid:
            raise ValueError(f"Invalid company identifiers: {invalid}")
    
    # Get the appropriate company list
    if ats_type == "greenhouse":
        target_list = GREENHOUSE_COMPANIES
    elif ats_type == "lever":
        target_list = LEVER_COMPANIES
    else:  # workday
        target_list = WORKDAY_COMPANIES
    
    # Add new companies (avoiding duplicates)
    added = 0
    for company in companies:
        company_lower = company.lower()
        if company_lower not in [c.lower() for c in target_list]:
            target_list.append(company_lower)
            added += 1
    
    logger.info(
        "companies_added",
        ats_type=ats_type,
        count=added,
        total=len(target_list),
    )


def remove_companies(ats_type: AtsType, companies: list[str]) -> None:
    """
    Remove companies from an ATS type configuration.
    
    Args:
        ats_type: ATS type ("greenhouse", "lever", "workday")
        companies: List of company identifiers to remove
        
    Raises:
        ValueError: If ATS type is unknown
    """
    if ats_type not in {"greenhouse", "lever", "workday"}:
        raise ValueError(f"Unknown ATS type: {ats_type}")
    
    # Get the appropriate company list
    if ats_type == "greenhouse":
        target_list = GREENHOUSE_COMPANIES
    elif ats_type == "lever":
        target_list = LEVER_COMPANIES
    else:  # workday
        target_list = WORKDAY_COMPANIES
    
    # Remove companies (case-insensitive)
    companies_lower = [c.lower() for c in companies]
    removed = 0
    for i in range(len(target_list) - 1, -1, -1):
        if target_list[i].lower() in companies_lower:
            removed_company = target_list.pop(i)
            removed += 1
    
    logger.info(
        "companies_removed",
        ats_type=ats_type,
        count=removed,
        total=len(target_list),
    )


def get_companies(ats_type: AtsType) -> list[str]:
    """
    Get all companies configured for an ATS type.
    
    Args:
        ats_type: ATS type ("greenhouse", "lever", "workday")
        
    Returns:
        List of company identifiers
        
    Raises:
        ValueError: If ATS type is unknown
    """
    if ats_type == "greenhouse":
        return GREENHOUSE_COMPANIES.copy()
    elif ats_type == "lever":
        return LEVER_COMPANIES.copy()
    elif ats_type == "workday":
        return WORKDAY_COMPANIES.copy()
    else:
        raise ValueError(f"Unknown ATS type: {ats_type}")


def print_configuration_summary() -> None:
    """Print a formatted summary of current configuration."""
    stats = get_source_stats()
    
    print("\n" + "=" * 70, flush=True)
    print("JOB AGGREGATION CONFIGURATION SUMMARY", flush=True)
    print("=" * 70, flush=True)
    
    print("\nATS-Based Sources (Company-Specific):", flush=True)
    print(f"  Greenhouse: {stats.get('greenhouse', 0)} companies")
    print(f"  Lever:      {stats.get('lever', 0)} companies")
    print(f"  Workday:    {stats.get('workday', 0)} companies")
    
    print("\nURL-Based Sources (Aggregators):", flush=True)
    print(f"  Remote Jobs:  {stats.get('remote_jobs', 0)} sources")
    print(f"  Wellfound:    {stats.get('wellfound', 0)} sources")
    print(f"  Job Boards:   {stats.get('job_board', 0)} sources")
    
    total_ats = (
        stats.get('greenhouse', 0)
        + stats.get('lever', 0)
        + stats.get('workday', 0)
    )
    total_url = (
        stats.get('remote_jobs', 0)
        + stats.get('wellfound', 0)
        + stats.get('job_board', 0)
    )
    
    print(f"\nSummary:", flush=True)
    print(f"  ATS Sources:  {total_ats}", flush=True)
    print(f"  URL Sources:  {total_url}", flush=True)
    print(f"  Total:        {stats.get('total', 0)}", flush=True)
    print("=" * 70 + "\n", flush=True)


def export_configuration_as_dict() -> dict[str, list[str]]:
    """
    Export current configuration as a dictionary.
    
    Useful for serialization or external tools.
    
    Returns:
        Dictionary with ATS types as keys and company lists as values
    """
    return {
        "greenhouse": get_companies("greenhouse"),
        "lever": get_companies("lever"),
        "workday": get_companies("workday"),
    }


def validate_all_sources() -> tuple[bool, list[str]]:
    """
    Validate all configured sources.
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors: list[str] = []
    
    try:
        sources = get_sources()
        for source in sources:
            try:
                source.validate()
            except ValueError as e:
                errors.append(f"{source.name}: {str(e)}")
    except Exception as e:
        errors.append(f"Error during validation: {str(e)}")
    
    is_valid = len(errors) == 0
    
    if is_valid:
        logger.info("configuration_valid", total_sources=len(sources))
    else:
        logger.error("configuration_invalid", error_count=len(errors))
    
    return is_valid, errors
