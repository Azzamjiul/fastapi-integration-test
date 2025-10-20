"""
Unit tests conftest.py - Fixtures for unit tests.

Unit tests don't need database or containers, so fixtures here are simpler.
They focus on mocks, stubs, and isolated component testing.
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_db_session():
    """
    Mock database session for unit testing.

    Use this instead of real database for unit tests.
    """
    session = MagicMock()
    return session


@pytest.fixture
def sample_todo_dict():
    """
    Sample todo data as dictionary for unit testing.
    """
    return {
        "id": 1,
        "title": "Unit Test Todo",
        "description": "For unit testing",
        "completed": False,
    }


# Auto-apply unit marker to all tests in this directory
def pytest_collection_modifyitems(items):
    """Automatically mark all tests in unit/ as unit tests."""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.fast)
