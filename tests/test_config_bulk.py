"""Unit tests for bulk ATS configuration system."""

from __future__ import annotations

import pytest

from job_platform.crawler.sources.config import (
    GREENHOUSE_COMPANIES,
    LEVER_COMPANIES,
    WORKDAY_COMPANIES,
    SourceConfig,
    get_sources,
    get_sources_by_type,
    get_source_stats,
)
from job_platform.crawler.sources.config_utils import (
    add_companies,
    export_configuration_as_dict,
    get_companies,
    remove_companies,
    validate_all_sources,
)


class TestBulkConfiguration:
    """Test bulk ATS company configuration."""

    def test_greenhouse_companies_loaded(self):
        """Test that Greenhouse companies are loaded."""
        assert len(GREENHOUSE_COMPANIES) > 0
        assert "stripe" in GREENHOUSE_COMPANIES
        assert "airbnb" in GREENHOUSE_COMPANIES

    def test_lever_companies_loaded(self):
        """Test that Lever companies are loaded."""
        assert len(LEVER_COMPANIES) > 0
        assert "netflix" in LEVER_COMPANIES
        assert "uber" in LEVER_COMPANIES

    def test_workday_companies_loaded(self):
        """Test that Workday companies are loaded."""
        assert len(WORKDAY_COMPANIES) > 0
        assert "microsoft" in WORKDAY_COMPANIES
        assert "meta" in WORKDAY_COMPANIES

    def test_no_duplicate_companies(self):
        """Test that there are no duplicate companies within each list."""
        # Greenhouse
        gh_lower = [c.lower() for c in GREENHOUSE_COMPANIES]
        assert len(gh_lower) == len(set(gh_lower))
        
        # Lever
        lv_lower = [c.lower() for c in LEVER_COMPANIES]
        assert len(lv_lower) == len(set(lv_lower))
        
        # Workday
        wd_lower = [c.lower() for c in WORKDAY_COMPANIES]
        assert len(wd_lower) == len(set(wd_lower))

    def test_valid_company_names(self):
        """Test that all company names are valid."""
        for company in GREENHOUSE_COMPANIES:
            assert isinstance(company, str)
            assert len(company) > 0
            assert company.islower()
        
        for company in LEVER_COMPANIES:
            assert isinstance(company, str)
            assert len(company) > 0
            assert company.islower()
        
        for company in WORKDAY_COMPANIES:
            assert isinstance(company, str)
            assert len(company) > 0
            assert company.islower()


class TestSourceGeneration:
    """Test automatic SOURCES list generation."""

    def test_sources_generated(self):
        """Test that SOURCES list is generated from company lists."""
        sources = get_sources()
        assert len(sources) > 0

    def test_greenhouse_sources_count(self):
        """Test that all Greenhouse companies have sources."""
        gh_sources = get_sources_by_type("greenhouse")
        assert len(gh_sources) == len(GREENHOUSE_COMPANIES)

    def test_lever_sources_count(self):
        """Test that all Lever companies have sources."""
        lv_sources = get_sources_by_type("lever")
        assert len(lv_sources) == len(LEVER_COMPANIES)

    def test_workday_sources_count(self):
        """Test that all Workday companies have sources."""
        wd_sources = get_sources_by_type("workday")
        assert len(wd_sources) == len(WORKDAY_COMPANIES)

    def test_source_config_valid(self):
        """Test that all generated sources are valid."""
        sources = get_sources()
        for source in sources:
            # Should not raise
            source.validate()

    def test_source_naming(self):
        """Test that sources have proper names."""
        sources = get_sources()
        for source in sources:
            assert source.name
            assert len(source.name) > 0
            assert source.source_type in source.name or "Remote" in source.name


class TestSourceStats:
    """Test source statistics."""

    def test_get_source_stats(self):
        """Test getting source statistics."""
        stats = get_source_stats()
        
        assert "total" in stats
        assert "greenhouse" in stats
        assert "lever" in stats
        assert stats["total"] > 0

    def test_stats_totals(self):
        """Test that stats add up correctly."""
        stats = get_source_stats()
        
        calculated_total = (
            stats.get("greenhouse", 0)
            + stats.get("lever", 0)
            + stats.get("workday", 0)
            + stats.get("remote_jobs", 0)
            + stats.get("wellfound", 0)
            + stats.get("job_board", 0)
        )
        
        assert stats["total"] == calculated_total


