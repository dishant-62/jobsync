"""
Manual DB verification script.

Run:  python -m job_platform.test_insert

Tests:
  1. Print masked DATABASE_URL
  2. Check table existence
  3. Count existing jobs
  4. Insert a test job
  5. Verify the insert
  6. Clean up the test job
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import date, datetime

from sqlalchemy import text

from job_platform.config import get_settings
from job_platform.db.session import engine, session_factory
from job_platform.db.models import Company, Job


async def _run() -> None:
    settings = get_settings()
    db_url = settings.database_url
    # Mask password
    if "@" in db_url:
        prefix, suffix = db_url.split("@", 1)
        scheme_user = prefix.rsplit(":", 1)[0]
        db_url = f"{scheme_user}:****@{suffix}"

    print(f"\n{'='*60}")
    print(f"  DB Verification Script")
    print(f"{'='*60}")
    print(f"\n🔌 DATABASE_URL: {db_url}\n")

    # ── 1. Check table existence ──────────────────────────────
    async with session_factory() as session:
        result = await session.execute(
            text(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname = 'public' "
                "ORDER BY tablename"
            )
        )
        tables = [row[0] for row in result.fetchall()]
        print(f"📋 Tables found: {tables}")

        if "jobs" not in tables:
            print("\n❌ 'jobs' table does NOT exist! Creating tables …")
            from job_platform.db.base import Base
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables created.\n")

    # ── 2. Count existing jobs ────────────────────────────────
    async with session_factory() as session:
        row = await session.execute(text("SELECT COUNT(*) FROM jobs"))
        count = row.scalar()
        print(f"📊 Current job count: {count}")

        row2 = await session.execute(text("SELECT COUNT(*) FROM companies"))
        co_count = row2.scalar()
        print(f"📊 Current company count: {co_count}\n")

    # ── 3. Insert test job ────────────────────────────────────
    test_job_id = "test_" + uuid.uuid4().hex[:16]
    print(f"➕ Inserting test job (job_id={test_job_id}) …")

    async with session_factory() as session:
        # Create test company first
        company = Company(name="TestCo", domain=f"test:{test_job_id}")
        session.add(company)
        await session.flush()

        job = Job(
            job_id=test_job_id,
            company_id=company.id,
            title="Test Job — DB Pipeline Verification",
            location="Remote",
            description="This is a test job inserted by test_insert.py",
            apply_url=f"https://test.example.com/apply/{test_job_id}",
            posted_date=date.today(),
            skills=["python", "testing"],
            experience_level="Entry Level",
            is_remote=True,
            score=42.0,
        )
        session.add(job)
        await session.commit()
        print(f"✅ Test job inserted: {job.title} (id={job.id})")

    # ── 4. Verify ─────────────────────────────────────────────
    async with session_factory() as session:
        row = await session.execute(text("SELECT COUNT(*) FROM jobs"))
        new_count = row.scalar()
        print(f"📊 Job count after insert: {new_count}")

        if new_count > count:
            print("✅ INSERT VERIFIED — jobs table is writable.\n")
        else:
            print("❌ INSERT FAILED — count did not increase!\n")

    # ── 5. Cleanup ────────────────────────────────────────────
    async with session_factory() as session:
        await session.execute(text("DELETE FROM jobs WHERE job_id = :jid"), {"jid": test_job_id})
        await session.execute(text("DELETE FROM companies WHERE domain = :d"), {"d": f"test:{test_job_id}"})
        await session.commit()
        print(f"🧹 Cleaned up test job ({test_job_id})")

    row_final = None
    async with session_factory() as session:
        row_final = await session.execute(text("SELECT COUNT(*) FROM jobs"))
        final_count = row_final.scalar()
        print(f"📊 Final job count: {final_count}\n")

    await engine.dispose()
    print(f"{'='*60}")
    print("  Done!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(_run())
