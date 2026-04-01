"""Backfill script to calculate and populate job scores for existing jobs."""

import asyncio
import logging
from datetime import date

from sqlalchemy import select, update

from job_platform.config import get_settings
from job_platform.db.models import Job
from job_platform.db.session import session_factory
from job_platform.utils.ranking import calculate_job_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def backfill_job_scores():
    """Calculate and populate scores for all existing jobs."""
    settings = get_settings()

    async with session_factory() as session:
        # Get all jobs that need score calculation (score is 0.0 or null)
        stmt = select(Job).where(Job.score.is_(None) | (Job.score == 0.0))
        result = await session.execute(stmt)
        jobs = result.scalars().all()

        if not jobs:
            logger.info("No jobs found that need score calculation")
            return

        logger.info(f"Found {len(jobs)} jobs to calculate scores for")

        updated_count = 0

        for job in jobs:
            # Calculate score for this job
            score = calculate_job_score(
                posted_date=job.posted_date,
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                is_remote=job.is_remote,
                description=job.description,
                skills=job.skills,
            )

            # Update the job with the calculated score
            await session.execute(
                update(Job)
                .where(Job.id == job.id)
                .values(score=score)
            )

            logger.info(f"Calculated score {score:.2f} for job {job.id} ({job.title})")
            updated_count += 1

        await session.commit()
        logger.info(f"Successfully calculated scores for {updated_count} jobs")


if __name__ == "__main__":
    asyncio.run(backfill_job_scores())