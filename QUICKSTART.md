# Quick Start Guide

Get SignSpeak AI running in 5 minutes!

## Option 1: Docker (Fastest)

### Prerequisite
- Docker installed

### Steps

```bash
cd signspeak-ai

# Build and run
docker compose up --build

# Wait for startup message:
# app-1  | INFO:     Uvicorn running at http://0.0.0.0:8000

# Open browser
# http://localhost:8000
```

✅ Done! The application is running.

## Option 2: Local Development (Recommended for Development)

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### Setup (2 minutes)

```bash
# Clone
git clone https://github.com/arpita1505/SignSpeak-AI.git
cd SignSpeak-AI

# Backend setup
cd backend
pip install -e ".[dev]"
cd ..

# Frontend setup
cd frontend
npm install
cd ..

# Copy environment
cp .env.example .env
```

### Run Development Servers

**Terminal 1: Backend**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Frontend**
```bash
cd frontend
npm run dev
```

**Access:** http://localhost:5173

## First Time Setup

### 1. Create Test Model

```bash
# Generate minimal test model for development
cd backend
python -m pip install -e ".[dev]"
cd ..

python ml/train.py --test
```

This creates `artifacts/signspeak_model.joblib` with test data.

### 2. Verify Setup

```bash
# Check backend
curl http://localhost:8000/api/health

# Check frontend
# http://localhost:5173 in browser
```

Expected responses:
- Backend: `{"status":"ok","model_loaded":true,...}`
- Frontend: SignSpeak AI app loads

## Using the Application

1. **Open the app** (http://localhost:5173 or http://localhost:8000)

2. **Click "Start Camera"**
   - Allow webcam access when prompted

3. **Make a sign**
   - System automatically recognizes and displays sign

4. **See translation**
   - Sign appears in translation panel

5. **Use controls**
   - Space: Add space
   - Delete: Remove character
   - Clear: Clear all
   - Speak: Text-to-speech
   - Save: Store to history

## Common Issues & Quick Fixes

### "Camera not working"
```bash
# Grant camera permission in browser settings
# Or use different camera:
python ml/collect_data.py --label A --camera 1
```

### "Model not loaded"
```bash
# Create test model
python ml/train.py --test

# Or train with real data
python ml/collect_data.py --label A --samples 50
python ml/prepare_dataset.py
python ml/train.py
```

### Port already in use
```bash
# Change port
export PORT=8001
uvicorn app.main:app --port 8001

# Or kill process using port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000 | findstr LISTENING  # Windows
```

### Dependencies not installed
```bash
# Backend
cd backend
pip install -e ".[dev]"

# Frontend
cd frontend
npm install
```

### WebSocket connection failed
- Check backend is running
- Check browser console for errors
- Try http://localhost:8000 (full-stack) instead of 5173 (frontend-only)

## Next Steps

After getting it running:

1. **Collect Real Data** (10 minutes per sign)
   ```bash
   python ml/collect_data.py --label A --samples 300
   ```

2. **Train Model** (5 minutes)
   ```bash
   python ml/prepare_dataset.py
   python ml/train.py
   ```

3. **Test Recognition** (Live with your trained model)

4. **Deploy** (See DEPLOYMENT.md)

## Project Structure (TL;DR)

```
signspeak-ai/
├── frontend/          # React app
├── backend/           # FastAPI server
├── ml/                # ML pipeline
├── artifacts/         # Trained models
├── scripts/           # Helper scripts
└── docker-compose.yml # Run with Docker
```

## Testing

```bash
# Run all tests
./scripts/test_all.sh

# Or individual tests
cd backend && pytest tests/
cd ../frontend && npm test
```

## Troubleshooting

Get help:
1. Check [README.md](README.md) for detailed docs
2. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
3. Check [TESTING.md](TESTING.md) for test issues
4. Open a GitHub issue

## Commands Cheat Sheet

| Command | Purpose |
|---------|---------|
| `docker compose up` | Run full stack with Docker |
| `scripts/dev.sh` | Run frontend + backend locally |
| `pip install -e .` | Install backend in dev mode |
| `npm install` | Install frontend dependencies |
| `pytest tests/` | Run backend tests |
| `npm test` | Run frontend tests |
| `python ml/train.py` | Train ML model |
| `./scripts/smoke_test.sh` | Test deployment |

## Performance Tips

- Use **5-10 FPS** for real-time inference (not 30 FPS)
- **Ensure good lighting** for best accuracy
- **Keep hands fully visible** in frame
- **Test with diverse users** before production

---

**Quick Start Version:** 1.0  
**Last Updated:** 2024

**Questions?** See full documentation in README.md
