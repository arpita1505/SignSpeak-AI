# Dataset Card — RealSign Indian Sign Language Dataset

Verified and processed on 2026-09-01.

## Source and license

- Dataset: [RealSign Indian Sign Language Dataset](https://github.com/RealSign62/RealSign-Indian-Sign-Language-Dataset)
- License: CC0-1.0 (as published by the source repository)
- Scope: static A–Z ISL fingerspelling images from four contributors
- Publisher layout: Training, Validation, and Testing directories

The downloaded archive is excluded from Git because it is about 657 MB and contains images of
people. Only derived 126-dimensional hand-landmark arrays are kept locally, also ignored.

## Audit and preprocessing

The source contained 25,977 labeled split images. Two files were unreadable. A global SHA-256 pass
found and removed 891 exact duplicate files, including publisher cross-split duplicates. MediaPipe
could not detect a hand in 2,716 additional images. The extraction pipeline retains the publisher's
split assignment after global exact-file deduplication and never moves test samples into training.

| Split | Usable features | No hand | Exact duplicates | Corrupt |
|---|---:|---:|---:|---:|
| Train | 16,138 | 1,916 | 144 | 0 |
| Validation | 2,179 | 291 | 109 | 0 |
| Test | 4,052 | 509 | 638 | 1 |
| **Total** | **22,369** | **2,716** | **891** | **1** |

All 26 labels A–Z occur in every processed split. Exact per-class counts are recorded in
`data/processed/metadata.json` and `artifacts/model_metadata.json`.

## Features

Each image is processed by the same `MediaPipeService` used at inference. Features are 126 floats:
21 x/y/z landmarks per hand, wrist-translated and wrist-to-middle-fingertip scaled, placed into
deterministic left/right slots, with a zero-filled slot when a hand is absent.

## Limitations

The source does not expose per-image signer or session IDs, so a signer-aware split could not be
constructed. Exact duplicates were removed globally, but near-duplicates and signer overlap may
remain; held-out scores may therefore overstate generalization to a new signer. Demographic,
lighting, device, and fairness coverage are undocumented. These are static images, so this dataset
does not establish performance on dynamic signs, facial grammar, body pose, or continuous ISL.

Reproduce extraction with `python ml/extract_realsign.py` after placing the publisher directories
under `data/raw/realsign/`. Existing processed artifacts should be reused unless source or
preprocessing changes.
