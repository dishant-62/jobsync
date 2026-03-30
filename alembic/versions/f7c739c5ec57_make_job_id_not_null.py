"""make_job_id_not_null

Revision ID: f7c739c5ec57
Revises: a137abf5c789
Create Date: 2026-03-27 04:08:36.734563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7c739c5ec57'
down_revision: Union[str, Sequence[str], None] = 'a137abf5c789'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make job_id column NOT NULL
    op.alter_column("jobs", "job_id", nullable=False)


def downgrade() -> None:
    # Make job_id column nullable again
    op.alter_column("jobs", "job_id", nullable=True)
