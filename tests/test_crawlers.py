"""Unit tests for job crawlers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from job_platform.crawler.base import BaseCrawler, NormalizedJob
from job_platform.crawler.sources.greenhouse import GreenhouseCrawler
from job_platform.crawler.sources.lever import LeverCrawler
from job_platform.crawler.sources.wellfound import WellfoundCrawler
from job_platform.crawler.sources.workday import WorkdayCrawler
from job_platform.crawler.sources.remote_jobs import RemoteJobsCrawler


class TestNormalizedJob:
    """Test NormalizedJob class."""

    def test_normalized_job_creation(self):
        """Test creating a normalized job."""
        job = NormalizedJob(
            title="Senior Engineer",
            location="San Francisco, CA",
            apply_url="https://example.com/apply/123",
            description="Great role",
            posted_date=datetime.now(tz=UTC),
            company_name="TechCorp",
        )
        
        assert job.title == "Senior Engineer"
        assert job.location == "San Francisco, CA"
        assert job.company_name == "TechCorp"

    def test_normalized_job_to_dict(self):
        """Test converting normalized job to dictionary."""
        now = datetime.now(tz=UTC)
        job = NormalizedJob(
            title="Engineer",
            location="NYC",
            apply_url="https://example.com/123",
            description="Role desc",
            posted_date=now,
            company_name="Company",
        )
        
        job_dict = job.to_dict()
        
        assert job_dict["title"] == "Engineer"
        assert job_dict["location"] == "NYC"
        assert job_dict["posted_date"] == now


class TestGreenhouseCrawler:
    """Test Greenhouse crawler."""

    @pytest.mark.asyncio
    async def test_fetch_jobs_from_company(self):
        """Test fetching jobs from Greenhouse."""
        crawler = GreenhouseCrawler()
        
        mock_response = {
            "jobs": [
                {
                    "title": "Software Engineer",
                    "location": {"name": "San Francisco"},
                    "absolute_url": "https://example.com/jobs/123",
                    "content": "Job description here",
                    "updated_at": "2024-01-15T10:00:00Z",
                },
                {
                    "title": "Product Manager",
                    "location": {"name": "New York"},
                    "absolute_url": "https://example.com/jobs/124",
                    "content": "PM role",
                    "updated_at": "2024-01-16T10:00:00Z",
                },
            ]
        }
        
        # Mock HTTP client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response_obj = MagicMock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response_obj)
        
        jobs = await crawler.fetch_jobs_from_company("stripe", mock_client)
        
        assert len(jobs) == 2
        assert jobs[0].title == "Software Engineer"
        assert jobs[0].location == "San Francisco"
        assert jobs[0].company_name == "stripe"
        assert jobs[1].title == "Product Manager"

    @pytest.mark.asyncio
    async def test_fetch_jobs_empty_response(self):
        """Test handling empty job list."""
        crawler = GreenhouseCrawler()
        
        mock_response = {"jobs": []}
        
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response_obj = MagicMock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response_obj)
        
        jobs = await crawler.fetch_jobs_from_company("stripe", mock_client)
        
        assert len(jobs) == 0

    @pytest.mark.asyncio
    async def test_fetch_jobs_invalid_company(self):
        """Test error handling for invalid company."""
        crawler = GreenhouseCrawler()
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        
        with pytest.raises(ValueError):
            await crawler.fetch_jobs_from_company("", mock_client)


class TestLeverCrawler:
    """Test Lever crawler."""

    @pytest.mark.asyncio
    async def test_fetch_jobs_from_company(self):
        """Test fetching jobs from Lever."""
        crawler = LeverCrawler()
        
        now = datetime.now(tz=UTC).timestamp() * 1000  # milliseconds
        
        mock_response = {
            "postings": [
                {
                    "text": "Senior Software Engineer",
                    "description": "Join our team",
                    "hostedUrl": "https://example.com/jobs/1",
                    "categories": {"location": "Remote"},
                    "createdAt": now,
                },
                {
                    "text": "Product Designer",
                    "description": "Design role",
                    "hostedUrl": "https://example.com/jobs/2",
                    "categories": {"location": "NYC"},
                    "createdAt": now,
                },
            ]
        }
        
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response_obj = MagicMock()
        mock_response_obj.json.return_value = mock_response
        mock_response_obj.raise_for_status.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response_obj)
        
        jobs = await crawler.fetch_jobs_from_company("netflix", mock_client)
        
        assert len(jobs) == 2
        assert jobs[0].title == "Senior Software Engineer"
        assert jobs[0].location == "Remote"
        assert jobs[0].company_name == "netflix"


class TestRemoteJobsCrawler:
    """Test Remote Jobs crawler."""

    @pytest.mark.asyncio
    async def test_normalize_remoteok_job(self):
        """Test normalizing RemoteOK job."""
        crawler = RemoteJobsCrawler()
        
        raw_job = {
            "title": "Remote Python Developer",
            "company": "TechStartup",
            "location": "Remote",
            "description": "Build awesome things",
            "url": "https://example.com/jobs/123",
            "date": "2024-01-15T10:00:00Z",
        }
        
        job = crawler._normalize_remoteok_job(raw_job)
        
        assert job is not None
        assert job.title == "Remote Python Developer"
        assert job.location == "Remote"
        assert job.company_name == "TechStartup"

    @pytest.mark.asyncio
    async def test_normalize_remoteok_job_missing_url(self):
        """Test handling RemoteOK job without URL."""
        crawler = RemoteJobsCrawler()
        
        raw_job = {
            "title": "Developer",
            "company": "Company",
            "location": "Remote",
            "description": "Role",
            # No URL
        }
        
        job = crawler._normalize_remoteok_job(raw_job)
        
        assert job is None


class TestWellfoundCrawler:
    """Test Wellfound crawler."""

    @pytest.mark.asyncio
    async def test_normalize_wellfound_job(self):
        """Test normalizing Wellfound job."""
        crawler = WellfoundCrawler()
        
        raw_job = {
            "title": "Full Stack Engineer",
            "description": "Help us build the future",
            "url": "https://wellfound.com/jobs/123",
            "apply_url": "https://example.com/apply",
            "created_at": "2024-01-15T10:00:00Z",
            "locations": [{"display_name": "San Francisco"}],
            "startup": {"name": "TechStartup"},
        }
        
        job = crawler._normalize_job(raw_job)
        
        assert job is not None
        assert job.title == "Full Stack Engineer"
        assert job.location == "San Francisco"
        assert job.company_name == "TechStartup"


class TestBaseCrawler:
    """Test BaseCrawler abstract class."""

    def test_base_crawler_not_implemented(self):
        """Test that base crawler doesn't implement concrete methods."""
        # BaseCrawler is abstract and should not be instantiated directly
        with pytest.raises(TypeError):
            BaseCrawler("test")

    def test_concrete_crawler_validation(self):
        """Test job validation in concrete crawler."""
        crawler = GreenhouseCrawler()
        
        # Valid job
        job = NormalizedJob(
            title="Engineer",
            location="NYC",
            apply_url="https://example.com/123",
            description="Role",
            posted_date=datetime.now(tz=UTC),
            company_name="Company",
        )
        
        assert crawler._validate_normalized_job(job) is True
        
        # Invalid job (no title)
        invalid_job = NormalizedJob(
            title="",
            location="NYC",
            apply_url="https://example.com/123",
            description="Role",
            posted_date=datetime.now(tz=UTC),
            company_name="Company",
        )
        
        assert crawler._validate_normalized_job(invalid_job) is False


