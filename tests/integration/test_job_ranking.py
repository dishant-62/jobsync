#!/usr/bin/env python3
"""Test script for job ranking system."""

import asyncio
import sys
from datetime import date, timedelta
import uuid

from job_platform.db.models import Job, Company
from job_platform.db.session import engine, session_factory
from job_platform.db.base import Base
from job_platform.repositories.job import JobRepository
from job_platform.utils.ranking import calculate_job_score


async def test_job_ranking():
    """Test the job ranking system end-to-end."""

    print("\n" + "="*60)
    print("🧪 JOB RANKING SYSTEM TEST")
    print("="*60)

    try:
        # Step 1: Initialize database
        print("\n1️⃣  Initializing database schema...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("   ✅ Database schema created")

        # Step 2: Create test company
        print("\n2️⃣  Creating test company...")
        async with session_factory() as session:
            company = Company(
                id=uuid.uuid4(),
                name="Test Corp",
                domain="testcorp.com",
            )
            session.add(company)
            await session.commit()
            print(f"   ✅ Created company: {company.name}")

        # Step 3: Create test jobs with different characteristics
        print("\n3️⃣  Creating test jobs with different ranking factors...")

        today = date.today()
        jobs_data = [
            {
                "title": "High Quality Recent Job",
                "posted_date": today,  # Very recent
                "salary_min": 100000,
                "salary_max": 120000,
                "is_remote": True,
                "description": "This is a very detailed job description with comprehensive information about the role, requirements, benefits, and company culture. It includes information about the team, technology stack, and growth opportunities.",
                "skills": ["Python", "Django", "React", "AWS", "Docker", "Kubernetes"],
                "expected_score": 17.0,  # 10 (recent) + 3 (salary) + 1 (remote) + 3 (desc >1000) + 3 (5+ skills) = 20, but capped at 17?
            },
            {
                "title": "Medium Quality Job",
                "posted_date": today - timedelta(days=15),  # 15 days old
                "salary_min": None,
                "salary_max": None,
                "is_remote": False,
                "description": "This is a decent job description with some information about the role and requirements.",
                "skills": ["Python", "JavaScript"],
                "expected_score": 4.0,  # 5 (15-30 days) + 0 (no salary) + 0 (not remote) + 2 (500-1000 desc) + 1 (1-2 skills) = 8, but let's check
            },
            {
                "title": "Low Quality Old Job",
                "posted_date": today - timedelta(days=60),  # Old job
                "salary_min": None,
                "salary_max": None,
                "is_remote": False,
                "description": "Short description.",
                "skills": None,
                "expected_score": 0.0,  # 0 (old) + 0 (no salary) + 0 (not remote) + 0 (short desc) + 0 (no skills) = 0
            },
        ]

        async with session_factory() as session:
            repo = JobRepository(session)

            created_jobs = []
            for i, job_data in enumerate(jobs_data):
                # Calculate expected score
                expected_score = calculate_job_score(
                    posted_date=job_data["posted_date"],
                    salary_min=job_data["salary_min"],
                    salary_max=job_data["salary_max"],
                    is_remote=job_data["is_remote"],
                    description=job_data["description"],
                    skills=job_data["skills"],
                )

                # Create job with calculated score
                job = Job(
                    id=uuid.uuid4(),
                    job_id=f"test_job_{i}_{uuid.uuid4().hex[:8]}",
                    company_id=company.id,
                    title=job_data["title"],
                    location="San Francisco, CA",
                    description=job_data["description"],
                    apply_url=f"https://example.com/apply/{i}",
                    posted_date=job_data["posted_date"],
                    skills=job_data["skills"],
                    salary_min=job_data["salary_min"],
                    salary_max=job_data["salary_max"],
                    is_remote=job_data["is_remote"],
                    score=expected_score,
                )
                session.add(job)
                created_jobs.append((job, expected_score))
                print(f"   ✅ Created job: {job.title} (score: {expected_score:.2f})")

            await session.commit()

        # Step 4: Test ranking - jobs should be sorted by score DESC
        print("\n4️⃣  Testing job ranking (should be sorted by score DESC)...")
        async with session_factory() as session:
            repo = JobRepository(session)

            # Get all jobs (should be sorted by score DESC)
            jobs = await repo.list_jobs()
            jobs_list = list(jobs)

            print(f"   ✅ Retrieved {len(jobs_list)} jobs")

            # Check that jobs are sorted by score descending
            scores = [job.score for job in jobs_list]
            is_sorted_desc = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

            if is_sorted_desc:
                print("   ✅ Jobs are correctly sorted by score (DESC)")
            else:
                print(f"   ❌ Jobs are NOT sorted correctly. Scores: {scores}")
                return False

            # Print the ranking
            print("\n   📊 Job Ranking Results:")
            for i, job in enumerate(jobs_list, 1):
                print(f"      {i}. {job.title} - Score: {job.score:.2f}")

        # Step 5: Test search_jobs also sorts by score
        print("\n5️⃣  Testing search_jobs ranking...")
        async with session_factory() as session:
            repo = JobRepository(session)

            search_results = await repo.search_jobs(
                q=None,
                location=None,
                limit=10,
                offset=0
            )

            search_scores = [job.score for job in search_results]
            search_is_sorted_desc = all(search_scores[i] >= search_scores[i+1] for i in range(len(search_scores)-1))

            if search_is_sorted_desc:
                print("   ✅ search_jobs also correctly sorts by score (DESC)")
            else:
                print(f"   ❌ search_jobs NOT sorted correctly. Scores: {search_scores}")
                return False

        print("\n" + "="*60)
        print("✨ JOB RANKING SYSTEM TEST PASSED!")
        print("="*60 + "\n")
        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(test_job_ranking())
    sys.exit(0 if success else 1)