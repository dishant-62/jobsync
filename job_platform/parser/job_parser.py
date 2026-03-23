"""Job description parsing layer that extracts structured information from raw text."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import structlog

from job_platform.models.domain.job import ParsedJob

logger = structlog.get_logger(__name__)


class JobParser:
    """
    Parser for extracting structured information from job descriptions.

    Extracts skills, experience level, salary range, and remote work status
    using keyword matching and regex patterns.
    """

    def __init__(self, skills_file: str | Path | None = None):
        """
        Initialize the job parser.

        Args:
            skills_file: Path to JSON file containing skills list. If None,
                        uses default location.
        """
        self.skills_file = skills_file or Path(__file__).parent.parent / "data" / "skills.json"
        self._skills_list: list[str] = []
        self._load_skills()

    def _load_skills(self) -> None:
        """Load skills list from JSON file."""
        try:
            with open(self.skills_file, 'r', encoding='utf-8') as f:
                self._skills_list = json.load(f)
            logger.info("skills_loaded", count=len(self._skills_list))
        except FileNotFoundError:
            logger.warning("skills_file_not_found", file=str(self.skills_file))
            self._skills_list = []
        except json.JSONDecodeError as e:
            logger.error("skills_file_invalid_json", error=str(e))
            self._skills_list = []

    def _extract_skills(self, description: str) -> list[str]:
        """
        Extract technical skills from job description using keyword matching.

        Args:
            description: Job description text

        Returns:
            List of matched skills (case-insensitive)
        """
        if not description or not self._skills_list:
            return []

        description_lower = description.lower()
        matched_skills = []

        for skill in self._skills_list:
            # Check for exact word match (with word boundaries)
            skill_pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(skill_pattern, description_lower):
                matched_skills.append(skill)

        return matched_skills

    def _extract_experience_level(self, description: str) -> str | None:
        """
        Extract experience level from job description.

        Detects patterns like:
        - "0-2 years" or "1-3 years" → entry
        - "3-5 years" or "2-4 years" → mid
        - "5+ years" or "7-10 years" → senior

        Args:
            description: Job description text

        Returns:
            Experience level: "entry", "mid", "senior", or None
        """
        if not description:
            return None

        description_lower = description.lower()

        # Senior level patterns (highest priority)
        senior_patterns = [
            r'\b5\+?\s*years?\b',
            r'\b[6-9]\s*years?\b',
            r'\b1[0-9]\s*years?\b',
            r'\b7-1[0-9]\s*years?\b',
            r'\b8-1[0-9]\s*years?\b',
            r'\b9-1[0-9]\s*years?\b',
            r'\b10\+?\s*years?\b',
        ]

        # Mid level patterns
        mid_patterns = [
            r'\b[2-4]-(?:3|4|5|6)\s*years?\b',
            r'\b3-5\s*years?\b',
            r'\b2-5\s*years?\b',
            r'\b4-6\s*years?\b',
        ]

        # Entry level patterns (lowest priority)
        entry_patterns = [
            r'\b0-2\s*years?\b',
            r'\b1-3\s*years?\b',
            r'\b0-3\s*years?\b',
            r'\b1-2\s*years?\b',
        ]

        # Check senior patterns first
        for pattern in senior_patterns:
            if re.search(pattern, description_lower):
                return "senior"

        # Check mid patterns
        for pattern in mid_patterns:
            if re.search(pattern, description_lower):
                return "mid"

        # Check entry patterns
        for pattern in entry_patterns:
            if re.search(pattern, description_lower):
                return "entry"

        return None

    def _extract_salary(self, description: str) -> tuple[int | None, int | None]:
        """
        Extract salary range from job description using regex.

        Supports various formats:
        - ₹50,000 - ₹80,000
        - $60k - $90k
        - €40,000 - €60,000
        - 5-8 LPA
        - $100,000 per year

        Args:
            description: Job description text

        Returns:
            Tuple of (min_salary, max_salary) in USD, or (None, None) if not found
        """
        if not description:
            return None, None

        # Currency patterns with multipliers for conversion to USD
        currency_patterns = [
            # Indian Rupee (₹) - convert to USD (approx 1 USD = 83 INR)
            (r'₹\s*([\d,]+)(?:\s*-\s*₹\s*([\d,]+))?', 1/83),
            # US Dollar ($)
            (r'\$\s*([\d,]+)(?:\s*-\s*\$\s*([\d,]+))?', 1.0),
            # Euro (€) - convert to USD (approx 1 USD = 0.92 EUR)
            (r'€\s*([\d,]+)(?:\s*-\s*€\s*([\d,]+))?', 1/0.92),
            # LPA (Lakhs Per Annum) - convert to USD (1 LPA ≈ 12000 USD)
            (r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*LPA', 12000),
            (r'(\d+(?:\.\d+)?)\s*LPA', 12000),
            # Per year patterns
            (r'\$\s*([\d,]+)\s*per\s*year', 1.0),
            (r'([\d,]+)\s*per\s*year', 1.0),
        ]

        for pattern, multiplier in currency_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            if matches:
                # Process the first match
                match = matches[0]
                if isinstance(match, tuple):
                    # Range pattern (min-max)
                    min_val, max_val = match
                    if min_val and max_val:
                        try:
                            min_salary = int(float(min_val.replace(',', '')) * multiplier)
                            max_salary = int(float(max_val.replace(',', '')) * multiplier)
                            return min_salary, max_salary
                        except ValueError:
                            continue
                    elif min_val:
                        # Single value
                        try:
                            salary = int(float(min_val.replace(',', '')) * multiplier)
                            return salary, salary
                        except ValueError:
                            continue
                else:
                    # Single value pattern
                    try:
                        salary = int(float(match.replace(',', '')) * multiplier)
                        return salary, salary
                    except ValueError:
                        continue

        return None, None

    def _extract_remote_status(self, description: str) -> bool:
        """
        Detect if job allows remote work.

        Args:
            description: Job description text

        Returns:
            True if remote work is mentioned, False otherwise
        """
        if not description:
            return False

        description_lower = description.lower()

        # Remote work indicators
        remote_keywords = [
            "remote",
            "work from home",
            "wfh",
            "remote work",
            "remote position",
            "remote opportunity",
            "fully remote",
            "partially remote",
            "hybrid remote",
            "telecommute",
            "virtual",
            "distributed team",
        ]

        for keyword in remote_keywords:
            if keyword in description_lower:
                return True

        return False

    def parse_job_description(self, description: str) -> ParsedJob:
        """
        Parse job description and extract structured information.

        Args:
            description: Raw job description text

        Returns:
            ParsedJob with extracted information
        """
        if not description:
            logger.warning("empty_description_provided")
            return ParsedJob()

        # Extract all fields
        skills = self._extract_skills(description)
        experience_level = self._extract_experience_level(description)
        salary_min, salary_max = self._extract_salary(description)
        is_remote = self._extract_remote_status(description)

        parsed_job = ParsedJob(
            skills=skills,
            experience_level=experience_level,
            salary_min=salary_min,
            salary_max=salary_max,
            is_remote=is_remote,
        )

        logger.info(
            "job_description_parsed",
            skills_count=len(skills),
            experience_level=experience_level,
            salary_range=f"{salary_min}-{salary_max}" if salary_min or salary_max else None,
            is_remote=is_remote,
        )

        return parsed_job


# Global parser instance for convenience
_default_parser = None


def get_job_parser() -> JobParser:
    """Get the default job parser instance."""
    global _default_parser
    if _default_parser is None:
        _default_parser = JobParser()
    return _default_parser


def parse_job_description(description: str) -> ParsedJob:
    """
    Convenience function to parse a job description.

    Args:
        description: Raw job description text

    Returns:
        ParsedJob with extracted information
    """
    return get_job_parser().parse_job_description(description)