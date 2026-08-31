#!/bin/bash
# Smoke test for running application

set -e

API_URL="${API_URL:-http://localhost:8000}"
RETRIES=30
RETRY_DELAY=1

echo "Waiting for application to be ready..."

for i in $(seq 1 $RETRIES); do
    if curl -sf "$API_URL/api/health" > /dev/null; then
        echo "✅ Application is ready!"
        
        # Test health endpoint
        echo "Testing health endpoint..."
        HEALTH=$(curl -s "$API_URL/api/health")
        echo "$HEALTH" | grep -q "ok" && echo "✅ Health check passed" || exit 1
        
        # Test labels endpoint
        echo "Testing labels endpoint..."
        curl -sf "$API_URL/api/labels" > /dev/null && echo "✅ Labels endpoint works" || exit 1
        
        # Test model info endpoint
        echo "Testing model info endpoint..."
        curl -sf "$API_URL/api/model/info" > /dev/null && echo "✅ Model info endpoint works" || exit 1
        
        echo ""
        echo "🎉 All smoke tests passed!"
        exit 0
    fi
    
    echo "Attempt $i/$RETRIES - Application not ready yet..."
    sleep $RETRY_DELAY
done

echo "❌ Application failed to start"
exit 1
