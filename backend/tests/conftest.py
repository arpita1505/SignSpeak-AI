"""Pytest configuration."""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set test environment BEFORE imports
os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Now import app after env is set
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import create_app

# Create test database
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override get_db for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Create test client with overridden database."""
    app = create_app(test_mode=True)
    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def smoothing_service():
    """Create smoothing service for testing."""
    from app.services.smoothing_service import TemporalSmoothingService

    return TemporalSmoothingService(
        stability_window=5,
        stability_min_count=4,
        cooldown_ms=800,
    )
