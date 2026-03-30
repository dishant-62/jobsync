"""Job ranking and scoring utilities."""

from datetime import date, datetime, timedelta
from typing import Optional


def calculate_job_score(
    posted_date: date,
    salary_min: Optional[int],
    salary_max: Optional[int],
    is_remote: bool,
    description: str,
    skills: Optional[list[str]],
) -> float:
    """Calculate a ranking score for a job based on various quality factors.

    Args:
        posted_date: When the job was posted
        salary_min: Minimum salary (if provided)
        salary_max: Maximum salary (if provided)
        is_remote: Whether the job is remote
        description: Job description text
        skills: List of required skills

    Returns:
        A float score representing job quality/relevance
    """
    score = 0.0

    # 1. Recency score (new jobs get higher scores)
    # Jobs from last 7 days: +10 points
    # Jobs from last 30 days: +5 points
    # Older jobs: +0 points
    today = date.today()
    days_since_posted = (today - posted_date).days

    if days_since_posted <= 7:
        score += 10.0
    elif days_since_posted <= 30:
        score += 5.0
    # Older jobs get 0 recency points

    # 2. Salary boost (+3 points if salary is provided)
    if salary_min is not None or salary_max is not None:
        score += 3.0

    # 3. Remote boost (+1 point for remote jobs)
    if is_remote:
        score += 1.0

    # 4. Description length score (quality signal)
    # Longer descriptions are generally more detailed/quality
    desc_length = len(description.strip())
    if desc_length > 1000:
        score += 3.0
    elif desc_length > 500:
        score += 2.0
    elif desc_length > 200:
        score += 1.0
    # Very short descriptions get 0 points

    # 5. Skills count score (relevance signal)
    # More skills listed = more specific requirements = higher relevance
    skills_count = len(skills) if skills else 0
    if skills_count >= 5:
        score += 3.0
    elif skills_count >= 3:
        score += 2.0
    elif skills_count >= 1:
        score += 1.0
    # No skills listed gets 0 points

    return score


def get_score_description(score: float) -> str:
    """Get a human-readable description of a score range."""
    if score >= 15:
        return "Excellent (very recent, comprehensive job posting)"
    elif score >= 12:
        return "Very good (recent with good details)"
    elif score >= 8:
        return "Good (recent or well-detailed)"
    elif score >= 4:
        return "Fair (some quality indicators)"
    else:
        return "Basic (minimal information)"