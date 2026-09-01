# Final Verification

Verified on 2026-09-01 in the local macOS and Docker environments.

## Status

REST health/model/label routes, history CRUD, deterministic two-hand features, confidence
filtering, release-aware smoothing, browser camera controls, sentence editing, browser speech, and
the production frontend build are implemented. Missing models are reported without random output.

This is an application for **isolated static ISL A–Z fingerspelling recognition**, not an
unrestricted continuous ISL translator. A genuine RealSign artifact is included and loaded once at
startup. Frames are size-bounded and validated; missing models fail closed without random output.

## Results

- Dataset: RealSign Indian Sign Language Dataset, CC0-1.0
- Processed splits: 16,138 train / 2,179 validation / 4,052 held-out test
- Cleaning: 891 global exact duplicates removed; 2,716 no-hand images rejected
- Supported signs: static A–Z
- Model: StandardScaler + RBF SVC, scikit-learn 1.6.1
- Held-out accuracy / macro F1 / weighted F1: 0.9055 / 0.8968 / 0.9037
- Operating confidence threshold: 0.75
- Backend Ruff: PASS
- Backend Black: PASS
- Backend pytest: PASS — 19 passed, 0 failed
- Frontend ESLint and TypeScript: PASS
- Frontend Vitest: PASS — 7 passed, 0 failed
- Frontend production build: PASS
- Docker build/start: PASS
- Container frontend, health, labels, and model endpoints: PASS
- Container health smoke: PASS
- WebSocket validation/error path: PASS
- Playwright E2E: PASS — 2 passed, 0 failed

## Remaining user actions

Perform an external signer-disjoint evaluation and a real-camera HTTPS usability test, then deploy
through the owner's authenticated hosting account. The publisher does not expose per-image signer
IDs: global exact deduplication was completed, but near-duplicate or signer overlap may remain and
the held-out metrics can overstate new-user generalization. No public URL is claimed yet.
