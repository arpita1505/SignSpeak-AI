"""Pydantic schemas for API requests/responses."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    model_version: Optional[str]
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

    type: str  # "prediction", "no_hand", "low_confidence", "error"
    sign: Optional[str] = None
    confidence: Optional[float] = None
    stable: Optional[bool] = None
    commit: Optional[bool] = None
    hands_detected: Optional[int] = None
    timestamp: Optional[str] = None
    message: Optional[str] = None


class TranslationCreate(BaseModel):
    """Create translation history entry."""

    text: str
    model_version: Optional[str] = None


class TranslationResponse(BaseModel):
    """Translation history response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    created_at: datetime
    model_version: Optional[str]


class LabelsResponse(BaseModel):
    """Labels response."""

    labels: list[str]
    count: int
