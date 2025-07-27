#!/bin/bash

echo "🏛️  ORACLE CLOUD AI TRAINING - 2000+ STOCKS"
echo "Instance: VM.Standard.A1.Flex (4 OCPUs, 24GB RAM)"
echo "Estimated Time: 4-8 hours"
echo "Cost: $0 (Always Free Tier)"
echo ""

# Check if API is running
echo "🏥 Checking API health..."
if ! curl -f http://localhost:8000/ai-signals/health > /dev/null 2>&1; then
    echo "❌ API not healthy. Starting services..."
    docker-compose -f docker-compose.oracle.yml up -d
    echo "⏳ Waiting for services to start..."
    sleep 30
fi

# Verify API is ready
curl -f http://localhost:8000/ai-signals/health || {
    echo "❌ API still not healthy. Check logs:"
    echo "docker-compose -f docker-compose.oracle.yml logs"
    exit 1
}

echo "✅ API is healthy"

# Get current universe size
echo "📊 Checking stock universe..."
UNIVERSE_SIZE=$(curl -s http://localhost:8000/ai-signals/universe | jq '.data.universe_info.total_stocks' 2>/dev/null || echo "0")
echo "Stock universe size: $UNIVERSE_SIZE"

# Start optimized training for Oracle Cloud ARM processors
echo "🚀 Starting AI training optimized for ARM Ampere processors..."
curl -X POST http://localhost:8000/ai-signals/train/batch \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": null,
    "shariah_only": true,
    "max_concurrent": 4
  }' | jq '.' || {
    echo "❌ Failed to start training"
    exit 1
}

echo ""
echo "✅ Training started on Oracle Cloud!"
echo ""
echo "📊 Monitor progress with:"
echo "   ./monitor_oracle_training.sh"
echo ""
echo "📋 View logs:"
echo "   docker logs emergent-trader-api -f"
echo ""
echo "📈 Check statistics:"
echo "   curl http://localhost:8000/ai-signals/stats | jq"
echo ""
echo "💾 Expected results:"
echo "   - 1800-2000 models trained"
echo "   - 4-8 hours completion time"
echo "   - 10-15 GB storage used"
echo "   - $0 cost (Always Free)"
