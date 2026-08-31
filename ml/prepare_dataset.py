#!/usr/bin/env python3
"""Prepare dataset for training."""
import json
import logging
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_dataset(data_dir: str = "data/raw") -> tuple:
    """Load all collected data."""
    data_dir = Path(data_dir)
    X = []
    y = []
    label_to_idx = {}
    idx_to_label = {}
    label_idx = 0

    for label_dir in sorted(data_dir.iterdir()):
        if not label_dir.is_dir():
            continue

        label = label_dir.name
        label_to_idx[label] = label_idx
        idx_to_label[label_idx] = label
        label_idx += 1

        files = list(label_dir.glob("*.npy"))
        logger.info(f"Loading {label}: {len(files)} samples")

        for file in files:
            try:
                landmarks = np.load(file)
                if landmarks.shape != (63,):
                    logger.warning(f"Skipping {file}: invalid shape {landmarks.shape}")
                    continue
                X.append(landmarks)
                y.append(label_to_idx[label])
            except Exception as e:
                logger.error(f"Error loading {file}: {e}")

    X = np.array(X)
    y = np.array(y)

    logger.info(f"Loaded {len(X)} samples from {len(label_to_idx)} labels")
    return X, y, label_to_idx, idx_to_label


def check_imbalance(y: np.ndarray, idx_to_label: dict) -> None:
    """Check class imbalance."""
    unique, counts = np.unique(y, return_counts=True)
    logger.info("Class distribution:")
    for idx, count in zip(unique, counts):
        label = idx_to_label[idx]
        logger.info(f"  {label}: {count} samples")

    if len(counts) > 0:
        max_count = np.max(counts)
        min_count = np.min(counts)
        imbalance_ratio = max_count / min_count if min_count > 0 else 0
        if imbalance_ratio > 3:
            logger.warning(f"Class imbalance detected: {imbalance_ratio:.2f}x")


def prepare_dataset(test_size: float = 0.2, val_size: float = 0.2) -> None:
    """Prepare train/val/test split."""
    # Load data
    X, y, label_to_idx, idx_to_label = load_dataset()

    if len(X) == 0:
        logger.error("No data found. Run data collection first.")
        return

    # Check imbalance
    check_imbalance(y, idx_to_label)

    # Split into train and temp (val + test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=(test_size + val_size), random_state=42, stratify=y
    )

    # Split temp into val and test
    val_size_relative = val_size / (val_size + test_size)
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=1 - val_size_relative,
        random_state=42,
        stratify=y_temp,
    )

    # Save splits
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    np.save(output_dir / "X_train.npy", X_train)
    np.save(output_dir / "y_train.npy", y_train)
    np.save(output_dir / "X_val.npy", X_val)
    np.save(output_dir / "y_val.npy", y_val)
    np.save(output_dir / "X_test.npy", X_test)
    np.save(output_dir / "y_test.npy", y_test)

    # Save metadata
    metadata = {
        "labels": label_to_idx,
        "idx_to_label": {str(k): v for k, v in idx_to_label.items()},
        "feature_dimension": 63,
        "train_size": len(X_train),
        "val_size": len(X_val),
        "test_size": len(X_test),
        "total_size": len(X),
    }

    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    logger.info(f"Saved to {output_dir}")


if __name__ == "__main__":
    prepare_dataset()
