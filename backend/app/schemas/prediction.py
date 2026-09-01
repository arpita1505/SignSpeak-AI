"""Pydantic schemas for API requests/responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    model_version: str | None
    database: str


class ModelInfoResponse(BaseModel):
    """Model information response."""

    version: str
    algorithm: str
    feature_dimension: int
    supported_labels: list[str]
    metrics: dict


class PredictionFrame(BaseModel):
    """Single prediction frame from WebSocket."""

    frame: str  # base64 encoded JPEG frame
    timestamp: float


class PredictionResponse(BaseModel):
    """Prediction response from WebSocket."""

    type: str  # prediction, no_hand, low_confidence, model_unavailable, error
    sign: str | None = None
    confidence: float | None = None
    stable: bool | None = None
    commit: bool | None = None
    hands_detected: int | None = None
    timestamp: str | None = None
    message: str | None = None


class TranslationCreate(BaseModel):
    """Create translation history entry."""

    text: str
    model_version: str | None = None


class TranslationResponse(BaseModel):
    """Translation history response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    created_at: datetime
    model_version: str | None


class LabelsResponse(BaseModel):
    """Labels response."""

    labels: list[str]
    count: int
