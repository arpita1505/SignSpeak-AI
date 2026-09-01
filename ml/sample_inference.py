#!/usr/bin/env python3
"""Run deterministic held-out images through the production inference pipeline."""
from __future__ import annotations

import json
from pathlib import Path

import cv2

from app.services.inference_service import InferenceService


def main() -> None:
    paths = json.loads(Path("data/processed/paths_test.json").read_text())
    chosen = []
    seen = set()
    for relative in paths:
        label = Path(relative).parent.name
        if label not in seen:
            chosen.append((label, relative))
            seen.add(label)
        if len(chosen) == 10:
            break

    service = InferenceService()
    for expected, relative in chosen:
        frame = cv2.imread(str(Path("data/raw/realsign") / relative))
        service.smoothing.reset()
        for _ in range(5):
            result, _, confidence = service.process_frame(frame)
        print(json.dumps({"expected": expected, "predicted": result["sign"], "confidence": round(confidence, 4)}))


if __name__ == "__main__":
    main()
