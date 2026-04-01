"""Backfill script to generate job_id for existing jobs."""

import asyncio
import logging
from collections import defaultdict

from sqlalchemy import select, update

from job_platform.config import get_settings
from job_platform.db.models import Job
from job_platform.db.session import session_factory
from job_platform.repositories.company import CompanyRepository
from job_platform.utils.job_id import generate_job_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def backfill_job_ids():
    """Generate and populate job_id for all existing jobs."""
    settings = get_settings()

    async with session_factory() as session:
        company_repo = CompanyRepository(session)

        # Get all jobs that don't have job_id set
        stmt = select(Job).where(Job.job_id.is_(None))
        result = await session.execute(stmt)
        jobs = result.scalars().all()

        if not jobs:
            logger.info("No jobs found that need job_id backfilling")
            return

        logger.info(f"Found {len(jobs)} jobs to backfill")

        # Group jobs by company for efficient company lookup
        jobs_by_company = defaultdict(list)
        for job in jobs:
            jobs_by_company[job.company_id].append(job)

        updated_count = 0

        for company_id, company_jobs in jobs_by_company.items():
            # Get company info
            company = await session.get(Job.company, company_id)
            if not company:
                logger.warning(f"Company {company_id} not found for jobs, skipping")
                continue

            # Generate job_id for each job in this company
            for job in company_jobs:
                job_id = generate_job_id(company.name, job.apply_url)

                # Update the job with the new job_id
                await session.execute(
                    update(Job)
                    .where(Job.id == job.id)
                    .values(job_id=job_id)
                )

                logger.info(f"Generated job_id {job_id} for job {job.id} ({job.title})")
                updated_count += 1

        await session.commit()
        logger.info(f"Successfully backfilled job_id for {updated_count} jobs")


if __name__ == "__main__":
    asyncio.run(backfill_job_ids())