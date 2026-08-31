"""Health check endpoints."""
import logging

from fastapi import APIRouter

from app.schemas.prediction import HealthResponse, ModelInfoResponse
from app.services.model_service import ModelService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["health"])

# Global model service instance
model_service = ModelService()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        model_loaded=model_service.is_model_loaded(),
        model_version=model_service.get_model_version(),
        database="ok",
    )


@router.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info() -> ModelInfoResponse:
    """Get model information."""
    if not model_service.is_model_loaded():
        return ModelInfoResponse(
            version="unknown",
            algorithm="unknown",
            feature_dimension=0,
            supported_labels=[],
            metrics={},
        )

    metadata = model_service.metadata or {}
    return ModelInfoResponse(
        version=metadata.get("version", "unknown"),
        algorithm=metadata.get("algorithm", "unknown"),
        feature_dimension=metadata.get("feature_dimension", 126),
        supported_labels=model_service.get_supported_labels(),
        metrics=metadata.get("metrics", {}),
    )


@router.get("/labels")
async def get_labels():
    """Get supported labels."""
    return {
        "labels": model_service.get_supported_labels(),
        "count": len(model_service.get_supported_labels()),
    }
