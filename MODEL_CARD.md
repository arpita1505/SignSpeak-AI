# Model Card — SignSpeak AI 1.0.0-realsign

Trained and evaluated on 2026-09-01. The deployable artifact is
`artifacts/signspeak_model.joblib`; machine-readable provenance is
`artifacts/model_metadata.json`.

## Model

- Task: isolated, static A–Z Indian Sign Language fingerspelling classification
- Selected classifier: RBF SVC (`C=10`, balanced class weights, probability output)
- Pipeline: `StandardScaler` → `SVC`
- Runtime: scikit-learn 1.6.1, random seed 42
- Input: 126 normalized MediaPipe hand-landmark features
- Output: one A–Z class plus an uncalibrated probability-like confidence
- Default confidence threshold: 0.75

Random Forest (300 trees) and SVC candidates were trained only on the 16,138-sample training split.
Selection used validation macro F1; the 4,052-sample test split was evaluated once after selection.

| Candidate | Validation accuracy | Validation macro F1 | Training time |
|---|---:|---:|---:|
| Random Forest | 0.8738 | 0.8598 | 3.160 s |
| **SVC (selected)** | **0.8802** | **0.8688** | **2.635 s** |

## Held-out test results

| Metric | Score |
|---|---:|
| Accuracy | 0.9055 |
| Macro precision | 0.9228 |
| Macro recall | 0.9052 |
| Macro F1 | 0.8968 |
| Weighted F1 | 0.9037 |

The full per-class report and confusion matrix are in `reports/metrics/` and
`reports/figures/confusion_matrix.png`.

At the 0.75 validation threshold, 88.34% of samples were accepted and accepted-sample accuracy was
95.58%. This threshold is an operating choice, not a formal calibration guarantee. Below-threshold
predictions are withheld; repeated above-threshold frames are temporally smoothed before commit.

## Intended use

This model supports educational/demo use for isolated static A–Z signs with a clearly visible hand
and similar camera conditions. It is not a continuous language translator, accessibility guarantee,
or substitute for a qualified interpreter. It must not be used for medical, legal, safety-critical,
identity, surveillance, or consequential decisions.

## Limitations and risks

- Signer IDs were unavailable. Exact duplicates were removed globally, but near-duplicate and signer
  leakage may remain, so results can overestimate new-user performance.
- No independent external-user, demographic-fairness, device, or low-light evaluation was run.
- MediaPipe detection failures are outside classifier metrics and can reduce end-to-end coverage.
- Static hand landmarks omit motion, face, body pose, spatial grammar, and linguistic context.
- Similar hand shapes, occlusion, unusual viewpoints, accessories, and mirrored-camera behavior may
  cause confident errors.
- SVC probability estimates are not formally calibrated.

Before a public accessibility deployment, perform signer-disjoint external evaluation with target
users, consent and privacy review, confidence calibration, error analysis, and usability testing.
