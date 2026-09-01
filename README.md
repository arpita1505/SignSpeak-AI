# SignSpeak AI

Real-Time Indian Sign Language to Text and Speech Translator Using Computer Vision

> **Verified release (2026-09-01):** the repository includes a real A–Z model trained on the
> CC0-licensed [RealSign Indian Sign Language Dataset](https://github.com/RealSign62/RealSign-Indian-Sign-Language-Dataset).
> After global exact deduplication and MediaPipe filtering, the splits contain 16,138 train, 2,179
> validation, and 4,052 held-out test feature vectors. The selected RBF SVC achieved **0.9055 test
> accuracy** and **0.8968 macro F1**. This product recognizes isolated static fingerspelling; it is
> not continuous ISL translation. See `DATASET_CARD.md`, `MODEL_CARD.md`, and
> `FINAL_VERIFICATION.md` for provenance, limitations, and measured verification.

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue)

## Overview

SignSpeak AI is a full-stack application that recognizes isolated Indian Sign Language (ISL) signs in real-time using your webcam and converts them into text, which can then be spoken aloud using text-to-speech technology.

The system uses:
- **MediaPipe** for hand landmark detection
- **Machine Learning** for sign classification
- **FastAPI** backend with WebSocket support
- **React** frontend with real-time streaming

## Features

- 🎥 Real-time webcam capture
- 🤚 Hand landmark detection with MediaPipe
- 🧠 ML-based sign classification
- 📊 Temporal smoothing for stable predictions
- 💬 Text-to-speech conversion
- 💾 Translation history storage
- 🎨 Responsive modern UI
- 🐳 Docker containerization
- ✅ Comprehensive testing suite

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Webcam access
- macOS/Linux/Windows

### Installation

1. Enter your checked-out repository:
```bash
cd /path/to/CGMS
```

2. Backend setup:
```bash
cd backend
python -m pip install --upgrade pip
pip install -e ".[dev]"
cd ..
```

3. Frontend setup:
```bash
cd frontend
npm install
cd ..
```

### Dataset Setup

#### Option A: Collect your own data

1. Collect samples for each sign:
```bash
python ml/collect_data.py --label A --samples 300
python ml/collect_data.py --label B --samples 300
# ... repeat for all signs (A-Z)
```

2. Prepare dataset:
```bash
python ml/prepare_dataset.py
```

3. Train model:
```bash
python ml/train.py
```

4. Evaluate:
```bash
python ml/evaluate.py
```

#### Option B: Reproduce the RealSign model

Place the publisher's extracted Training, Validation, and Testing directories under
`data/raw/realsign/`, then run:

```bash
python ml/extract_realsign.py
python ml/train_realsign.py
python ml/sample_inference.py
```

The repository already contains the verified deployable artifact; do not retrain merely to run it.

### Running Development Server

```bash
./scripts/dev.sh
```

Or manually:

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Access: http://localhost:5173

### Running with Docker

```bash
docker compose up --build
```

Access: http://localhost:8000

## Usage

1. **Open Application**: Navigate to http://localhost:5173 (dev) or http://localhost:8000 (docker)

2. **Start Camera**: Click "Start Camera" and allow webcam access

3. **Perform Sign**: Hold up a sign in front of webcam

4. **Automatic Recognition**: System detects and translates sign to text

5. **Manual Controls**:
   - **Space**: Add space between words
   - **Delete**: Remove last character
   - **Clear**: Clear entire translation
   - **Speak**: Convert text to speech
   - **Save**: Store translation to history

## Architecture

### High-Level Flow

```
Webcam Frame
    ↓
[Browser MediaDevices API]
    ↓
Base64 JPEG Frame (5-10 FPS)
    ↓
[WebSocket]
    ↓
[FastAPI Backend]
    ↓
[MediaPipe Hand Landmark Detection]
    ↓
21 Hand Landmarks × 3 (x, y, z)
    ↓
[Landmark Normalization]
    ↓
Feature Vector (126 dimensions)
    ↓
[ML Model Prediction]
    ↓
[Temporal Smoothing]
    ↓
Stable Sign
    ↓
[WebSocket Response]
    ↓
[React Frontend UI Update]
    ↓
Text/Translation & TTS
```