class TestCrawlerRegistry:
    """Test crawler registry."""

    def test_get_crawler(self):
        """Test retrieving crawler from registry."""
        from job_platform.crawler.sources.registry import get_crawler
        
        greenhouse = get_crawler("greenhouse")
        assert isinstance(greenhouse, GreenhouseCrawler)
        
        lever = get_crawler("lever")
        assert isinstance(lever, LeverCrawler)

    def test_unknown_crawler(self):
        """Test error when requesting unknown crawler."""
        from job_platform.crawler.sources.registry import get_crawler
        
        with pytest.raises(ValueError):
            get_crawler("unknown_type")


class TestSourceConfig:
    """Test source configuration."""

    def test_valid_company_source(self):
        """Test validating company-based source."""
        from job_platform.crawler.sources.config import SourceConfig
        
        source = SourceConfig(
            name="Test Greenhouse",
            source_type="greenhouse",
            company="stripe",
        )
        
        # Should not raise
        source.validate()

    def test_invalid_company_source(self):
        """Test validation error for missing company field."""
        from job_platform.crawler.sources.config import SourceConfig
        
        source = SourceConfig(
            name="Test Greenhouse",
            source_type="greenhouse",
            # Missing company field
        )
        
        with pytest.raises(ValueError):
            source.validate()

    def test_valid_url_source(self):
        """Test validating URL-based source."""
        from job_platform.crawler.sources.config import SourceConfig
        
        source = SourceConfig(
            name="Test Remote Jobs",
            source_type="remote_jobs",
            url="https://remoteok.com",
        )
        
        # Should not raise
        source.validate()

    def test_get_sources_by_type(self):
        """Test filtering sources by type."""
        from job_platform.crawler.sources.config import get_sources_by_type
        
        greenhouse_sources = get_sources_by_type("greenhouse")
        
        # Should return Greenhouse sources
        assert all(s.source_type == "greenhouse" for s in greenhouse_sources)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
