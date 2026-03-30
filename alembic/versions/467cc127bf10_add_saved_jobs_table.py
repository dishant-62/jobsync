"""add_saved_jobs_table

Revision ID: 467cc127bf10
Revises: 6a2363dc0794
Create Date: 2026-03-24 14:04:46.868355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '467cc127bf10'
down_revision: Union[str, Sequence[str], None] = '6a2363dc0794'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create saved_jobs table
    op.create_table(
        "saved_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=False, default="guest"),
        sa.Column("job_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.job_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("ix_saved_jobs_user_id", "saved_jobs", ["user_id"])
    op.create_index("ix_saved_jobs_job_id", "saved_jobs", ["job_id"])
    op.create_index("ix_saved_jobs_user_job", "saved_jobs", ["user_id", "job_id"], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_saved_jobs_user_job", table_name="saved_jobs")
    op.drop_index("ix_saved_jobs_job_id", table_name="saved_jobs")
    op.drop_index("ix_saved_jobs_user_id", table_name="saved_jobs")

    # Drop table
    op.drop_table("saved_jobs")