### Directory Structure

```
signspeak-ai/
├── frontend/              # React TypeScript application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # API/WebSocket services
│   │   ├── types/        # TypeScript types
│   │   ├── utils/        # Utility functions
│   │   └── App.tsx
│   └── package.json
│
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── services/    # Business logic
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── db/          # Database
│   │   ├── ml/          # ML integrations
│   │   ├── config.py    # Configuration
│   │   └── main.py      # App entry
│   ├── tests/           # Unit tests
│   └── pyproject.toml
│
├── ml/                  # ML pipeline
│   ├── collect_data.py      # Webcam data collection
│   ├── prepare_dataset.py   # Data preprocessing
│   ├── train.py             # Model training
│   └── evaluate.py          # Model evaluation
│
├── data/               # Dataset storage
│   ├── raw/           # Collected samples
│   └── processed/     # Split datasets
│
├── artifacts/         # Model artifacts
│   ├── signspeak_model.joblib
│   └── model_metadata.json
│
├── scripts/           # Utility scripts
│   ├── dev.sh
│   ├── test_all.sh
│   └── smoke_test.sh
│
└── Dockerfile         # Production container
```

## API Documentation

### REST Endpoints

#### Health Check
```http
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_version": "1.0.0",
  "database": "ok"
}
```

#### Model Info
```http
GET /api/model/info
```

Response:
```json
{
  "version": "1.0.0",
  "algorithm": "SVC",
  "feature_dimension": 126,
  "supported_labels": ["A", "B", "C", ...],
  "metrics": {
    "accuracy": 0.9054787759131293,
    "macro_f1": 0.8967902795968558
  }
}
```

#### Labels
```http
GET /api/labels
```

#### Translation History
```http
GET /api/history           # List all
POST /api/history          # Create entry
DELETE /api/history        # Clear all
DELETE /api/history/{id}   # Delete one
```

### WebSocket

#### Connection
```
ws://localhost:8000/ws/predict
```

#### Send Frame
```json
{
  "frame": "base64_encoded_jpeg"
}
```

#### Receive Prediction
```json
{
  "type": "prediction",
  "sign": "A",
  "confidence": 0.96,
  "stable": true,
  "commit": true,
  "hands_detected": 1,
  "timestamp": "2024-01-01T12:00:00"
}
```

Or:
```json
{
  "type": "no_hand"
}
```

```json
{
  "type": "low_confidence",
  "confidence": 0.45
}
```

```json
{
  "type": "error",
  "message": "Model not loaded"
}
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm run coverage
```

### All Tests
```bash
./scripts/test_all.sh
```

### Smoke Test
```bash
# With app running
./scripts/smoke_test.sh

# Or specify URL
API_URL=http://localhost:8000 ./scripts/smoke_test.sh
```

## Model Training

### Data Collection

Collect 300+ samples per sign:
```bash
python ml/collect_data.py --label A --samples 300 --camera 0
```

### Dataset Preparation

```bash
python ml/prepare_dataset.py
```

This creates train/val/test splits with stratification.

### Training

```bash
python ml/train.py
```

Trains multiple models (Random Forest, SVM) and selects the best based on validation accuracy.

### Evaluation

```bash
python ml/evaluate.py
```

Generates confusion matrix and detailed metrics.

## Configuration

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Key variables:

```env
# Application
APP_ENV=development
PORT=8000

# Database
DATABASE_URL=sqlite:///./signspeak.db  # or PostgreSQL URL

# ML Model
MODEL_PATH=artifacts/signspeak_model.joblib
MODEL_METADATA_PATH=artifacts/model_metadata.json

# Inference
CONFIDENCE_THRESHOLD=0.75
STABILITY_WINDOW=5
STABILITY_MIN_COUNT=4
SIGN_COOLDOWN_MS=800

# Logging
LOG_LEVEL=INFO
```

