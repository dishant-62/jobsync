"""Add parsed job fields for enhanced job data.

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-23

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add parsed job fields
    op.add_column("jobs", sa.Column("skills", sa.JSON, nullable=True))
    op.add_column("jobs", sa.Column("experience_level", sa.String(50), nullable=True))
    op.add_column("jobs", sa.Column("salary_min", sa.Integer, nullable=True))
    op.add_column("jobs", sa.Column("salary_max", sa.Integer, nullable=True))
    op.add_column("jobs", sa.Column("is_remote", sa.Boolean, server_default="false", nullable=False))

    # Add indexes for commonly queried fields
    op.create_index("ix_jobs_experience_level", "jobs", ["experience_level"])
    op.create_index("ix_jobs_is_remote", "jobs", ["is_remote"])
    op.create_index("ix_jobs_salary_min", "jobs", ["salary_min"])
    op.create_index("ix_jobs_salary_max", "jobs", ["salary_max"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_jobs_salary_max", table_name="jobs")
    op.drop_index("ix_jobs_salary_min", table_name="jobs")
    op.drop_index("ix_jobs_is_remote", table_name="jobs")
    op.drop_index("ix_jobs_experience_level", table_name="jobs")

    # Drop columns
    op.drop_column("jobs", "is_remote")
    op.drop_column("jobs", "salary_max")
    op.drop_column("jobs", "salary_min")
    op.drop_column("jobs", "experience_level")
    op.drop_column("jobs", "skills")