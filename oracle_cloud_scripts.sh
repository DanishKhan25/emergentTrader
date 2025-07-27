#!/bin/bash

# Oracle Cloud Scripts for EmergentTrader AI Training
# Optimized for VM.Standard.A1.Flex (4 OCPUs, 24GB RAM)

# Create training script
cat > train_oracle_cloud.sh << 'EOF'
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
EOF

# Create monitoring script
cat > monitor_oracle_training.sh << 'EOF'
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
EOF

# Create system optimization script
cat > optimize_oracle_system.sh << 'EOF'
#!/bin/bash

echo "🔧 OPTIMIZING ORACLE CLOUD SYSTEM FOR AI TRAINING"
echo "Optimizing for ARM Ampere A1 processors..."

# System optimizations
echo "⚙️  Applying system optimizations..."
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.dirty_ratio=15' | sudo tee -a /etc/sysctl.conf
echo 'vm.dirty_background_ratio=5' | sudo tee -a /etc/sysctl.conf
echo 'net.core.rmem_max=134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max=134217728' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Docker optimizations
echo "🐳 Optimizing Docker for ARM..."
sudo mkdir -p /etc/docker
cat > /tmp/daemon.json << 'DOCKER_EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
DOCKER_EOF
sudo mv /tmp/daemon.json /etc/docker/daemon.json
sudo systemctl restart docker

# Create swap file for additional memory
echo "💾 Creating swap file for additional memory..."
if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Optimize for machine learning workloads
echo "🤖 Optimizing for ML workloads..."
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4
echo 'export OMP_NUM_THREADS=4' >> ~/.bashrc
echo 'export MKL_NUM_THREADS=4' >> ~/.bashrc
echo 'export OPENBLAS_NUM_THREADS=4' >> ~/.bashrc

echo "✅ System optimization complete!"
echo ""
echo "📊 System Information:"
echo "   CPU Cores: $(nproc)"
echo "   Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo "   Swap: $(free -h | awk '/^Swap:/ {print $2}')"
echo "   Disk: $(df -h / | awk 'NR==2 {print $2}')"
EOF

# Create backup script for Oracle Object Storage
cat > backup_to_oracle_storage.sh << 'EOF'
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="oracle_models_backup_$DATE.tar.gz"

echo "💾 CREATING ORACLE CLOUD BACKUP"
echo "Backup file: $BACKUP_FILE"

# Create compressed backup
echo "📦 Creating compressed backup..."
tar -czf $BACKUP_FILE \
    python_backend/models/ \
    python_backend/logs/ \
    --exclude="*.pyc" \
    --exclude="__pycache__"

BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
echo "✅ Backup created: $BACKUP_FILE ($BACKUP_SIZE)"

# Optional: Upload to Oracle Object Storage (requires OCI CLI setup)
if command -v oci &> /dev/null; then
    echo "☁️  Uploading to Oracle Object Storage..."
    
    # Create bucket if it doesn't exist
    oci os bucket create --name emergent-trader-backups --compartment-id YOUR_COMPARTMENT_ID 2>/dev/null || true
    
    # Upload backup
    oci os object put \
        --bucket-name emergent-trader-backups \
        --file $BACKUP_FILE \
        --name "backups/$BACKUP_FILE" \
        --force
    
    echo "✅ Backup uploaded to Object Storage"
    
    # Clean up local backup file
    rm $BACKUP_FILE
    echo "🧹 Local backup file cleaned up"
else
    echo "ℹ️  OCI CLI not configured. Backup saved locally: $BACKUP_FILE"
    echo "📋 To upload to Object Storage:"
    echo "   1. Install OCI CLI: bash -c \"\$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)\""
    echo "   2. Configure: oci setup config"
    echo "   3. Run this script again"
fi

echo ""
echo "📊 Backup Summary:"
echo "   File: $BACKUP_FILE"
echo "   Size: $BACKUP_SIZE"
echo "   Date: $(date)"
EOF

# Create deployment verification script
cat > verify_oracle_deployment.sh << 'EOF'
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
EOF

# Make all scripts executable
chmod +x train_oracle_cloud.sh
chmod +x monitor_oracle_training.sh
chmod +x optimize_oracle_system.sh
chmod +x backup_to_oracle_storage.sh
chmod +x verify_oracle_deployment.sh

echo "✅ Oracle Cloud scripts created successfully!"
echo ""
echo "📋 Available scripts:"
echo "   ./train_oracle_cloud.sh - Start AI training"
echo "   ./monitor_oracle_training.sh - Monitor training progress"
echo "   ./optimize_oracle_system.sh - Optimize system for training"
echo "   ./backup_to_oracle_storage.sh - Backup models to Object Storage"
echo "   ./verify_oracle_deployment.sh - Verify deployment status"
