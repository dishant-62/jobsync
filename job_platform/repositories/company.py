"""Company persistence operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from job_platform.db.models import Company


def greenhouse_board_domain(board_token: str) -> str:
    """Stable synthetic domain key for a Greenhouse board token."""
    return f"greenhouse-board:{board_token.strip().lower()}"


def _source_domain(source_type: str, identifier: str) -> str:
    """
    Generate stable domain key for any source type.
    
    Args:
        source_type: Crawler type (greenhouse, lever, etc.)
        identifier: Source-specific identifier (company, URL, etc.)
        
    Returns:
        Stable domain key
    """
    clean_id = identifier.strip().lower()
    return f"{source_type}:{clean_id}"


class CompanyRepository:
    """Async repository for ``Company`` entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create_for_source(
        self, source_type: str, identifier: str, display_name: str | None = None
    ) -> Company:
        """
        Get or create a company record for any source type.
        
        Args:
            source_type: Crawler type (greenhouse, lever, workday, etc.)
            identifier: Source-specific identifier (board token, company slug, URL, etc.)
            display_name: Optional display name for the company
            
        Returns:
            Company record (existing or newly created)
            
        Raises:
            ValueError: If identifier is empty
        """
        clean_id = identifier.strip()
        if not clean_id:
            raise ValueError("identifier must be non-empty")

        domain = _source_domain(source_type, clean_id)
        
        # Try to find existing company
        result = await self._session.execute(select(Company).where(Company.domain == domain))
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing

        # Create new company record
        name = display_name or clean_id
        company = Company(name=name, domain=domain)
        self._session.add(company)
        await self._session.flush()
        await self._session.refresh(company)
        return company

    async def get_or_create_for_greenhouse_board(self, board_token: str) -> Company:
        """
        Get or create a company record for a Greenhouse board.
        
        DEPRECATED: Use get_or_create_for_source instead.
        
        Args:
            board_token: Greenhouse board token
            
        Returns:
            Company record
        """
        return await self.get_or_create_for_source(
            source_type="greenhouse",
            identifier=board_token,
        )

    async def get_company_by_identifier(
        self, source_type: str, identifier: str
    ) -> Company | None:
        """
        Find a company by source type and identifier.
        
        Args:
            source_type: Crawler type
            identifier: Source identifier
            
        Returns:
            Company record or None if not found
        """
        domain = _source_domain(source_type, identifier)
        result = await self._session.execute(select(Company).where(Company.domain == domain))
        return result.scalar_one_or_none()
