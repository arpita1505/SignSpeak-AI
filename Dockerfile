# Multi-stage build for SignSpeak AI

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy frontend
COPY frontend/package*.json ./frontend/
COPY frontend/vite.config.ts ./frontend/
COPY frontend/tsconfig.json ./frontend/
COPY frontend/tsconfig.node.json ./frontend/
COPY frontend/vitest.config.ts ./frontend/
COPY frontend/eslint.config.js ./frontend/
COPY frontend/src ./frontend/src
COPY frontend/index.html ./frontend/

WORKDIR /app/frontend

# Install dependencies
RUN npm ci

# Build
RUN npm run build

# Stage 2: Build backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend/pyproject.toml .
COPY backend/app ./app

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy ML artifacts
COPY artifacts ./artifacts
COPY data ./data

# Copy frontend build from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
