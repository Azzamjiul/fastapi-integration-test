"""
Database fixtures for integration tests.
Provides centralized database session and setup that can be customized per feature.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.core import utils
from testcontainers.postgres import PostgresContainer

from app.database import Base


def initialize_test_db(engine):
    """
    Initialize test database with seed data if needed.
    This is a CENTRALIZED function that can be OVERRIDDEN per feature.

    Override example in feature conftest.py:
        def initialize_test_db(engine):
            # Custom seed data for this feature
            Base.metadata.create_all(engine)
            with Session(engine) as session:
                # Add feature-specific seed data
                session.add(SomeModel(...))
                session.commit()
    """
    # Default: just create tables, no seed data
    pass


@pytest.fixture(scope="session")
def db_engine(postgres_container: PostgresContainer):
    """
    Create database engine from postgres container.

    This fixture can be OVERRIDDEN to customize engine configuration per feature.

    Example override:
        @pytest.fixture(scope="session")
        def db_engine(postgres_container):
            url = postgres_container.get_connection_url()
            engine = create_engine(
                url,
                echo=True,  # Enable SQL logging for this feature
                pool_size=20  # Custom pool size
            )
            Base.metadata.create_all(engine)
            return engine
    """
    if utils.is_windows():
        postgres_container.get_container_host_ip = lambda: "localhost"

    url = postgres_container.get_connection_url()
    engine = create_engine(url, echo=False)
    Base.metadata.create_all(engine)
    initialize_test_db(engine)
    return engine


@pytest.fixture(scope="session")
def db(db_engine):
    """
    Provide database session for tests.

    This fixture can be OVERRIDDEN to change session behavior per feature.

    Example override (function scope instead of session):
        @pytest.fixture(scope="function")
        def db(db_engine):
            # Create fresh session for each test
            with Session(db_engine) as session:
                yield session
                session.rollback()  # Rollback after each test
    """
    with Session(db_engine) as session:
        yield session
