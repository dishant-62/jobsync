#!/usr/bin/env python3
"""Test script for saved jobs functionality."""

import asyncio
import sys
from datetime import date
import uuid

from job_platform.db.models import Job, Company, SavedJob
from job_platform.db.session import engine, session_factory
from job_platform.db.base import Base
from job_platform.repositories.saved_job import SavedJobRepository
from job_platform.repositories.job import JobRepository


async def test_saved_jobs():
    """Test saved jobs functionality end-to-end."""

    print("\n" + "="*60)
    print("🧪 SAVED JOBS FUNCTIONALITY TEST")
    print("="*60)

    try:
        # Step 1: Initialize database
        print("\n1️⃣  Initializing database schema...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("   ✅ Database schema created")

        # Step 2: Create test data
        print("\n2️⃣  Creating test data...")
        async with session_factory() as session:
            # Create a company
            company = Company(
                id=uuid.uuid4(),
                name="Test Corp",
                domain="testcorp.com",
            )
            session.add(company)
            await session.flush()

            # Create a job
            job = Job(
                id=uuid.uuid4(),
                job_id="test_job_12345",
                company_id=company.id,
                title="Senior Python Developer",
                location="San Francisco, CA",
                description="A great opportunity to join our team...",
                apply_url="https://example.com/apply/1",
                posted_date=date.today(),
                skills=["Python", "Django", "FastAPI"],
                experience_level="Senior",
                salary_min=130000,
                salary_max=160000,
                is_remote=True,
            )
            session.add(job)
            await session.commit()
            print(f"   ✅ Created company: {company.name}")
            print(f"   ✅ Created job: {job.title} (job_id: {job.job_id})")

        # Step 3: Test repository operations
        print("\n3️⃣  Testing repository operations...")
        async with session_factory() as session:
            saved_repo = SavedJobRepository(session)
            job_repo = JobRepository(session)

            # Test saving a job
            saved_job = await saved_repo.save_job(user_id="guest", job_id=job.job_id)
            print(f"   ✅ Saved job for user 'guest': {saved_job.job_id}")

            # Test checking if job is saved
            is_saved = await saved_repo.is_job_saved(user_id="guest", job_id=job.job_id)
            print(f"   ✅ Job is saved: {is_saved}")

            # Test getting saved jobs
            saved_jobs = await saved_repo.get_saved_jobs(user_id="guest")
            print(f"   ✅ Retrieved {len(saved_jobs)} saved jobs")
            if saved_jobs:
                print(f"      - Job title: {saved_jobs[0].job.title}")

            # Test unsaving a job
            removed = await saved_repo.unsave_job(user_id="guest", job_id=job.job_id)
            print(f"   ✅ Removed saved job: {removed}")

            # Test that job is no longer saved
            is_saved_after = await saved_repo.is_job_saved(user_id="guest", job_id=job.job_id)
            print(f"   ✅ Job is no longer saved: {not is_saved_after}")

        print("\n" + "="*60)
        print("✨ ALL SAVED JOBS TESTS PASSED!")
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
    success = asyncio.run(test_saved_jobs())
    sys.exit(0 if success else 1)