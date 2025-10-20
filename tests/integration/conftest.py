"""
Integration tests conftest.py - Centralized fixtures for all integration tests.

This file imports and exposes fixtures from the fixtures/ directory.
These fixtures are available to ALL integration tests and can be overridden
in feature-specific conftest.py files.

Fixture Hierarchy:
1. tests/conftest.py (root) - Base configuration, markers
2. tests/integration/conftest.py (this file) - Integration-wide fixtures
3. tests/integration/<feature>/conftest.py - Feature-specific overrides
"""
import pytest
from fastapi.testclient import TestClient

# Import centralized fixtures
# These will be available to all integration tests
from tests.integration.fixtures.containers import (
    postgres_container,
    DEFAULT_POSTGRES_IMAGE,
    DEFAULT_POSTGRES_USER,
    DEFAULT_POSTGRES_PASSWORD,
    DEFAULT_POSTGRES_DATABASE,
)
from tests.integration.fixtures.database import (
    db_engine,
    db,
    initialize_test_db,
)

# Import app components
from app.main import app
from app.database import get_db


@pytest.fixture(scope="session")
def test_client(db):
    """
    Provide FastAPI test client with database dependency override.

    This is a CENTRALIZED fixture that can be OVERRIDDEN per feature.

    Example override in feature conftest.py:
        @pytest.fixture(scope="function")  # Different scope
        def test_client(db):
            # Custom middleware or dependencies
            app.dependency_overrides[get_db] = lambda: db
            app.middleware("http")(custom_middleware)
            with TestClient(app) as c:
                yield c
            app.dependency_overrides.clear()
    """
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# Auto-apply integration marker to all tests in this directory
def pytest_collection_modifyitems(items):
    """Automatically mark all tests in integration/ as integration tests."""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