## Deployment

### Docker

Build and run:
```bash
docker build -t signspeak-ai .
docker run -p 8000:8000 signspeak-ai
```

### Render

1. Push to GitHub
2. Create Render Web Service
3. Connect repository
4. Select Docker deployment
5. Set environment variables
6. Deploy

The application requires:
- Port: 8000
- Health check: `/api/health`
- HTTPS enabled (for webcam access)

### Environment Variables

For production:

```env
APP_ENV=production
DATABASE_URL=postgresql://user:pass@host:5432/signspeak
MODEL_PATH=/app/artifacts/signspeak_model.joblib
LOG_LEVEL=WARNING
```

## Limitations

### Current Version (1.0.0)

✅ **Supports:**
- Isolated ISL fingerspelling (individual characters A-Z)
- Single-hand and dual-hand signs
- Real-time recognition at ~10 FPS
- Landmark-based classification
- Simple gesture controls

❌ **Does NOT Support:**
- Continuous sign-to-sentence translation
- Dynamic signs requiring movement
- Facial expression recognition
- Two-handed coordinated signs
- Grammar-aware translation
- Emotional/contextual interpretation

### Known Issues

- Lighting changes affect accuracy
- Similar hand shapes may be confused
- Static classifier cannot fully model temporal dynamics
- Requires clear hand visibility

### Future Enhancements

- [ ] LSTM/Transformer for temporal modeling
- [ ] Expanded vocabulary (100+ signs)
- [ ] Facial landmark integration
- [ ] Pose features
- [ ] Hindi/Regional language output
- [ ] Mobile app
- [ ] On-device inference
- [ ] Personalized calibration

## Privacy & Security

### Data Collection

- ✅ Webcam frames processed locally in browser
- ✅ Frames transmitted only to backend (not stored)
- ✅ Raw landmarks not persisted
- ✅ Translation history contains text only
- ❌ Optional: Can disable history storage

### Security Measures

- CORS configured appropriately
- Input validation on all endpoints
- WebSocket payload size limits
- No arbitrary file access
- Dependency scanning in CI/CD
- HTTPS recommended for production

## Troubleshooting

### Camera Not Working

```
Permission denied: Grant webcam access in browser settings
Camera unavailable: Check device is not in use by another app
No image: Try different camera index with --camera flag
```

### Model Not Loading

```
Check artifacts/ directory exists
Verify model_metadata.json is present
Run: python ml/train.py to create model
```

### WebSocket Connection Failed

```
Check backend is running
Verify firewall allows port 8000
Check browser console for detailed error
Try http://localhost:8000 instead of hostname
```

### Low Recognition Accuracy

```
Collect more training data for problematic signs
Ensure good lighting during collection
Verify data is representative of user population
Check model training completed successfully
Review confusion matrix to identify confusing signs
```

## Development

### Project Setup for Contributors

```bash
# Clone
git clone <repo>
cd signspeak-ai

# Backend
cd backend
pip install -e ".[dev]"  # With dev dependencies
pre-commit install      # (optional) Set up pre-commit hooks
cd ..

# Frontend
cd frontend
npm install
npm run lint  # Check code style
cd ..

# Run tests
./scripts/test_all.sh
```

### Code Style

**Backend:** Ruff + Black
```bash
cd backend
ruff check .
black . --check
```

**Frontend:** ESLint + TypeScript
```bash
cd frontend
npm run lint
npm run type-check
```

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and test
4. Run linting and tests
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citations

- MediaPipe: https://github.com/google-ai-edge/mediapipe
- scikit-learn: https://scikit-learn.org/
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/

## Contact

For questions or issues, please open a GitHub issue or contact the maintainers.

---

**Made with ❤️ for accessible communication**
