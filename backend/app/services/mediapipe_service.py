"""MediaPipe hand landmark detection service."""
from __future__ import annotations

import logging

import cv2
import mediapipe as mp
import numpy as np

logger = logging.getLogger(__name__)


class MediaPipeService:
    """Service for hand landmark detection using MediaPipe."""

    def __init__(self, initialize_detector: bool = True):
        """Initialize MediaPipe hand detector."""
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) if initialize_detector else None
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands

    def detect_landmarks(
        self, frame: np.ndarray
    ) -> tuple[list | None, list | None, list | None]:
        """
        Detect hand landmarks from a frame.

        Args:
            frame: Input image frame (BGR format)

        Returns:
            Tuple of (landmarks_list, handedness_list, processed_frame)
            landmarks_list: List of landmark arrays or None
            handedness_list: List of handedness strings or None
            processed_frame: Processed frame for visualization
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if self.hands is None:
                raise RuntimeError("MediaPipe detector is not initialized")
            results = self.hands.process(rgb_frame)

            landmarks_list = []
            handedness_list = []

            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(
                    results.multi_hand_landmarks, results.multi_handedness
                ):
                    # Extract landmarks
                    landmarks = []
                    for landmark in hand_landmarks.landmark:
                        landmarks.extend([landmark.x, landmark.y, landmark.z])
                    landmarks_list.append(np.array(landmarks))

                    # Get handedness (Left/Right)
                    hand_label = handedness.classification[0].label
                    handedness_list.append(hand_label)

            return (
                landmarks_list if landmarks_list else None,
                handedness_list if handedness_list else None,
                rgb_frame,
            )

        except Exception as e:
            logger.error(f"Error detecting landmarks: {e}")
            return None, None, None

    def draw_landmarks(
        self, frame: np.ndarray, landmarks_list: list | None
    ) -> np.ndarray:
        """
        Draw landmarks on frame.

        Args:
            frame: Input frame (RGB)
            landmarks_list: List of landmark arrays

        Returns:
            Frame with drawn landmarks
        """
        if landmarks_list is None:
            return frame

        try:
            for landmarks in landmarks_list:
                # Reshape landmarks to MediaPipe format
                reshaped = []
                for i in range(0, len(landmarks), 3):
                    x, y, z = landmarks[i : i + 3]
                    # Create a simple landmark-like object
                    class LandmarkObj:
                        pass

                    lm = LandmarkObj()
                    lm.x = x
                    lm.y = y
                    lm.z = z
                    reshaped.append(lm)

                # Draw connections manually
                h, w, _ = frame.shape
                for i, lm in enumerate(reshaped):
                    x, y = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

            return frame
        except Exception as e:
            logger.error(f"Error drawing landmarks: {e}")
            return frame

    def normalize_landmarks(self, landmarks: np.ndarray) -> np.ndarray:
        """
        Normalize landmarks to be invariant to position and scale.

        Args:
            landmarks: Array of shape (21*3,) with x, y, z coordinates

        Returns:
            Normalized landmarks array
        """
        if landmarks is None or len(landmarks) != 63:
            return landmarks

        try:
            # Reshape to (21, 3)
            landmarks = landmarks.reshape(21, 3)

            # Use wrist (landmark 0) as reference
            wrist = landmarks[0]
            landmarks_centered = landmarks - wrist

            # Normalize by the distance from wrist to middle finger tip (landmark 12)
            scale = np.linalg.norm(landmarks[12] - landmarks[0])
            if scale < 1e-6:
                scale = 1.0
            landmarks_normalized = landmarks_centered / scale

            # Flatten back
            return landmarks_normalized.flatten()
        except Exception as e:
            logger.error(f"Error normalizing landmarks: {e}")
            return landmarks

    def pad_landmarks_for_two_hands(
        self, landmarks_list: list | None, handedness_list: list | None
    ) -> np.ndarray:
        """
        Pad landmarks to support exactly 2 hands.

        Args:
            landmarks_list: List of landmark arrays
            handedness_list: List of handedness strings

        Returns:
            Feature vector with padded landmarks for 2 hands
        """
        # Initialize feature vector for 2 hands (21*3 * 2 = 126)
        feature_vector = np.zeros(126)

        if landmarks_list is None:
            return feature_vector

        # Determine hand order (Left first, Right second)
        hands = {}
        if handedness_list is None or len(handedness_list) != len(landmarks_list):
            return feature_vector
        for landmarks, handedness in zip(landmarks_list, handedness_list):
            hands[handedness] = self.normalize_landmarks(landmarks)

        # Fill in features
        idx = 0
        for hand_type in ["Left", "Right"]:
            if hand_type in hands:
                feature_vector[idx : idx + 63] = hands[hand_type]
            idx += 63

        return feature_vector
