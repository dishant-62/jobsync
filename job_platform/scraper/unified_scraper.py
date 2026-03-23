"""Unified scraping layer that converts raw crawler data into standardized job format."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import structlog
from pydantic import ValidationError

from job_platform.models.domain.job import RawJob

logger = structlog.get_logger(__name__)


def _clean_html_description(description: str) -> str:
    """
    Clean HTML tags and normalize whitespace from job descriptions.

    Args:
        description: Raw description with potential HTML

    Returns:
        Cleaned description with HTML removed and whitespace normalized
    """
    if not description:
        return ""

    # Remove HTML tags
    clean_text = re.sub(r"<[^>]+>", "", description)

    # Decode common HTML entities
    clean_text = clean_text.replace("&nbsp;", " ")
    clean_text = clean_text.replace("&amp;", "&")
    clean_text = clean_text.replace("&lt;", "<")
    clean_text = clean_text.replace("&gt;", ">")
    clean_text = clean_text.replace("&quot;", '"')
    clean_text = clean_text.replace("&#39;", "'")

    # Normalize whitespace
    clean_text = re.sub(r"\s+", " ", clean_text)
    clean_text = clean_text.strip()

    return clean_text


def _normalize_greenhouse_job(raw_data: dict[str, Any], source: str) -> dict[str, Any]:
    """
    Normalize raw Greenhouse job data to unified format.

    Expected raw fields: title, location, apply_url, description, posted_date, company
    """
    return {
        "title": raw_data.get("title", "").strip(),
        "company": raw_data.get("company", "").strip(),
        "location": raw_data.get("location", "").strip() or None,
        "description": _clean_html_description(raw_data.get("description", "")),
        "apply_url": raw_data.get("apply_url", "").strip(),
        "posted_date": raw_data.get("posted_date"),
        "source": source,
    }


def _normalize_lever_job(raw_data: dict[str, Any], source: str) -> dict[str, Any]:
    """
    Normalize raw Lever job data to unified format.

    Expected raw fields: title, company_name, location, description, apply_url, posted_date
    """
    return {
        "title": raw_data.get("title", "").strip(),
        "company": raw_data.get("company_name", "").strip(),
        "location": raw_data.get("location", "").strip() or None,
        "description": _clean_html_description(raw_data.get("description", "")),
        "apply_url": raw_data.get("apply_url", "").strip(),
        "posted_date": raw_data.get("posted_date"),
        "source": source,
    }


def _normalize_workday_job(raw_data: dict[str, Any], source: str) -> dict[str, Any]:
    """
    Normalize raw Workday job data to unified format.

    Expected raw fields: title, company, location, description, apply_url, posted_date
    """
    return {
        "title": raw_data.get("title", "").strip(),
        "company": raw_data.get("company", "").strip(),
        "location": raw_data.get("location", "").strip() or None,
        "description": _clean_html_description(raw_data.get("description", "")),
        "apply_url": raw_data.get("apply_url", "").strip(),
        "posted_date": raw_data.get("posted_date"),
        "source": source,
    }


def _normalize_generic_job(raw_data: dict[str, Any], source: str) -> dict[str, Any]:
    """
    Normalize raw job data from generic sources to unified format.

    This is a fallback for sources that don't have specific normalization.
    """
    return {
        "title": raw_data.get("title", "").strip(),
        "company": raw_data.get("company", "").strip(),
        "location": raw_data.get("location", "").strip() or None,
        "description": _clean_html_description(raw_data.get("description", "")),
        "apply_url": raw_data.get("apply_url", "").strip(),
        "posted_date": raw_data.get("posted_date"),
        "source": source,
    }


async def normalize_raw_job(raw_data: dict[str, Any], source: str) -> RawJob | None:
    """
    Convert raw crawler data into standardized RawJob format.

    This function handles per-source field mapping, data cleaning, and validation.
    If required fields are missing or invalid, returns None (job is skipped).

    Args:
        raw_data: Raw job data from crawler (dict with source-specific fields)
        source: Source identifier (greenhouse, lever, workday, etc.)

    Returns:
        RawJob instance if successful, None if job should be skipped

    Raises:
        Does not raise exceptions - logs errors and returns None for invalid jobs
    """
    try:
        # Select normalization function based on source
        if source == "greenhouse":
            normalized_data = _normalize_greenhouse_job(raw_data, source)
        elif source == "lever":
            normalized_data = _normalize_lever_job(raw_data, source)
        elif source == "workday":
            normalized_data = _normalize_workday_job(raw_data, source)
        else:
            # Fallback for unknown sources
            normalized_data = _normalize_generic_job(raw_data, source)

        # Validate required fields
        if not normalized_data.get("title"):
            logger.warning(
                "job_normalization_skipped_missing_title",
                source=source,
                company=normalized_data.get("company", "unknown"),
                reason="missing_title"
            )
            return None

        if not normalized_data.get("company"):
            logger.warning(
                "job_normalization_skipped_missing_company",
                source=source,
                title=normalized_data.get("title", "unknown"),
                reason="missing_company"
            )
            return None

        if not normalized_data.get("apply_url"):
            logger.warning(
                "job_normalization_skipped_missing_apply_url",
                source=source,
                company=normalized_data.get("company", "unknown"),
                title=normalized_data.get("title", "unknown"),
                reason="missing_apply_url"
            )
            return None

        # Create and validate RawJob instance
        raw_job = RawJob(**normalized_data)

        logger.info(
            "job_normalization_success",
            source=source,
            company=raw_job.company,
            title=raw_job.title,
            apply_url=str(raw_job.apply_url)
        )

        return raw_job

    except ValidationError as e:
        logger.error(
            "job_normalization_validation_error",
            source=source,
            company=raw_data.get("company", "unknown"),
            title=raw_data.get("title", "unknown"),
            validation_errors=e.errors()
        )
        return None

    except Exception as e:
        logger.error(
            "job_normalization_unexpected_error",
            source=source,
            company=raw_data.get("company", "unknown"),
            title=raw_data.get("title", "unknown"),
            error=str(e)
        )
        return None