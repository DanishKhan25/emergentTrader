#!/bin/bash

# Test script to verify Python backend is running and accessible
echo "🔗 Testing Python Backend Connection..."
echo "Backend URL: http://localhost:8000"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test health endpoint
echo "📡 Testing Health Endpoint..."
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health endpoint responding${NC}"
    curl -s http://localhost:8000/health | head -3
else
    echo -e "${RED}❌ Health endpoint not responding${NC}"
    echo -e "${YELLOW}💡 Start the backend with: cd python_backend && python main_enhanced.py${NC}"
fi

echo ""

# Test signals endpoints (these will return 401 without auth, which is expected)
echo "📊 Testing Signals Endpoints..."

endpoints=("/signals" "/signals/active" "/signals/statistics")

for endpoint in "${endpoints[@]}"; do
    echo "Testing $endpoint..."
    
    response=$(curl -s -w "%{http_code}" http://localhost:8000$endpoint)
    http_code="${response: -3}"
    
    if [ "$http_code" = "401" ]; then
        echo -e "${GREEN}✅ $endpoint responding (401 - auth required, expected)${NC}"
    elif [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ $endpoint responding (200 - success)${NC}"
    elif [ "$http_code" = "000" ]; then
        echo -e "${RED}❌ $endpoint not reachable (connection refused)${NC}"
    else
        echo -e "${YELLOW}⚠️  $endpoint returned HTTP $http_code${NC}"
    fi
done

echo ""
echo "📋 Summary:"
echo "✅ Status 200 or 401 = Backend is running correctly"
echo "❌ Connection refused = Backend is not running"
echo "🚀 If backend is not running, start it with:"
echo "   cd python_backend && python main_enhanced.py"
