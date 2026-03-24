"""Utilities for job ID generation and management."""

import hashlib


def generate_job_id(company_identifier: str, apply_url: str) -> str:
    """Generate a deterministic job ID using SHA256 hash of company:URL.

    Args:
        company_identifier: Unique identifier for the company/source
        apply_url: The job's application URL

    Returns:
        A 64-character hexadecimal string representing the job ID
    """
    # Create a consistent key by combining company and URL
    key = f"{company_identifier}:{apply_url}".encode('utf-8')

    # Generate SHA256 hash and return as hex string
    return hashlib.sha256(key).hexdigest()