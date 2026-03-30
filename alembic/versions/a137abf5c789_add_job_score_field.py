"""add_job_score_field

Revision ID: a137abf5c789
Revises: 467cc127bf10
Create Date: 2026-03-24 14:13:22.047562

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a137abf5c789'
down_revision: Union[str, Sequence[str], None] = '467cc127bf10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add score column for job ranking
    op.add_column("jobs", sa.Column("score", sa.Float(), nullable=False, default=0.0, server_default="0.0"))

    # Create index for score-based sorting
    op.create_index("ix_jobs_score", "jobs", ["score"])


def downgrade() -> None:
    # Drop index
    op.drop_index("ix_jobs_score", table_name="jobs")

    # Drop column
    op.drop_column("jobs", "score")
