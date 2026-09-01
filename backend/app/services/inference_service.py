"""Inference pipeline orchestration."""

from __future__ import annotations

import base64
import logging

import cv2
import numpy as np

from app.services.mediapipe_service import MediaPipeService
from app.services.model_service import ModelService
from app.services.smoothing_service import TemporalSmoothingService

logger = logging.getLogger(__name__)


class InferenceService:
    """Orchestrates the full inference pipeline."""

    def __init__(self, model_service: ModelService | None = None):
        """Initialize inference service with all components."""
        self.mp_service = MediaPipeService()
        self.model_service = model_service or ModelService()
        self.smoothing = TemporalSmoothingService()

    def decode_frame(self, frame_base64: str) -> np.ndarray | None:
        """
        Decode base64 JPEG frame.

        Args:
            frame_base64: Base64 encoded JPEG frame

        Returns:
            Decoded frame as numpy array or None
        """
        try:
            frame_bytes = base64.b64decode(frame_base64)
            frame = cv2.imdecode(np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            logger.error(f"Error decoding frame: {e}")
            return None

    def process_frame(self, frame: np.ndarray) -> tuple[dict, str | None, float]:
        """
        Process a single frame through the full pipeline.

        Args:
            frame: Input frame (BGR)

        Returns:
            Tuple of (prediction_dict, stable_sign, confidence)
        """
        prediction_dict = {
            "sign": None,
            "confidence": 0.0,
            "stable": False,
            "commit": False,
            "hands_detected": 0,
        }

        # Step 1: Detect landmarks
        landmarks_list, handedness_list, _ = self.mp_service.detect_landmarks(frame)

        if landmarks_list is None or len(landmarks_list) == 0:
            return prediction_dict, None, 0.0

        prediction_dict["hands_detected"] = len(landmarks_list)

        # Step 2: Pad features for 2 hands
        features = self.mp_service.pad_landmarks_for_two_hands(landmarks_list, handedness_list)

        # Step 3: Model prediction
        if not self.model_service.is_model_loaded():
            return prediction_dict, None, 0.0

        sign, confidence = self.model_service.predict(features)

        if sign is None:
            return prediction_dict, None, 0.0

        prediction_dict["sign"] = sign
        prediction_dict["confidence"] = confidence

        # Step 4: Temporal smoothing
        stable_sign, should_commit = self.smoothing.process_prediction(sign, confidence)

        if stable_sign is not None:
            prediction_dict["stable"] = True
            prediction_dict["commit"] = should_commit

        return prediction_dict, stable_sign, confidence

    def process_frame_from_base64(self, frame_base64: str) -> tuple[dict, str | None, float]:
        """
        Process a base64-encoded frame.

        Args:
            frame_base64: Base64 encoded JPEG frame

        Returns:
            Tuple of (prediction_dict, stable_sign, confidence)
        """
        frame = self.decode_frame(frame_base64)
        if frame is None:
            return {"sign": None, "confidence": 0.0, "stable": False}, None, 0.0

        return self.process_frame(frame)
