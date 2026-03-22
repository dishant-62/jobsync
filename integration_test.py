#!/usr/bin/env python3
"""Integration test for unified scraper and parser."""

import asyncio
from job_platform.scraper.unified_scraper import normalize_raw_job
from job_platform.parser.job_parser import parse_job_description
from job_platform.models.domain.job import FinalJob

async def test_integration():
    """Test the complete flow from raw data to final job."""

    # Sample raw job data
    raw_data = {
        'title': 'Senior Python Developer',
        'company': 'TechCorp',
        'location': 'San Francisco, CA',
        'description': '''
        We are looking for a Senior Python Developer with 5+ years of experience.

        Required Skills:
        - Python, Django, FastAPI
        - React, JavaScript, TypeScript
        - AWS, Docker, Kubernetes
        - PostgreSQL, Redis

        Experience: 5+ years in software development
        Salary: $130,000 - $160,000 per year
        Location: This is a remote position

        Requirements:
        - Bachelor's degree in Computer Science
        - Experience with agile development
        - Strong problem-solving skills
        ''',
        'apply_url': 'https://example.com/jobs/123',
        'posted_date': '2024-03-20T10:00:00Z'
    }

    print("=== Testing Unified Scraper ===")

    # Step 1: Normalize raw data
    raw_job = await normalize_raw_job(raw_data, 'greenhouse')
    if not raw_job:
        print("❌ Raw job normalization failed")
        return

    print("✅ Raw job normalized:")
    print(f"  Title: {raw_job.title}")
    print(f"  Company: {raw_job.company}")
    print(f"  Description length: {len(raw_job.description)} chars")

    print("\n=== Testing Parser ===")

    # Step 2: Parse description
    parsed_job = parse_job_description(raw_job.description)

    print("✅ Job parsed:")
    print(f"  Skills found: {len(parsed_job.skills)}")
    print(f"  Skills: {parsed_job.skills[:5]}..." if len(parsed_job.skills) > 5 else f"  Skills: {parsed_job.skills}")
    print(f"  Experience Level: {parsed_job.experience_level}")
    print(f"  Salary Range: {parsed_job.salary_min} - {parsed_job.salary_max}")
    print(f"  Is Remote: {parsed_job.is_remote}")

    print("\n=== Testing Final Job ===")

    # Step 3: Combine into final job
    final_job_data = {**raw_job.model_dump(), **parsed_job.model_dump()}
    final_job = FinalJob(**final_job_data)

    print("✅ Final job created:")
    print(f"  Title: {final_job.title}")
    print(f"  Company: {final_job.company}")
    print(f"  Skills: {len(final_job.skills)}")
    print(f"  Experience: {final_job.experience_level}")
    print(f"  Remote: {final_job.is_remote}")

    print("\n🎉 Integration test passed!")

if __name__ == "__main__":
    asyncio.run(test_integration())