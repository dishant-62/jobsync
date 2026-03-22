"""Data access repositories."""

from job_platform.repositories.company import CompanyRepository, greenhouse_board_domain
from job_platform.repositories.job import JobRepository

__all__ = ["CompanyRepository", "JobRepository", "greenhouse_board_domain"]
