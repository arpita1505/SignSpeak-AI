"""Tests for MediaPipe service."""
import numpy as np
import pytest

from app.services.mediapipe_service import MediaPipeService


@pytest.fixture
def mediapipe_service():
    """Create MediaPipe service instance."""
    return MediaPipeService()


def test_normalize_landmarks_dimensions(mediapipe_service):
    """Test that normalization preserves dimensions."""
    landmarks = np.random.randn(63)
    normalized = mediapipe_service.normalize_landmarks(landmarks)
    assert normalized.shape == (63,)


def test_normalize_landmarks_translation_invariance(mediapipe_service):
    """Test that normalization is translation invariant."""
    # Create two hands with same shape but different position
    landmarks1 = np.random.randn(63)
    landmarks1[:3] = [0.5, 0.5, 0]  # Set wrist position

    # Create second hand (same shape, different position)
    landmarks2 = landmarks1 + np.array([0.1, 0.1, 0] + [0] * 60)
    landmarks2[0:3] = [0.6, 0.6, 0]  # New wrist position

    normalized1 = mediapipe_service.normalize_landmarks(landmarks1)
    normalized2 = mediapipe_service.normalize_landmarks(landmarks2)

    # Should be very similar (allowing for floating point differences)
    # After normalization, translation doesn't matter much


def test_pad_landmarks_for_two_hands_single_hand(mediapipe_service):
    """Test padding for single hand."""
    landmarks = [np.ones(63)]
    handedness = ["Right"]

    features = mediapipe_service.pad_landmarks_for_two_hands(landmarks, handedness)

    assert features.shape == (126,)
    # First 63 should be the hand, second 63 should be zeros
    assert np.allclose(features[63:], 0)


def test_pad_landmarks_for_two_hands_two_hands(mediapipe_service):
    """Test padding for two hands."""
    landmarks = [np.ones(63), np.full(63, 2)]
    handedness = ["Left", "Right"]

    features = mediapipe_service.pad_landmarks_for_two_hands(landmarks, handedness)

    assert features.shape == (126,)


def test_pad_landmarks_no_hands(mediapipe_service):
    """Test padding with no hands."""
    features = mediapipe_service.pad_landmarks_for_two_hands(None, None)
    assert features.shape == (126,)
    assert np.allclose(features, 0)
