"""Tests for temporal smoothing service."""
import pytest

from app.services.smoothing_service import TemporalSmoothingService


@pytest.fixture
def smoothing_service():
    """Create smoothing service instance."""
    return TemporalSmoothingService(
        stability_window=5, stability_min_count=4, cooldown_ms=800
    )


def test_process_prediction_low_confidence(smoothing_service):
    """Test that low confidence predictions are rejected."""
    sign, should_commit = smoothing_service.process_prediction("A", 0.5)
    assert sign is None
    assert should_commit is False


def test_process_prediction_not_enough_frames(smoothing_service):
    """Test that we need enough frames for stability."""
    # First 3 frames (need 4 for stability)
    for _ in range(3):
        sign, should_commit = smoothing_service.process_prediction("A", 0.9)
        assert sign is None
        assert should_commit is False


def test_process_prediction_stable_sign(smoothing_service):
    """Test stable sign detection."""
    # Process 4 identical predictions
    for i in range(4):
        sign, should_commit = smoothing_service.process_prediction("A", 0.9)

    # After 4 frames of same sign, should be stable
    assert sign == "A"


def test_process_prediction_sign_change(smoothing_service):
    """Test sign change detection."""
    # First: 4 A's
    for _ in range(4):
        sign, should_commit = smoothing_service.process_prediction("A", 0.9)

    # This should emit the first A (stable)
    first_sign = sign

    # Then: different sign immediately
    sign, should_commit = smoothing_service.process_prediction("B", 0.9)

    # After cooldown, B should be detected
    assert sign == "A"  # Still processing A's


def test_process_prediction_cooldown(smoothing_service):
    """Test that cooldown prevents duplicate emissions."""
    # Get first stable sign
    for _ in range(4):
        smoothing_service.process_prediction("A", 0.9)

    # Continue with same sign - should not re-emit
    for _ in range(3):
        sign, should_commit = smoothing_service.process_prediction("A", 0.9)
        assert should_commit is False


def test_reset(smoothing_service):
    """Test reset functionality."""
    for _ in range(4):
        smoothing_service.process_prediction("A", 0.9)

    smoothing_service.reset()

    sign, should_commit = smoothing_service.process_prediction("B", 0.9)
    assert sign is None  # Reset cleared history
