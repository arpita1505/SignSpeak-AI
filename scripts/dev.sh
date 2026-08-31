#!/bin/bash
# Development mode - run frontend and backend

set -e

echo "🚀 Starting SignSpeak AI in development mode..."

# Check if dependencies are installed
if [ ! -d "backend/.venv" ] && [ ! -d "backend/venv" ]; then
    echo "Installing backend dependencies..."
    cd backend
    python -m pip install --upgrade pip
    pip install -e ".[dev]"
    cd ..
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Initialize database
echo "Initializing database..."
cd backend
python -c "from app.db.database import init_db; init_db()"
cd ..

# Start backend in background
echo "Starting backend server..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend in background
echo "Starting frontend dev server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
