#!/bin/bash

echo "📊 ORACLE CLOUD TRAINING MONITOR"
echo "VM.Standard.A1.Flex - 4 OCPUs, 24GB RAM (ARM Ampere)"
echo "Press Ctrl+C to stop monitoring"
echo ""

# Function to get system stats
get_system_stats() {
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEMORY_INFO=$(free -h | awk '/^Mem:/ {print $3 "/" $2 " (" int($3/$2*100) "%%)"}')
    DISK_INFO=$(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')
    LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}')
}

# Function to get training stats
get_training_stats() {
    TRAINING_STATS=$(curl -s http://localhost:8000/ai-signals/stats 2>/dev/null)
    if [ $? -eq 0 ]; then
        TRAINED_MODELS=$(echo $TRAINING_STATS | jq '.data.statistics.trained_models_count' 2>/dev/null || echo "0")
        UNIVERSE_SIZE=$(echo $TRAINING_STATS | jq '.data.statistics.stock_universe_size' 2>/dev/null || echo "0")
        GENERATION_STATS=$(echo $TRAINING_STATS | jq '.data.statistics.generation_stats' 2>/dev/null || echo "{}")
    else
        TRAINED_MODELS="API Error"
        UNIVERSE_SIZE="API Error"
        GENERATION_STATS="API Error"
    fi
}

# Function to get model count
get_model_count() {
    MODEL_COUNT=$(docker exec emergent-trader-api find /app/python_backend/models/price_prediction -name "*.joblib" 2>/dev/null | wc -l || echo "0")
}

# Main monitoring loop
while true; do
    clear
    echo "🏛️  ORACLE CLOUD AI TRAINING MONITOR"
    echo "Instance: VM.Standard.A1.Flex (ARM Ampere A1)"
    echo "Started: $(date)"
    echo "=" * 60
    
    # Get all stats
    get_system_stats
    get_training_stats
    get_model_count
    
    # Display system resources
    echo "💻 SYSTEM RESOURCES:"
    echo "   CPU Usage: ${CPU_USAGE}%"
    echo "   Memory: ${MEMORY_INFO}"
    echo "   Disk: ${DISK_INFO}"
    echo "   Load Average:${LOAD_AVG}"
    echo ""
    
    # Display training progress
    echo "🤖 TRAINING PROGRESS:"
    echo "   Trained Models: ${TRAINED_MODELS}"
    echo "   Universe Size: ${UNIVERSE_SIZE}"
    if [ "$TRAINED_MODELS" != "API Error" ] && [ "$UNIVERSE_SIZE" != "API Error" ] && [ "$UNIVERSE_SIZE" != "0" ]; then
        PROGRESS=$(echo "scale=1; $TRAINED_MODELS * 100 / $UNIVERSE_SIZE" | bc 2>/dev/null || echo "0")
        echo "   Progress: ${PROGRESS}%"
    fi
    echo "   Model Files: ${MODEL_COUNT}"
    echo ""
    
    # Display generation statistics
    echo "📊 GENERATION STATISTICS:"
    if [ "$GENERATION_STATS" != "API Error" ]; then
        echo "$GENERATION_STATS" | jq -r 'to_entries[] | "   \(.key): \(.value)"' 2>/dev/null || echo "   No stats available"
    else
        echo "   API not responding"
    fi
    echo ""
    
    # Display recent training logs
    echo "📋 RECENT TRAINING LOGS:"
    docker logs emergent-trader-api --tail 5 2>/dev/null | grep -i "training\|model\|batch" | tail -3 || echo "   No recent training logs"
    echo ""
    
    # Display estimated completion
    if [ "$TRAINED_MODELS" != "API Error" ] && [ "$TRAINED_MODELS" != "0" ]; then
        echo "⏱️  ESTIMATED COMPLETION:"
        CURRENT_TIME=$(date +%s)
        # Rough estimation based on progress
        if [ "$UNIVERSE_SIZE" != "0" ] && [ "$UNIVERSE_SIZE" != "API Error" ]; then
            REMAINING=$(echo "$UNIVERSE_SIZE - $TRAINED_MODELS" | bc 2>/dev/null || echo "Unknown")
            echo "   Remaining Models: ${REMAINING}"
            echo "   Estimated Time: 2-6 hours (depends on market data availability)"
        fi
    fi
    
    echo ""
    echo "🔄 Refreshing in 30 seconds... (Ctrl+C to stop)"
    sleep 30
done
