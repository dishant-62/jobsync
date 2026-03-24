"""add_job_id_field

Revision ID: 6a2363dc0794
Revises: 0003
Create Date: 2026-03-24 12:15:57.940244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a2363dc0794'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add job_id column as unique VARCHAR(64) for SHA256 hash
    op.add_column("jobs", sa.Column("job_id", sa.String(64), unique=True, nullable=False))

    # Create index for job_id lookups
    op.create_index("ix_jobs_job_id", "jobs", ["job_id"])


def downgrade() -> None:
    # Drop index
    op.drop_index("ix_jobs_job_id", table_name="jobs")

    # Drop column
    op.drop_column("jobs", "job_id")
