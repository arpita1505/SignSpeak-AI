#!/usr/bin/env python3
"""Extract production-compatible MediaPipe features from RealSign images."""
from __future__ import annotations
import argparse, hashlib, json, logging
from collections import Counter
from pathlib import Path
import cv2
import numpy as np
from app.services.mediapipe_service import MediaPipeService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)
SPLITS = (("Training", "train"), ("Validation", "val"), ("Testing", "test"))

def extract(source: Path, output: Path, limit: int | None = None) -> dict:
    service = MediaPipeService(static_image_mode=True)
    seen: set[str] = set(); output.mkdir(parents=True, exist_ok=True)
    meta: dict = {"source": str(source), "feature_dimension": 126, "splits": {}}
    for source_split, split in SPLITS:
        xs=[]; ys=[]; paths=[]; counts=Counter(); skipped=Counter()
        for label_dir in sorted((source/source_split).iterdir()):
            if not label_dir.is_dir(): continue
            for path in sorted(label_dir.iterdir()):
                if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}: continue
                if limit is not None and counts[label_dir.name] >= limit: continue
                digest=hashlib.sha256(path.read_bytes()).hexdigest()
                if digest in seen: skipped["exact_duplicate"] += 1; continue
                seen.add(digest)
                frame=cv2.imread(str(path))
                if frame is None: skipped["corrupt"] += 1; continue
                landmarks, handedness, _=service.detect_landmarks(frame)
                if not landmarks: skipped["no_hand"] += 1; continue
                vector=service.pad_landmarks_for_two_hands(landmarks, handedness)
                if vector.shape != (126,) or not np.isfinite(vector).all(): skipped["invalid"] += 1; continue
                xs.append(vector.astype(np.float32)); ys.append(label_dir.name)
                paths.append(str(path.relative_to(source))); counts[label_dir.name] += 1
                if len(xs) % 500 == 0: log.info("%s: %d", split, len(xs))
        if not xs: raise RuntimeError(f"No usable samples for {source_split}")
        np.save(output/f"X_{split}.npy", np.stack(xs)); np.save(output/f"y_{split}.npy", np.asarray(ys))
        (output/f"paths_{split}.json").write_text(json.dumps(paths, indent=2))
        meta["splits"][split]={"samples":len(xs),"class_counts":dict(sorted(counts.items())),"skipped":dict(skipped)}
        log.info("%s complete: %d, skipped=%s", split, len(xs), dict(skipped))
    meta["labels"]=sorted(set(np.load(output/"y_train.npy").tolist()))
    meta["normalization"]="wrist translation; wrist-to-middle-fingertip scale; left/right slots; zero padding"
    meta["split_method"]="publisher directories after global exact-file deduplication; signer IDs unavailable"
    (output/"metadata.json").write_text(json.dumps(meta, indent=2)); return meta

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--source",type=Path,default=Path("data/raw/realsign")); p.add_argument("--output",type=Path,default=Path("data/processed")); p.add_argument("--limit-per-class",type=int)
    a=p.parse_args(); extract(a.source,a.output,a.limit_per_class)
