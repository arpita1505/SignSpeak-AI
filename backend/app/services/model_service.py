"""Model loading and inference service."""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
from joblib import load

from app.config import settings

logger = logging.getLogger(__name__)


class ModelService:
    """Service for loading and running ML model inference."""

    def __init__(self):
        """Initialize model service."""
        self.model = None
        self.metadata = None
        self.labels = None
        self.load_model()

    def load_model(self) -> bool:
        """
        Load the ML model from disk.

        Returns:
            True if successful, False otherwise
        """
        try:
            model_path = Path(settings.model_path)
            metadata_path = Path(settings.model_metadata_path)

            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}")
                return False

            # Load model
            self.model = load(model_path)
            logger.info(f"Model loaded from {model_path}")

            # Load metadata
            if metadata_path.exists():
                with open(metadata_path, "r") as f:
                    self.metadata = json.load(f)
                self.labels = self.metadata.get("supported_labels", [])
                logger.info(f"Model metadata loaded: version {self.metadata.get('version')}")
            else:
                logger.warning(f"Metadata file not found: {metadata_path}")
                self.labels = []

            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def predict(self, features: np.ndarray) -> tuple[str | None, float]:
        """
        Make a prediction.

        Args:
            features: Feature vector from normalized landmarks

        Returns:
            Tuple of (predicted_label, confidence)
        """
        if self.model is None:
            logger.warning("Model not loaded")
            return None, 0.0

        try:
            # Validate feature dimension
            if len(features) != 126:
                logger.warning(f"Invalid feature dimension: {len(features)}, expected 126")
                return None, 0.0

            # Reshape for sklearn model
            features_reshaped = features.reshape(1, -1)

            # Predict
            prediction = self.model.predict(features_reshaped)[0]
            confidence = float(np.max(self.model.predict_proba(features_reshaped)))

            return str(prediction), confidence

        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return None, 0.0

    def is_model_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None

    def get_model_version(self) -> str | None:
        """Get model version."""
        if self.metadata:
            return self.metadata.get("version")
        return None

    def get_supported_labels(self) -> list[str]:
        """Get list of supported labels."""
        return self.labels if self.labels else []
