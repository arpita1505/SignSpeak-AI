#!/bin/bash
# Run all tests: backend, frontend, and integration

set -e

echo "================================"
echo "Running Backend Tests"
echo "================================"
cd backend
pip install -e ".[dev]" > /dev/null 2>&1 || true
python -m pytest tests/ -v --tb=short
cd ..

echo ""
echo "================================"
echo "Running Frontend Tests"
echo "================================"
cd frontend
npm ci > /dev/null 2>&1 || true
npm run test -- --run
cd ..

echo ""
echo "================================"
echo "Checking Frontend Type Safety"
echo "================================"
cd frontend
npm run type-check
cd ..

echo ""
echo "================================"
echo "Building Frontend"
echo "================================"
cd frontend
npm run build
cd ..

echo ""
echo "✅ All tests passed!"
