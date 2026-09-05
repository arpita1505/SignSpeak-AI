# Architecture Documentation

## System Overview

SignSpeak AI follows a modular, three-tier architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT TIER (Browser)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            React Frontend (TypeScript)              │   │
│  │  - Camera capture (MediaDevices API)                │   │
│  │  - Frame encoding (JPEG)                            │   │
│  │  - WebSocket client                                 │   │
│  │  - Speech synthesis                                 │   │
│  │  - Translation UI                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│                    WebSocket (ws://)                        │
│                            ↓                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION TIER (Server)                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           FastAPI Application (Python)              │   │
│  │                                                     │   │
│  │  ┌────────────────────────────────────────────┐    │   │
│  │  │         WebSocket Handler                  │    │   │
│  │  │  - Frame reception                         │    │   │
│  │  │  - Message validation                      │    │   │
│  │  └────────────────────────────────────────────┘    │   │
│  │                      ↓                              │   │
│  │  ┌────────────────────────────────────────────┐    │   │
│  │  │    Inference Pipeline Service             │    │   │
│  │  │                                            │    │   │
│  │  │  1. Frame Decoding (base64 → OpenCV)     │    │   │
│  │  │  2. Hand Detection (MediaPipe)            │    │   │
│  │  │  3. Landmark Extraction (21 points × 3)   │    │   │
│  │  │  4. Normalization (translation/scale)     │    │   │
│  │  │  5. Feature Padding (2-hand support)      │    │   │
│  │  │                                            │    │   │
│  │  └────────────────────────────────────────────┘    │   │
│  │                      ↓                              │   │
│  │  ┌────────────────────────────────────────────┐    │   │
│  │  │   ML Model Service                         │    │   │
│  │  │  - sklearn Pipeline loaded                 │    │   │
│  │  │  - Features: [126] → Classes: A-Z          │    │   │
│  │  │  - Confidence scores                       │    │   │
│  │  │                                            │    │   │
│  │  └────────────────────────────────────────────┘    │   │
│  │                      ↓                              │   │
│  │  ┌────────────────────────────────────────────┐    │   │
│  │  │  Temporal Smoothing Service                │    │   │
│  │  │  - Prediction history (5-frame window)    │    │   │
│  │  │  - Stability check (4/5 frames same)      │    │   │
│  │  │  - Cooldown enforcement                    │    │   │
│  │  │  - Duplicate suppression                   │    │   │
│  │  │                                            │    │   │
│  │  └────────────────────────────────────────────┘    │   │
│  │                      ↓                              │   │
│  │  ┌────────────────────────────────────────────┐    │   │
│  │  │   REST API Endpoints                       │    │   │
│  │  │  - GET /api/health                         │    │   │
│  │  │  - GET /api/model/info                     │    │   │
│  │  │  - GET /api/labels                         │    │   │
│  │  │  - POST/GET /api/history                   │    │   │
│  │  │                                            │    │   │
│  │  └────────────────────────────────────────────┘    │   │
│  │                      ↓                              │   │
│  │  ┌────────────────────────────────────────────┐    │   │
│  │  │   Database Service (SQLAlchemy)            │    │   │
│  │  │  - Translation history persistence         │    │   │
│  │  │  - SQLite/PostgreSQL support               │    │   │
│  │  │                                            │    │   │
│  │  └────────────────────────────────────────────┘    │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    PERSISTENCE TIER                         │
│  ┌──────────────────────┐      ┌──────────────────────┐   │
│  │   SQLite/PostgreSQL  │      │   Model Artifacts    │   │
│  │   - Translations     │      │  - signspeak_model   │   │
│  │   - Sessions         │      │  - model_metadata.json
│  └──────────────────────┘      └──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (React/TypeScript)

**Key Components:**
- `App.tsx`: Root component, state orchestration
- `CameraPanel.tsx`: Webcam capture and control
- `PredictionCard.tsx`: Live prediction display
- `TranslationPanel.tsx`: Translation management
- `StatusBadge.tsx`: Connection/model status

**Hooks:**
- `useCamera()`: Camera lifecycle management
- `usePrediction()`: WebSocket communication

**Services:**
- `api.ts`: REST endpoints (health, labels, history)
- `websocket.ts`: WebSocket client with auto-reconnect
- `camera.ts`: MediaDevices wrapper
- `speech.ts`: Speech synthesis wrapper

**Data Flow:**
1. User clicks "Start Camera"
2. Browser requests mediaDevices permission
3. Video stream attached to `<video>` element
4. Capture loop draws frames to canvas
5. Canvas converted to base64 JPEG
6. Send via WebSocket to backend (5-10 FPS)
7. Receive predictions, update UI
8. On stable sign commit, append to translation text
9. User triggers Speak → browser SpeechSynthesis API

### 2. Backend (FastAPI/Python)

**Architecture Layers:**

#### API Layer (`app/api/`)
- Routes: REST endpoints, WebSocket handler
- Request/response validation via Pydantic
- Error handling and logging

#### Service Layer (`app/services/`)

**MediaPipeService**
```python
def detect_landmarks(frame) → (landmarks, handedness)
def normalize_landmarks(landmarks) → normalized_features
def pad_landmarks_for_two_hands(landmarks, handedness) → features[126]
```

Normalization strategy:
1. Reshape 63D (21 × 3) to 21 landmarks × 3 coordinates
2. Translate by wrist (landmark 0)
3. Scale by distance from wrist to middle finger tip (landmark 12)
4. Flatten back to 63D

Two-hand padding:
- Features ordered: [Left hand 63D] + [Right hand 63D] = 126D
- Missing hands filled with zeros
- Deterministic: Left before Right by MediaPipe handedness

**ModelService**
```python
def load_model() → joblib Pipeline
def predict(features[126]) → (label, confidence)
def get_model_version() → str
```

Model format:
```python
Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier or SVC)
])
```

Supports both `predict()` and `predict_proba()` for confidence scores.

**TemporalSmoothingService**

```python
def process_prediction(sign, confidence) → (stable_sign, should_commit)
```

State machine:
```
Frame 1: [A=0.9]        → history=[A], no commit
Frame 2: [A=0.92]       → history=[A,A], no commit
Frame 3: [A=0.88]       → history=[A,A,A], no commit
Frame 4: [A=0.91]       → history=[A,A,A,A], COMMIT
Frame 5: [A=0.89]       → history=[A,A,A,A,A], no re-commit (cooldown)
Frame 6: [B=0.85]       → history=[A,A,A,B,B], after cooldown → COMMIT B
```

Configurable parameters:
- `stability_window`: # of frames to consider (default 5)
- `stability_min_count`: # of same predictions for stability (default 4)
- `sign_cooldown_ms`: Milliseconds before same sign can re-emit (default 800)

**InferenceService** (Orchestrator)
```python
def process_frame(frame) → prediction_dict
def process_frame_from_base64(base64_frame) → prediction_dict
```

Chains: Frame → MediaPipe → Model → Smoothing

#### Model Layer (`app/models/`)
- `TranslationHistory`: SQLAlchemy ORM model

#### Schema Layer (`app/schemas/`)
- Pydantic models for validation/documentation

#### Database Layer (`app/db/`)
- SQLAlchemy setup
- Session management
- Migration support (Alembic-ready)

### 3. ML Pipeline

#### Data Collection (`ml/collect_data.py`)
- OpenCV webcam capture
- MediaPipe landmark extraction
- Normalization
- Stratified sampling (avoid duplicates)
- File storage (`.npy` files)

#### Data Preprocessing (`ml/prepare_dataset.py`)
- Load all collected samples
- Stratified train/val/test split (80/10/10)
- Deterministic split (random_state=42)
- Class imbalance detection
- Metadata generation

#### Model Training (`ml/train.py`)
- Candidates: Random Forest, SVM
- Hyperparameters fixed (not tuned)
- Validation-based model selection
- Test set evaluation
- Artifact generation:
  - `artifacts/signspeak_model.joblib`: Trained Pipeline
  - `artifacts/model_metadata.json`: Metrics + config

#### Model Evaluation (`ml/evaluate.py`)
- Confusion matrix visualization
- Classification report per class
- Metrics saved to reports/

## Feature Vector Design

### Landmark Coordinates

MediaPipe Hands provides 21 landmarks:
- Wrist (0)
- Thumb (1-4)
- Index finger (5-8)
- Middle finger (9-12)
- Ring finger (13-16)
- Pinky (17-20)

Each landmark: (x, y, z) ∈ [0, 1] × [0, 1] × [-1, 1]
- x, y: Normalized to [0, 1] image coordinates
- z: Depth (relative to wrist)

### Normalization (63D per hand)

```python
# Input: landmarks[21, 3] from MediaPipe
wrist = landmarks[0]
landmarks_centered = landmarks - wrist  # Translation invariant

# Scale
scale = ||landmarks[12] - landmarks[0]||  # Wrist to middle finger tip
landmarks_normalized = landmarks_centered / scale  # Scale invariant

# Output: 21 × 3 = 63D
```

### Two-Hand Padding (126D)

```python
features = [
    *normalize(left_hand),    # 63D or zeros
    *normalize(right_hand),   # 63D or zeros
]
# Total: 126D
```

## WebSocket Protocol

### Frame Transmission (Browser → Server)

Rate: 5-10 FPS (configurable)

```json
{
  "frame": "base64_encoded_jpeg_data"
}
```

JPEG compression ratio: 0.8 (80% quality)
Frame size: ~5-10 KB compressed

### Prediction Response (Server → Browser)

#### Prediction with stable sign:
```json
{
  "type": "prediction",
  "sign": "A",
  "confidence": 0.96,
  "stable": true,
  "commit": true,
  "hands_detected": 1,
  "timestamp": "2024-01-01T12:00:00.123456"
}
```

#### No hand:
```json
{
  "type": "no_hand"
}
```

#### Low confidence:
```json
{
  "type": "low_confidence",
  "confidence": 0.45
}
```

#### Error:
```json
{
  "type": "error",
  "message": "Model not loaded"
}
```

## Deployment Architecture

### Docker Container

**Multi-stage build:**

Stage 1: Node.js
- `npm ci` (exact versions via package-lock.json)
- `npm run build` → `frontend/dist/`

Stage 2: Python
- Install system dependencies (OpenCV, etc.)
- `pip install -e .` (backend)
- Copy `frontend/dist/` into Python app
- Non-root user (UID 1000)
- Healthcheck endpoint

**Image layers:**
1. Python base image
2. System dependencies
3. Python dependencies (cached)
4. Backend code
5. Frontend dist

### Port Binding

- Port 8000 (configurable via PORT env var)
- Render: Reads PORT from environment
- Health endpoint: `/api/health` (30s interval)

### Environment Parity

| Component | Dev | Docker | Render |
|-----------|-----|--------|--------|
| Database | SQLite | SQLite (file) | PostgreSQL (via DATABASE_URL) |
| Host | localhost | 0.0.0.0 | 0.0.0.0 |
| Port | 8000 | 8000 | $PORT env |
| Frontend | Vite dev server | Nginx (static) | Nginx (static) |
| TLS | ❌ | ❌ | ✅ |

## Performance Considerations

### Inference Latency
- Frame capture: ~5ms
- MediaPipe detection: ~50-100ms
- Normalization: ~1ms
- Model prediction: ~5-20ms
- Smoothing: <1ms
- **Total: ~60-150ms per frame**
- @ 10 FPS: ~100ms between requests

### Memory Usage
- Model (joblib): ~100-200 MB (loaded once)
- MediaPipe resources: ~50 MB
- Per-frame: ~10 MB (temporarily)

### WebSocket Optimization
- Frame rate: 5-10 FPS (not 30 FPS)
- JPEG compression: 80% quality
- Backpressure: Don't queue frames if server busy
- Connection reuse: Single WebSocket per session

## Error Handling

### Client-Side
- Camera unavailable: Show permission prompt
- WebSocket disconnect: Auto-reconnect with exponential backoff
- Model not loaded: Disable predictions, show status
- Invalid response: Log and ignore

### Server-Side
- Missing frame: Return error event
- Model inference failure: Log + error event
- Database unavailable: History operations fail, predictions continue
- Invalid JSON: Parse error response

## Security Considerations

1. **Input Validation**
   - Frame size limits (5 MB)
   - WebSocket message size limit
   - JSON schema validation

2. **Privacy**
   - Frames not persisted
   - Landmarks not stored
   - History contains text only
   - User consent for camera

3. **Authentication** (Future)
   - Optional user sessions
   - History per user
   - API key for production

## Testing Strategy

### Unit Tests (Backend)
- MediaPipe normalization
- Temporal smoothing state machine
- Model prediction format
- API endpoint responses
- Database operations

### Frontend Tests
- Component rendering
- Camera hook lifecycle
- WebSocket mock handling
- Translation text updates
- Button interactions

### Integration Tests
- End-to-end frame processing
- WebSocket message flow
- History persistence
- Model loading and inference

### Smoke Tests
- Application startup
- Health endpoint
- Basic API endpoints
- Docker container health check

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-09-05
