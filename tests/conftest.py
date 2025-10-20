"""
Root conftest.py - Base configurations for all tests.

This file contains:
- Test markers registration
- Environment setup
- Shared utilities for all test types (unit and integration)
"""
import os
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set testing mode before importing app
os.environ["TESTING"] = "1"


def pytest_configure(config):
    """
    Register custom markers for pytest.

    Markers help organize and filter tests:
    - pytest -m integration  # Run only integration tests
    - pytest -m unit         # Run only unit tests
    - pytest -m slow         # Run only slow tests
    """
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "fast: mark test as fast running"
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Setup test environment for all tests.
    Runs automatically before any test starts.
    """
    # Any global test setup can go here
    print("\n🚀 Setting up test environment...")
    yield
    print("\n✅ Test environment cleanup complete")
