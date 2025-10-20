# conftest.py
import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from testcontainers.core import utils
from testcontainers.postgres import PostgresContainer

# Load environment variables
load_dotenv()

# Set testing mode before importing app
os.environ["TESTING"] = "1"

from app.main import app
from app.database import get_db, Base

POSTGRES_IMAGE = "postgres:14"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "test_password"
POSTGRES_DATABASE = "test_database"
POSTGRES_CONTAINER_PORT = 5432


def initialize_test_db(engine):
    """
    Initialize test database with seed data if needed.
    Add any test data setup here.
    """
    # Currently just creates tables, can be extended with seed data
    pass


@pytest.fixture(scope="session")
def postgres_container() -> PostgresContainer:
    """
    Setup postgres container
    PostgresContainer has built-in wait strategy, no need to specify custom one
    """
    postgres = PostgresContainer(
        image=POSTGRES_IMAGE,
        username=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DATABASE,
        port=POSTGRES_CONTAINER_PORT,
    )
    with postgres:
        yield postgres


@pytest.fixture(scope="session")
def db(postgres_container: PostgresContainer):
    if utils.is_windows():
        postgres_container.get_container_host_ip = lambda: "localhost"
    url = postgres_container.get_connection_url()
    engine = create_engine(url, echo=False)
    Base.metadata.create_all(engine)
    initialize_test_db(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session")
def test_client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
