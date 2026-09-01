"""Temporal smoothing for stable predictions."""

from __future__ import annotations

import logging
from collections import deque
from time import time

from app.config import settings

logger = logging.getLogger(__name__)


class TemporalSmoothingService:
    """Service for temporal smoothing of predictions."""

    def __init__(
        self,
        stability_window: int = settings.stability_window,
        stability_min_count: int = settings.stability_min_count,
        cooldown_ms: int = settings.sign_cooldown_ms,
        confidence_threshold: float = settings.confidence_threshold,
    ):
        """
        Initialize temporal smoothing.

        Args:
            stability_window: Number of recent frames to consider
            stability_min_count: Minimum frames with same sign for stability
            cooldown_ms: Cooldown in milliseconds after emitting a sign
        """
        self.stability_window = stability_window
        self.stability_min_count = stability_min_count
        self.cooldown_ms = cooldown_ms
        self.confidence_threshold = confidence_threshold

        # State tracking
        self.prediction_history: deque = deque(maxlen=stability_window)
        self.last_emitted_sign: str | None = None
        self.last_emit_time: float = 0.0
        self.released_since_emit = True

    def process_prediction(self, sign: str | None, confidence: float) -> tuple[str | None, bool]:
        """
        Process a prediction with temporal smoothing.

        Args:
            sign: Predicted sign
            confidence: Confidence score

        Returns:
            Tuple of (stable_sign, should_commit)
            stable_sign: The sign if stable, None otherwise
            should_commit: Whether this should be added to translation
        """
        current_time = time() * 1000  # Convert to milliseconds

        # Skip if low confidence
        if sign is None or confidence < self.confidence_threshold:
            self.prediction_history.clear()
            self.released_since_emit = True
            return None, False

        # Add to history
        self.prediction_history.append(sign)

        # Check if we have enough predictions in window
        if len(self.prediction_history) < self.stability_min_count:
            return None, False

        # Count occurrences of each sign in window
        sign_counts = {}
        for pred in self.prediction_history:
            if pred is not None:
                sign_counts[pred] = sign_counts.get(pred, 0) + 1

        # Get most common sign
        if not sign_counts:
            return None, False

        most_common_sign = max(sign_counts, key=sign_counts.get)
        most_common_count = sign_counts[most_common_sign]

        # Check if it's stable
        if most_common_count < self.stability_min_count:
            return None, False

        # Check cooldown
        time_since_last = current_time - self.last_emit_time
        if time_since_last < self.cooldown_ms:
            return most_common_sign, False

        # Check if it's different from last emitted (or cooldown expired)
        if most_common_sign != self.last_emitted_sign or self.released_since_emit:
            self.last_emitted_sign = most_common_sign
            self.last_emit_time = current_time
            self.released_since_emit = False
            return most_common_sign, True

        return most_common_sign, False

    def reset(self):
        """Reset the temporal state."""
        self.prediction_history.clear()
        self.last_emitted_sign = None
        self.last_emit_time = 0.0
        self.released_since_emit = True
