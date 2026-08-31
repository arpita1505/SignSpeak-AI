#!/usr/bin/env python3
"""Train ML models for sign recognition."""
import json
import logging
import numpy as np
from pathlib import Path
from datetime import datetime
from joblib import dump
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_prepared_data(processed_dir: str = "data/processed"):
    """Load prepared train/val/test data."""
    processed_dir = Path(processed_dir)

    if not (processed_dir / "X_train.npy").exists():
        logger.error("Prepared data not found. Run prepare_dataset.py first.")
        return None

    X_train = np.load(processed_dir / "X_train.npy")
    y_train = np.load(processed_dir / "y_train.npy")
    X_val = np.load(processed_dir / "X_val.npy")
    y_val = np.load(processed_dir / "y_val.npy")
    X_test = np.load(processed_dir / "X_test.npy")
    y_test = np.load(processed_dir / "y_test.npy")

    with open(processed_dir / "metadata.json") as f:
        metadata = json.load(f)

    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
        "X_test": X_test,
        "y_test": y_test,
        "metadata": metadata,
    }


def train_model(model_name: str, X_train, y_train, X_val, y_val):
    """Train a single model."""
    logger.info(f"Training {model_name}...")

    if model_name == "random_forest":
        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("classifier", RandomForestClassifier(n_estimators=100, random_state=42)),
            ]
        )
    elif model_name == "svm":
        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("classifier", SVC(kernel="rbf", probability=True, random_state=42)),
            ]
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")

    pipeline.fit(X_train, y_train)

    # Evaluate on validation set
    y_pred = pipeline.predict(X_val)
    accuracy = accuracy_score(y_val, y_pred)

    logger.info(f"{model_name} validation accuracy: {accuracy:.4f}")
    return pipeline, accuracy


def evaluate_model(pipeline, X_test, y_test, idx_to_label):
    """Evaluate model on test set."""
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
    macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

    metrics = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "macro_f1": float(macro_f1),
    }

    logger.info("Test Set Metrics:")
    for key, value in metrics.items():
        logger.info(f"  {key}: {value:.4f}")

    return metrics


def train_all(test_mode: bool = False):
    """Train all models and select the best."""
    data = load_prepared_data()
    if data is None:
        return

    X_train = data["X_train"]
    y_train = data["y_train"]
    X_val = data["X_val"]
    y_val = data["y_val"]
    X_test = data["X_test"]
    y_test = data["y_test"]
    metadata = data["metadata"]

    if test_mode:
        logger.info("Running in TEST mode with subset data")
        X_train = X_train[:100]
        y_train = y_train[:100]
        X_val = X_val[:20]
        y_val = y_val[:20]
        X_test = X_test[:20]
        y_test = y_test[:20]

    # Train models
    models = {}
    accuracies = {}

    for model_name in ["random_forest", "svm"]:
        try:
            pipeline, accuracy = train_model(model_name, X_train, y_train, X_val, y_val)
            models[model_name] = pipeline
            accuracies[model_name] = accuracy
        except Exception as e:
            logger.error(f"Error training {model_name}: {e}")

    if not models:
        logger.error("No models trained successfully")
        return

    # Select best model
    best_model_name = max(accuracies, key=accuracies.get)
    best_model = models[best_model_name]

    logger.info(f"Best model: {best_model_name} (accuracy: {accuracies[best_model_name]:.4f})")

    # Evaluate on test set
    test_metrics = evaluate_model(best_model, X_test, y_test, metadata["idx_to_label"])

    # Save model
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    model_path = artifacts_dir / "signspeak_model.joblib"
    dump(best_model, model_path)
    logger.info(f"Model saved to {model_path}")

    # Save metadata
    idx_to_label_str = {str(k): v for k, v in metadata["idx_to_label"].items()}
    model_metadata = {
        "version": "1.0.0",
        "created_at": datetime.utcnow().isoformat(),
        "algorithm": best_model_name.replace("_", " ").title(),
        "feature_dimension": metadata["feature_dimension"],
        "supported_labels": list(metadata["labels"].keys()),
        "train_size": metadata["train_size"],
        "val_size": metadata["val_size"],
        "test_size": metadata["test_size"],
        "metrics": test_metrics,
        "training_config": {
            "random_state": 42,
            "stratified_split": True,
        },
    }

    metadata_path = artifacts_dir / "model_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(model_metadata, f, indent=2)
    logger.info(f"Metadata saved to {metadata_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train ML models for sign recognition")
    parser.add_argument("--test", action="store_true", help="Run in test mode with subset data")

    args = parser.parse_args()
    train_all(test_mode=args.test)
