"""Company persistence operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from job_platform.db.models import Company


def greenhouse_board_domain(board_token: str) -> str:
    """Stable synthetic domain key for a Greenhouse board token."""
    return f"greenhouse-board:{board_token.strip().lower()}"


class CompanyRepository:
    """Async repository for ``Company`` entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create_for_greenhouse_board(self, board_token: str) -> Company:
        """Return the company row for this board, creating it if needed."""
        token = board_token.strip()
        if not token:
            raise ValueError("board token must be non-empty")

        domain = greenhouse_board_domain(token)
        result = await self._session.execute(select(Company).where(Company.domain == domain))
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing

        company = Company(name=token, domain=domain)
        self._session.add(company)
        await self._session.flush()
        await self._session.refresh(company)
        return company
