"""
Pytest configuration map and test database dependency injections.
Ensures testing environment uses localized SQLite memory isolation.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from src.backend.main import app, get_db

# Use an in-memory SQLite database for testing, isolated from the enterprise.db
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

def get_test_db():
    with Session(engine) as session:
        yield session

# Override the FastAPI dependency explicitly
app.dependency_overrides[get_db] = get_test_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
