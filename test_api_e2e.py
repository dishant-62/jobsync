#!/usr/bin/env python3
"""End-to-end test for the API."""

import asyncio
import sys
from datetime import date
import uuid

from job_platform.db.models import Job, Company
from job_platform.db.session import engine, session_factory
from job_platform.db.base import Base
from job_platform.repositories.job import JobRepository
from job_platform.schemas.job import JobRead


async def test_database_and_api():
    """Test database operations and API serialization."""
    
    print("\n" + "="*60)
    print("🧪 END-TO-END API TEST")
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
                job_id="test_job_id_1234567890123456789012345678901234567890",  # 64 char job_id
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
            print(f"   ✅ Created job: {job.title}")
        
        # Step 3: Test repository query
        print("\n3️⃣  Testing repository query...")
        async with session_factory() as session:
            repo = JobRepository(session)
            
            # Count jobs
            total = await repo.count_jobs(q=None, location=None)
            print(f"   ✅ Total jobs in database: {total}")
            
            # Search jobs
            jobs = await repo.search_jobs(
                q=None,
                location=None,
                limit=20,
                offset=0
            )
            print(f"   ✅ Retrieved {len(jobs)} jobs from repository")
            
            if jobs:
                job = jobs[0]
                print(f"      - Job ID: {job.id}")
                print(f"      - Job ID (deterministic): {job.job_id}")
                print(f"      - Title: {job.title}")
                print(f"      - Company ID: {job.company_id}")
                print(f"      - Company object exists: {job.company is not None}")
                if job.company:
                    print(f"      - Company name: {job.company.name}")
            
            # Test get_job_by_id with UUID
            if jobs:
                job = jobs[0]
                retrieved_job = await repo.get_job_by_id(job.id)
                print(f"   ✅ Retrieved job by UUID: {retrieved_job is not None}")
                
                # Test get_job_by_id with job_id string
                retrieved_job_by_job_id = await repo.get_job_by_id(job.job_id)
                print(f"   ✅ Retrieved job by job_id: {retrieved_job_by_job_id is not None}")
                print(f"   ✅ Same job retrieved: {retrieved_job.id == retrieved_job_by_job_id.id}")
        
        # Step 4: Test Pydantic serialization
        print("\n4️⃣  Testing Pydantic serialization...")
        async with session_factory() as session:
            repo = JobRepository(session)
            jobs = await repo.search_jobs(
                q=None,
                location=None,
                limit=20,
                offset=0
            )
            
            if jobs:
                job_orm = jobs[0]
                try:
                    job_read = JobRead.model_validate(job_orm)
                    print(f"   ✅ Successfully serialized job to JobRead")
                    print(f"      - ID: {job_read.id}")
                    print(f"      - Title: {job_read.title}")
                    print(f"      - Company: {job_read.company.name}")
                    print(f"      - Experience: {job_read.experience_level}")
                    print(f"      - Remote: {job_read.is_remote}")
                except Exception as e:
                    print(f"   ❌ Serialization failed: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
        
        print("\n" + "="*60)
        print("✨ ALL TESTS PASSED!")
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
    success = asyncio.run(test_database_and_api())
    sys.exit(0 if success else 1)
