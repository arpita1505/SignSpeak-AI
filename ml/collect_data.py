#!/usr/bin/env python3
"""Collect hand landmark data from webcam."""
import argparse
import json
import logging
import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
LABELS_CONFIG = {
    "A": "Letter A",
    "B": "Letter B",
    "C": "Letter C",
    "D": "Letter D",
    "E": "Letter E",
    "F": "Letter F",
    "G": "Letter G",
    "H": "Letter H",
    "I": "Letter I",
    "J": "Letter J",
    "K": "Letter K",
    "L": "Letter L",
    "M": "Letter M",
    "N": "Letter N",
    "O": "Letter O",
    "P": "Letter P",
    "Q": "Letter Q",
    "R": "Letter R",
    "S": "Letter S",
    "T": "Letter T",
    "U": "Letter U",
    "V": "Letter V",
    "W": "Letter W",
    "X": "Letter X",
    "Y": "Letter Y",
    "Z": "Letter Z",
}


def normalize_landmarks(landmarks: np.ndarray) -> np.ndarray:
    """Normalize landmarks."""
    if len(landmarks) != 63:
        return landmarks

    landmarks = landmarks.reshape(21, 3)
    wrist = landmarks[0]
    landmarks_centered = landmarks - wrist

    scale = np.linalg.norm(landmarks[12] - landmarks[0])
    if scale < 1e-6:
        scale = 1.0
    landmarks_normalized = landmarks_centered / scale

    return landmarks_normalized.flatten()


def collect_data(label: str, samples: int, camera_idx: int = 0):
    """Collect hand landmark data."""
    if label not in LABELS_CONFIG:
        logger.error(f"Unknown label: {label}")
        return

    output_dir = Path("data/raw") / label
    output_dir.mkdir(parents=True, exist_ok=True)

    mp_hands = mp.solutions.hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
    )

    cap = cv2.VideoCapture(camera_idx)
    if not cap.isOpened():
        logger.error("Cannot open camera")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    collected = 0
    fps = 0
    frame_count = 0

    logger.info(f"Collecting {samples} samples for label '{label}'")
    logger.info("Press SPACE to start collection, ESC to exit")

    collecting = False
    countdown = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape

        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_hands.process(rgb_frame)

        # Calculate FPS
        frame_count += 1
        if frame_count % 30 == 0:
            fps = 30.0 / (cv2.getTickCount() / cv2.getTickFrequency())

        # Draw status
        status_text = f"Label: {label} | Collected: {collected}/{samples}"
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if collecting:
            if countdown > 0:
                countdown -= 1
                cv2.putText(
                    frame,
                    f"Collecting in {countdown // 10 + 1}...",
                    (w // 2 - 100, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    (0, 255, 0),
                    2,
                )
            elif results.multi_hand_landmarks:
                landmarks = results.multi_hand_landmarks[0]
                landmark_data = []
                for landmark in landmarks.landmark:
                    landmark_data.extend([landmark.x, landmark.y, landmark.z])

                landmark_data = np.array(landmark_data)
                normalized = normalize_landmarks(landmark_data)

                # Save
                filename = output_dir / f"{collected:04d}.npy"
                np.save(filename, normalized)
                collected += 1

                if collected >= samples:
                    collecting = False
                    logger.info(f"Completed collecting {samples} samples!")
            else:
                cv2.putText(
                    frame,
                    "No hand detected!",
                    (w // 2 - 100, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

        else:
            cv2.putText(
                frame,
                "Press SPACE to start",
                (10, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 0),
                1,
            )

        # Draw landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for landmark in hand_landmarks.landmark:
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

        cv2.imshow(f"Collecting - {label}", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            if not collecting and collected < samples:
                collecting = True
                countdown = 30  # 3 seconds at 10 FPS

    cap.release()
    cv2.destroyAllWindows()
    logger.info(f"Saved {collected} samples to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect hand landmark data")
    parser.add_argument("--label", required=True, help="Label/sign to collect")
    parser.add_argument("--samples", type=int, default=300, help="Number of samples")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")

    args = parser.parse_args()
    collect_data(args.label, args.samples, args.camera)