class TestConfigUtils:
    """Test configuration utility functions."""

    def test_get_companies_greenhouse(self):
        """Test getting Greenhouse companies."""
        companies = get_companies("greenhouse")
        assert len(companies) == len(GREENHOUSE_COMPANIES)
        assert "stripe" in companies

    def test_get_companies_lever(self):
        """Test getting Lever companies."""
        companies = get_companies("lever")
        assert len(companies) == len(LEVER_COMPANIES)
        assert "netflix" in companies

    def test_get_companies_invalid_type(self):
        """Test error handling for invalid ATS type."""
        with pytest.raises(ValueError):
            get_companies("invalid_type")  # type: ignore

    def test_add_companies(self):
        """Test adding companies to a list."""
        # Get original count
        original = get_companies("greenhouse")
        original_count = len(original)
        
        # Add a test company (won't persist after test)
        add_companies("greenhouse", ["testcompany"])
        
        # Check it was added
        updated = get_companies("greenhouse")
        assert len(updated) > original_count

    def test_add_companies_duplicate(self):
        """Test that adding duplicate companies is skipped."""
        # Add a company that already exists
        original_count = len(get_companies("greenhouse"))
        
        add_companies("greenhouse", ["stripe"])
        
        # Count should not change (duplicate skipped)
        updated_count = len(get_companies("greenhouse"))
        assert updated_count == original_count

    def test_remove_companies(self):
        """Test removing companies."""
        # First add a test company
        add_companies("greenhouse", ["testcompanyx"])
        before = len(get_companies("greenhouse"))
        
        # Remove it
        remove_companies("greenhouse", ["testcompanyx"])
        after = len(get_companies("greenhouse"))
        
        assert after < before

    def test_export_configuration(self):
        """Test exporting configuration as dictionary."""
        config = export_configuration_as_dict()
        
        assert "greenhouse" in config
        assert "lever" in config
        assert "workday" in config
        
        assert len(config["greenhouse"]) > 0
        assert len(config["lever"]) > 0

    def test_validate_all_sources(self):
        """Test validation of all sources."""
        is_valid, errors = validate_all_sources()
        
        # Should be valid if all is well
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
        
        # If there are errors, it should be invalid
        if len(errors) > 0:
            assert not is_valid
        else:
            assert is_valid


class TestSourceConfigObject:
    """Test SourceConfig dataclass."""

    def test_source_config_creation(self):
        """Test creating SourceConfig objects."""
        config = SourceConfig(
            name="Test Company",
            source_type="greenhouse",
            company="testco",
        )
        
        assert config.name == "Test Company"
        assert config.source_type == "greenhouse"
        assert config.company == "testco"

    def test_source_config_validation_greenhouse(self):
        """Test validation for Greenhouse sources."""
        # Valid
        config = SourceConfig(
            name="Test",
            source_type="greenhouse",
            company="testco",
        )
        config.validate()  # Should not raise
        
        # Invalid (no company)
        invalid = SourceConfig(
            name="Test",
            source_type="greenhouse",
        )
        with pytest.raises(ValueError):
            invalid.validate()

    def test_source_config_validation_remote_jobs(self):
        """Test validation for remote_jobs sources."""
        # Valid
        config = SourceConfig(
            name="Test",
            source_type="remote_jobs",
            url="https://example.com",
        )
        config.validate()  # Should not raise
        
        # Invalid (no URL)
        invalid = SourceConfig(
            name="Test",
            source_type="remote_jobs",
        )
        with pytest.raises(ValueError):
            invalid.validate()

    def test_source_config_unknown_type(self):
        """Test error for unknown source type."""
        config = SourceConfig(
            name="Test",
            source_type="unknown",  # type: ignore
        )
        with pytest.raises(ValueError):
            config.validate()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
