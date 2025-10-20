"""
Docker container fixtures for integration tests.
Provides centralized container configurations that can be overridden per feature.
"""

import pytest
from testcontainers.postgres import PostgresContainer

# Default container configurations
# These can be overridden in feature-specific conftest.py
DEFAULT_POSTGRES_IMAGE = "postgres:14"
DEFAULT_POSTGRES_USER = "postgres"
DEFAULT_POSTGRES_PASSWORD = "test_password"
DEFAULT_POSTGRES_DATABASE = "test_database"
DEFAULT_POSTGRES_PORT = 5432


@pytest.fixture(scope="session")
def postgres_container() -> PostgresContainer:
    """
    Setup postgres container with default configuration.

    This is a CENTRALIZED fixture that can be OVERRIDDEN in feature-specific conftest.py.

    Example override in tests/integration/todos/conftest.py:
        @pytest.fixture(scope="session")
        def postgres_container():
            # Custom configuration for todos feature
            return PostgresContainer(
                image="postgres:15",  # Different version
                username="custom_user",
                password="custom_pass",
                dbname="todos_db",
            )
    """
    postgres = PostgresContainer(
        image=DEFAULT_POSTGRES_IMAGE,
        username=DEFAULT_POSTGRES_USER,
        password=DEFAULT_POSTGRES_PASSWORD,
        dbname=DEFAULT_POSTGRES_DATABASE,
        port=DEFAULT_POSTGRES_PORT,
    )
    with postgres:
        yield postgres
