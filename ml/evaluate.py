#!/usr/bin/env python3
"""Evaluate model performance."""
import json
import logging
from pathlib import Path
from joblib import load
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def evaluate():
    """Evaluate the trained model."""
    model_path = Path("artifacts/signspeak_model.joblib")
    metadata_path = Path("artifacts/model_metadata.json")

    if not model_path.exists():
        logger.error(f"Model not found: {model_path}")
        return

    # Load model
    model = load(model_path)

    # Load metadata
    with open(metadata_path) as f:
        metadata = json.load(f)

    # Load test data
    X_test = np.load("data/processed/X_test.npy")
    y_test = np.load("data/processed/y_test.npy")

    # Predictions
    y_pred = model.predict(X_test)

    # Metrics
    logger.info("Classification Report:")
    idx_to_label = {int(k): v for k, v in metadata["metrics"].items()}
    labels = sorted(metadata["supported_labels"])
    report = classification_report(y_test, y_pred, target_names=labels, zero_division=0)
    logger.info(report)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    reports_dir = Path("reports/figures")
    reports_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    plt.savefig(reports_dir / "confusion_matrix.png")
    logger.info(f"Confusion matrix saved to {reports_dir / 'confusion_matrix.png'}")

    # Save classification report
    with open(reports_dir.parent / "classification_report.txt", "w") as f:
        f.write(report)

    logger.info("Evaluation complete")


if __name__ == "__main__":
    evaluate()
