"""
Todos feature-specific conftest.py - Override and customize fixtures for todos tests.

This file demonstrates how to OVERRIDE centralized fixtures for feature-specific needs.

FIXTURE OVERRIDE PATTERN:
========================

When you define a fixture with the SAME NAME as a centralized fixture,
pytest will use YOUR version instead of the centralized one for tests in this directory.

Example:
  - tests/integration/conftest.py defines: @pytest.fixture def db()
  - tests/integration/todos/conftest.py defines: @pytest.fixture def db()
  - Tests in todos/ will use the LOCAL db() fixture, not the centralized one
  - Tests in other features will still use the centralized db() fixture

This allows you to:
  1. Customize behavior per feature
  2. Add feature-specific seed data
  3. Change fixture scope
  4. Add custom configuration
  5. Keep centralized fixtures as defaults
"""
import pytest
from sqlalchemy.orm import Session

# Import what you need from centralized fixtures
from tests.integration.fixtures.factories import create_todo_data, create_multiple_todos


# ============================================================================
# EXAMPLE 1: Override factory fixture to add feature-specific defaults
# ============================================================================

@pytest.fixture
def todo_data():
    """
    Feature-specific factory for creating todo data.

    This OVERRIDES the generic create_todo_data factory with custom defaults
    specific to todos feature tests.

    Usage in tests:
        def test_something(todo_data):
            # Get default todo data
            data = todo_data()

            # Override specific fields
            data = todo_data(title="Custom", completed=True)
    """
    def _factory(**kwargs):
        # Set feature-specific defaults
        defaults = {
            "title": "Todos Feature Test",
            "description": "Created in todos feature tests",
            "completed": False,
        }
        defaults.update(kwargs)
        return create_todo_data(**defaults)
    return _factory


# ============================================================================
# EXAMPLE 2: Add feature-specific fixtures (not overriding, just adding new)
# ============================================================================

@pytest.fixture
def sample_todo(test_client, todo_data):
    """
    Creates a sample todo in the database for testing.

    This is a NEW fixture, not an override. It's only available in todos/ tests.

    Usage:
        def test_update(sample_todo):
            todo_id = sample_todo["id"]
            # Use the pre-created todo
    """
    data = todo_data()
    response = test_client.post("/api/todos/", json=data)
    return response.json()


@pytest.fixture
def multiple_todos(test_client, todo_data):
    """
    Creates multiple todos for list/pagination testing.

    Another NEW fixture for this feature.
    """
    todos = []
    for i in range(5):
        data = todo_data(title=f"Todo {i+1}")
        response = test_client.post("/api/todos/", json=data)
        todos.append(response.json())
    return todos


# ============================================================================
# EXAMPLE 3: Override db fixture to change scope (commented out by default)
# ============================================================================

# Uncomment this to override the db fixture for todos tests only
# This changes scope from 'session' to 'function' for better test isolation

# @pytest.fixture(scope="function")
# def db(db_engine):
#     """
#     OVERRIDE: Function-scoped database session for todos tests.
#
#     Centralized db fixture uses scope="session" for performance.
#     But todos tests might need fresh DB state for each test.
#
#     This override provides a NEW session for EACH test and rolls back
#     changes after each test.
#     """
#     with Session(db_engine) as session:
#         yield session
#         session.rollback()  # Rollback after each test


# ============================================================================
# EXAMPLE 4: Override test_client to add custom behavior (commented out)
# ============================================================================

# @pytest.fixture(scope="function")
# def test_client(db):
#     """
#     OVERRIDE: Custom test client for todos feature.
#
#     Example: Add custom headers, middleware, or event handlers
#     specific to todos testing.
#     """
#     from app.main import app
#     from app.database import get_db
#     from fastapi.testclient import TestClient
#
#     app.dependency_overrides[get_db] = lambda: db
#
#     # Add custom headers for all requests in todos tests
#     with TestClient(app, headers={"X-Test-Feature": "todos"}) as c:
#         yield c
#
#     app.dependency_overrides.clear()


# ============================================================================
# EXAMPLE 5: Override initialize_test_db to add seed data (commented out)
# ============================================================================

# You can also create a fixture that runs before tests to seed data

# @pytest.fixture(scope="session", autouse=True)
# def seed_todos_data(db_engine):
#     """
#     Automatically seed specific data for todos tests.
#
#     autouse=True means this runs automatically without being requested.
#     scope="session" means it runs once for all todos tests.
#     """
#     from app.models.todo import Todo
#
#     with Session(db_engine) as session:
#         # Add seed data
#         session.add(Todo(title="Seed Todo 1", description="Pre-seeded", completed=False))
#         session.add(Todo(title="Seed Todo 2", description="Pre-seeded", completed=True))
#         session.commit()
#
#     yield
#
#     # Cleanup after all tests
#     with Session(db_engine) as session:
#         session.query(Todo).delete()
#         session.commit()
