#!/bin/bash

echo "🔍 VERIFYING ORACLE CLOUD DEPLOYMENT"
echo "=" * 50

# Check system resources
echo "💻 System Resources:"
echo "   CPU Cores: $(nproc)"
echo "   Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo "   Disk Space: $(df -h / | awk 'NR==2 {print $4 " available"}')"
echo "   Architecture: $(uname -m)"
echo ""

# Check Docker
echo "🐳 Docker Status:"
if command -v docker &> /dev/null; then
    echo "   ✅ Docker installed: $(docker --version)"
    echo "   ✅ Docker running: $(systemctl is-active docker)"
else
    echo "   ❌ Docker not installed"
fi
echo ""

# Check Docker Compose
echo "📦 Docker Compose Status:"
if command -v docker-compose &> /dev/null; then
    echo "   ✅ Docker Compose installed: $(docker-compose --version)"
else
    echo "   ❌ Docker Compose not installed"
fi
echo ""

# Check services
echo "🚀 Service Status:"
if docker-compose -f docker-compose.oracle.yml ps | grep -q "Up"; then
    echo "   ✅ Services running:"
    docker-compose -f docker-compose.oracle.yml ps
else
    echo "   ❌ Services not running"
    echo "   Start with: docker-compose -f docker-compose.oracle.yml up -d"
fi
echo ""

# Check API health
echo "🏥 API Health Check:"
if curl -f http://localhost:8000/ai-signals/health > /dev/null 2>&1; then
    echo "   ✅ API is healthy"
    API_STATUS=$(curl -s http://localhost:8000/ai-signals/health | jq '.data.status' 2>/dev/null || echo "unknown")
    echo "   Status: $API_STATUS"
else
    echo "   ❌ API not responding"
fi
echo ""

# Check frontend
echo "🌐 Frontend Status:"
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend is accessible"
else
    echo "   ❌ Frontend not responding"
fi
echo ""

# Check trained models
echo "🤖 AI Models:"
MODEL_COUNT=$(find python_backend/models/price_prediction -name "*.joblib" 2>/dev/null | wc -l || echo "0")
echo "   Trained models: $MODEL_COUNT"
if [ "$MODEL_COUNT" -gt 0 ]; then
    echo "   ✅ Models available for prediction"
else
    echo "   ℹ️  No models trained yet. Run: ./train_oracle_cloud.sh"
fi
echo ""

# Check network access
echo "🌍 Network Access:"
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "unknown")
echo "   Public IP: $PUBLIC_IP"
if [ "$PUBLIC_IP" != "unknown" ]; then
    echo "   🌐 External access:"
    echo "      Frontend: http://$PUBLIC_IP:3000"
    echo "      API: http://$PUBLIC_IP:8000"
    echo "      Swagger: http://$PUBLIC_IP:8000/docs"
fi
echo ""

echo "✅ Deployment verification complete!"
