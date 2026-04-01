"""
Integration test conftest.py

Tests in this directory require a live PostgreSQL database.
They are intentionally excluded from the default `pytest` run.

To run integration tests:
    pytest tests/integration/ --integration

To run a specific integration test directly as a script:
    python tests/integration/test_api_e2e.py
    python tests/integration/test_job_ranking.py
    python tests/integration/test_saved_jobs.py
    python tests/integration/test_parser.py
    python tests/integration/integration_test.py
"""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run integration tests that require a live database",
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--integration"):
        skip_integration = pytest.mark.skip(
            reason="Requires --integration flag and a live database"
        )
        for item in items:
            if "integration" in str(item.fspath):
                item.add_marker(skip_integration)
