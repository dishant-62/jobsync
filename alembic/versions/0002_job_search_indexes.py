"""pg_trgm GIN indexes for job search (ILIKE).

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-22

"""

from collections.abc import Sequence

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    op.create_index(
        "ix_jobs_title_trgm",
        "jobs",
        ["title"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"title": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_jobs_description_trgm",
        "jobs",
        ["description"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"description": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_jobs_location_trgm",
        "jobs",
        ["location"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"location": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_jobs_location_trgm", table_name="jobs")
    op.drop_index("ix_jobs_description_trgm", table_name="jobs")
    op.drop_index("ix_jobs_title_trgm", table_name="jobs")
