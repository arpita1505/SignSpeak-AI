"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Create test database engine BEFORE importing app modules
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch app.db.database BEFORE importing app modules
import app.db.database as db_module

original_sessionlocal = db_module.SessionLocal
db_module.SessionLocal = TestingSessionLocal

# Now import app after patching
from app.db.database import Base, get_db
from app.main import create_app

# Create all tables with test engine
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    """Override get_db for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Create test client with test database."""
    # Create app in test mode
    app = create_app(test_mode=True)
    # Override database dependency
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    # Cleanup
    app.dependency_overrides.clear()
    # Restore original SessionLocal
    db_module.SessionLocal = original_sessionlocal


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert data["status"] == "ok"


def test_labels_endpoint(client):
    """Test labels endpoint."""
    response = client.get("/api/labels")
    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "count" in data
    assert isinstance(data["labels"], list)


def test_model_info_endpoint(client):
    """Test model info endpoint."""
    response = client.get("/api/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "algorithm" in data
    assert "supported_labels" in data


def test_history_get_empty(client):
    """Test getting empty history."""
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_history_create(client):
    """Test creating history entry."""
    response = client.post("/api/history", json={"text": "Hello world"})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Hello world"
    assert "id" in data
    assert "created_at" in data


def test_history_delete_all(client):
    """Test deleting all history."""
    # Create some entries
    client.post("/api/history", json={"text": "Test 1"})
    client.post("/api/history", json={"text": "Test 2"})

    # Delete all
    response = client.delete("/api/history")
    assert response.status_code == 200

    # Verify empty
    response = client.get("/api/history")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_websocket_rejects_malformed_json(client):
    """Malformed messages return a safe protocol error without a traceback."""
    with client.websocket_connect("/ws/predict") as socket:
        socket.send_text("not-json")
        assert socket.receive_json() == {
            "type": "error",
            "sign": None,
            "confidence": None,
            "stable": None,
            "commit": None,
            "hands_detected": None,
            "timestamp": None,
            "message": "Invalid JSON format",
        }


def test_websocket_reports_model_unavailable(client):
    """A missing production artifact is explicit and does not initialize MediaPipe."""
    from app.api.health import model_service

    original = model_service.model
    model_service.model = None
    try:
        with client.websocket_connect("/ws/predict") as socket:
            socket.send_json({"frame": "ZmFrZQ=="})
            message = socket.receive_json()
            assert message["type"] == "model_unavailable"
            assert message["message"] == "Model not loaded"
    finally:
        model_service.model = original
