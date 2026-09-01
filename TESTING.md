# Testing Guide

## Test Suites

### 1. Backend Unit Tests

**Location:** `backend/tests/`

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

**What's Tested:**
- MediaPipe landmark normalization
- Temporal smoothing state machine
- Model prediction format
- API endpoint responses
- Database operations

**Test Files:**
- `test_mediapipe_service.py`: Landmark processing
- `test_smoothing_service.py`: Temporal logic
- `test_api.py`: REST endpoints

### 2. Frontend Component Tests

**Location:** `frontend/src/components/`

```bash
cd frontend
npm test
npm run test:ui  # Vitest UI
npm run coverage
```

**What's Tested:**
- Component rendering
- User interactions
- Hook behavior
- Error states

**Framework:** Vitest + React Testing Library

### 3. Integration Tests (E2E)

**Framework:** Playwright (implemented; camera, WebSocket, prediction, editing, speech, cleanup,
and unavailable-model states are browser-tested with deterministic mocks)

```bash
npx playwright install chromium
npm run test:e2e
```

### 4. ML Pipeline Tests

**Location:** `ml/`

Tests are implicit in the pipeline scripts:

```bash
# Test data collection
python ml/collect_data.py --label A --samples 50

# Test preprocessing
python ml/prepare_dataset.py

# Reproduce RealSign feature extraction and training only when inputs or pipeline change
python ml/extract_realsign.py
python ml/train_realsign.py

# Run held-out production-service samples without retraining
python ml/sample_inference.py
```

### 5. Smoke Tests

**Purpose:** Verify deployed application functionality

```bash
./scripts/smoke_test.sh

# Or specify API URL
API_URL=http://localhost:8000 ./scripts/smoke_test.sh
```

**Checks:**
- Health endpoint responds
- Labels endpoint works
- Model info endpoint works
- Database accessible

## Running All Tests

### Quick Test Run (Backend + Frontend)

```bash
./scripts/test_all.sh
```

### Complete Test Cycle

```bash
# Backend
cd backend
pip install -e ".[dev]"
pytest tests/ -v
black . --check
ruff check .
cd ..

# Frontend
cd frontend
npm ci
npm run lint
npm run type-check
npm test -- --run
npm run build
cd ..
```

## Test Configuration

### Backend (pytest)

**Config:** `backend/pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "--cov=app --cov-report=html --cov-report=term-missing"
```

**Environment:** `backend/tests/conftest.py`

```python
os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"  # In-memory DB
```

### Frontend (Vitest)

**Config:** `frontend/vitest.config.ts`

```typescript
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
  },
})
```

## Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| Backend | ≥80% | TBD |
| Frontend | ≥75% | TBD |
| ML Pipeline | N/A | Manual |

### Generate Coverage Report

```bash
# Backend
cd backend
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html  # macOS

# Frontend
cd frontend
npm run coverage
```

## Continuous Integration

Tests run automatically on:
- Push to any branch
- Pull requests

**Workflow:** `.github/workflows/ci.yml`

### CI Stages

1. **Backend Lint** (`ruff`, `black`)
2. **Backend Tests** (`pytest`)
3. **Frontend Lint** (`eslint`)
4. **Frontend Type Check** (`tsc`)
5. **Frontend Tests** (`vitest`)
6. **Frontend Build** (`vite build`)
7. **Docker Build** (multi-stage)

All must pass before merge.

## Manual Testing Checklist

### Backend API

```bash
# Health check
curl http://localhost:8000/api/health

# Model info
curl http://localhost:8000/api/model/info

# Labels
curl http://localhost:8000/api/labels

# History (create)
curl -X POST http://localhost:8000/api/history \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello"}'

# History (get)
curl http://localhost:8000/api/history

# History (delete all)
curl -X DELETE http://localhost:8000/api/history
```

### WebSocket

```bash
# Connect
wscat -c ws://localhost:8000/ws/predict

# Send frame (via Python or Node)
echo '{"frame":"<base64>"}' | send to WebSocket
```

### Frontend UI

- [ ] Camera starts/stops
- [ ] Predictions display
- [ ] Confidence bar updates
- [ ] Status shows correct state
- [ ] Translation text updates on commit
- [ ] Space button works
- [ ] Delete button works
- [ ] Clear button works
- [ ] Speak button speaks
- [ ] Save button saves to history
- [ ] Responsive on mobile
- [ ] Dark mode compatibility (if implemented)

### ML Pipeline

```bash
# Step 1: Collect data
python ml/collect_data.py --label A --samples 50
python ml/collect_data.py --label B --samples 50
# ... etc

# Step 2: Prepare
python ml/prepare_dataset.py

# Step 3: Train
python ml/train.py

# Step 4: Evaluate
python ml/evaluate.py

# Verify artifacts
ls -la artifacts/
```

### Docker

```bash
# Build
docker build -t signspeak-ai .

# Run
docker run -p 8000:8000 signspeak-ai

# Test
./scripts/smoke_test.sh

# Clean
docker rmi signspeak-ai
```

## Debugging

### Backend Debug

```bash
# Run with verbose logging
RUST_LOG=debug uvicorn app.main:app --reload

# Or in Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Frontend Debug

```bash
# Browser DevTools (F12 in Firefox/Chrome)
# Console shows WebSocket messages
# Network tab shows requests

# Or enable debug logging:
localStorage.setItem('debug', 'signspeak-ai:*')
```

### Camera Issues

```bash
# Test webcam directly
python -c "
import cv2
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if ret:
        print(f'Frame shape: {frame.shape}')
    else:
        print('Cannot read frame')
    break
"
```

### MediaPipe Issues

```bash
# Verify MediaPipe installation
python -c "import mediapipe as mp; print(mp.__version__)"

# Test landmark detection
python -c "
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands.Hands()
cap = cv2.VideoCapture(0)

ret, frame = cap.read()
if ret:
    results = mp_hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    print(f'Hands detected: {bool(results.multi_hand_landmarks)}')
"
```

## Performance Testing

### Latency Profiling

```python
import time
from app.services.inference_service import InferenceService

service = InferenceService()

# Measure inference time
start = time.time()
pred_dict, stable_sign, conf = service.process_frame_from_base64(frame_base64)
latency = time.time() - start

print(f"Inference latency: {latency*1000:.1f}ms")
```

### Memory Profiling

```bash
# Monitor memory usage
cd backend
python -m memory_profiler script.py
```

### Load Testing

```bash
# Simple load test with Apache Bench
ab -n 100 -c 10 http://localhost:8000/api/health

# Or use Locust
pip install locust
locust -f locustfile.py
```

## Known Test Issues

⚠️ **Webcam-dependent tests:**
- E2E tests with real camera
- Live prediction testing
- Real user acceptance testing

These require manual verification or hardware mocking.

⚠️ **Model-dependent tests:**
- Real inference accuracy tests
- Confusion matrix visualization
- Cross-user evaluation

These require actual trained model (not available until data collected).

## Test Report Generation

```bash
# Backend coverage
cd backend
pytest tests/ --html=report.html --self-contained-html

# Frontend coverage
cd frontend
npm run coverage:html

# ML evaluation
cd ..
python ml/evaluate.py  # Creates reports/figures/confusion_matrix.png
```

---

**Testing Documentation Version:** 1.0  
**Last Updated:** 2024
