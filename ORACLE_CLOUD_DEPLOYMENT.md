# ☁️ Oracle Cloud Free Tier Deployment Guide

## 🎯 **Why Oracle Cloud Free Tier is Perfect**

Oracle Cloud offers the **most generous free tier** in the industry:

### **Always Free Resources:**
- ✅ **2 AMD Compute VMs**: 1/8 OCPU each, 1 GB RAM each
- ✅ **4 Arm-based Ampere A1 Compute VMs**: Up to 4 OCPUs, 24 GB RAM total
- ✅ **200 GB Block Storage**: High-performance storage
- ✅ **10 GB Object Storage**: For backups and static files
- ✅ **Always Free**: No time limits, permanent free resources

### **Perfect for AI Training:**
```
Recommended Configuration:
- 1x Ampere A1 VM: 4 OCPUs, 24 GB RAM
- 200 GB Boot Volume
- Cost: $0/month (Always Free)
- Training Time: 4-8 hours for 2000 stocks
```

## 🚀 **Step-by-Step Deployment**

### **Step 1: Create Oracle Cloud Account**

1. Go to [cloud.oracle.com](https://cloud.oracle.com)
2. Click "Start for free"
3. Fill in details (requires credit card for verification, but won't be charged)
4. Verify email and phone
5. Complete account setup

### **Step 2: Create Compute Instance**

#### **Launch Ampere A1 Instance (Recommended)**
```bash
# Instance Configuration:
Name: emergent-trader-ai
Image: Ubuntu 22.04 Minimal
Shape: VM.Standard.A1.Flex
OCPUs: 4 (maximum free tier)
Memory: 24 GB (maximum free tier)
Boot Volume: 200 GB
Network: Create new VCN with internet gateway
```

#### **Detailed Steps:**
1. **Login to OCI Console** → Compute → Instances
2. **Create Instance**:
   - Name: `emergent-trader-ai`
   - Placement: Choose any availability domain
   - Image: `Canonical Ubuntu 22.04 Minimal`
   - Shape: `VM.Standard.A1.Flex` (Ampere ARM processor)
   - OCPUs: `4` (use maximum free allocation)
   - Memory: `24 GB` (use maximum free allocation)
3. **Networking**:
   - Create new Virtual Cloud Network (VCN)
   - Create new subnet
   - Assign public IP address
4. **SSH Keys**:
   - Generate new key pair OR upload existing public key
   - Download private key (keep safe!)
5. **Boot Volume**: `200 GB` (maximum free tier)
6. **Click "Create"**

### **Step 3: Configure Security Rules**

#### **Add Ingress Rules:**
```bash
# In VCN → Security Lists → Default Security List
# Add these ingress rules:

1. HTTP Traffic:
   - Source: 0.0.0.0/0
   - Protocol: TCP
   - Port: 80

2. HTTPS Traffic:
   - Source: 0.0.0.0/0
   - Protocol: TCP
   - Port: 443

3. API Traffic:
   - Source: 0.0.0.0/0
   - Protocol: TCP
   - Port: 8000

4. Frontend Traffic:
   - Source: 0.0.0.0/0
   - Protocol: TCP
   - Port: 3000
```

### **Step 4: Connect and Setup**

#### **Connect to Instance:**
```bash
# Get public IP from OCI console
# Connect via SSH
ssh -i /path/to/private-key ubuntu@YOUR_PUBLIC_IP

# Update system
sudo apt update && sudo apt upgrade -y
```

#### **Install Dependencies:**
```bash
# Install Docker (recommended approach)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional tools
sudo apt install -y git htop curl jq unzip

# Logout and login again for docker group
exit
ssh -i /path/to/private-key ubuntu@YOUR_PUBLIC_IP
```

### **Step 5: Deploy Application**

#### **Clone Repository:**
```bash
# Clone your repository
git clone https://github.com/your-username/emergent-trader.git
cd emergent-trader

# Or upload files if no git repository
# scp -i /path/to/private-key -r ./emergent-trader ubuntu@YOUR_PUBLIC_IP:~/
```

#### **Create Oracle Cloud Optimized Docker Compose:**
```yaml
# docker-compose.oracle.yml
version: '3.8'

services:
  emergent-trader-api:
    build: .
    container_name: emergent-trader-api
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/python_backend/models
      - ./logs:/app/python_backend/logs
      - ./data:/app/python_backend/data
    environment:
      - PYTHONPATH=/app/python_backend
      - PYTHONUNBUFFERED=1
      - MAX_CONCURRENT_TRAINING=4  # Optimized for 4 OCPUs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 20G  # Leave 4GB for system
        reservations:
          memory: 16G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/ai-signals/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Frontend (Next.js)
  emergent-trader-frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: emergent-trader-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://YOUR_PUBLIC_IP:8000
    restart: unless-stopped
    depends_on:
      - emergent-trader-api

volumes:
  models_data:
  logs_data:
  data_volume:
```

#### **Create Frontend Dockerfile:**
```dockerfile
# Dockerfile.frontend
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN yarn build

# Expose port
EXPOSE 3000

# Start the application
CMD ["yarn", "start"]
```

### **Step 6: Build and Deploy**

#### **Build and Start Services:**
```bash
# Create necessary directories
mkdir -p models logs data

# Build and start services
docker-compose -f docker-compose.oracle.yml up -d --build

# Check status
docker-compose -f docker-compose.oracle.yml ps

# View logs
docker-compose -f docker-compose.oracle.yml logs -f
```

#### **Verify Deployment:**
```bash
# Test API
curl http://localhost:8000/ai-signals/health

# Test from external
curl http://YOUR_PUBLIC_IP:8000/ai-signals/health

# Test frontend
curl http://YOUR_PUBLIC_IP:3000
```

### **Step 7: Configure Firewall (Ubuntu)**

```bash
# Configure Ubuntu firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000
sudo ufw allow 3000
sudo ufw --force enable

# Check status
sudo ufw status
```

## 🤖 **AI Training on Oracle Cloud**

### **Optimized Training Configuration:**

#### **Create Training Script:**
```bash
# train_oracle_cloud.sh
#!/bin/bash

echo "🤖 ORACLE CLOUD AI TRAINING - 2000+ STOCKS"
echo "Instance: 4 OCPUs, 24GB RAM (Ampere A1)"
echo "Estimated Time: 4-8 hours"
echo ""

# Health check
curl -f http://localhost:8000/ai-signals/health || {
    echo "❌ API not healthy"
    exit 1
}

# Start optimized training for Oracle Cloud
curl -X POST http://localhost:8000/ai-signals/train/batch \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": null,
    "shariah_only": true,
    "max_concurrent": 4
  }' | jq '.'

echo ""
echo "✅ Training started on Oracle Cloud!"
echo "📊 Monitor: ./monitor_oracle_training.sh"
```

#### **Create Monitoring Script:**
```bash
# monitor_oracle_training.sh
#!/bin/bash

echo "📊 ORACLE CLOUD TRAINING MONITOR"
echo "4 OCPUs, 24GB RAM - Ampere A1"
echo ""

while true; do
    clear
    echo "🤖 AI Training Progress - $(date)"
    echo "Oracle Cloud Free Tier - Ampere A1"
    echo "=" * 50
    
    # System resources
    echo "💻 System Resources:"
    echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
    echo ""
    
    # Training stats
    echo "📈 Training Statistics:"
    curl -s http://localhost:8000/ai-signals/stats | jq '.data.statistics' 2>/dev/null || echo "API not responding"
    
    echo ""
    echo "💾 Models Created:"
    docker exec emergent-trader-api find /app/python_backend/models/price_prediction -name "*.joblib" | wc -l
    
    echo ""
    echo "📋 Recent Logs:"
    docker logs emergent-trader-api --tail 5 | grep -i training || echo "No recent training logs"
    
    sleep 30
done
```

### **Performance Optimization for ARM:**

#### **ARM-Optimized Requirements:**
```txt
# requirements.oracle.txt - ARM optimized
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
yfinance==0.2.18
fastapi==0.103.0
uvicorn==0.23.2
joblib==1.3.2

# ARM-optimized ML libraries
scipy==1.11.1
matplotlib==3.7.2
seaborn==0.12.2
```

#### **Update Dockerfile for ARM:**
```dockerfile
# Dockerfile - ARM optimized
FROM python:3.11-slim

# ARM-specific optimizations
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OMP_NUM_THREADS=4

WORKDIR /app

# Install ARM-optimized system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY python_backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY python_backend/ ./python_backend/
COPY components/ ./components/

# Create directories
RUN mkdir -p python_backend/models/price_prediction python_backend/logs

# Set environment
ENV PYTHONPATH=/app/python_backend

EXPOSE 8000

CMD ["python", "python_backend/main.py"]
```

## 🔧 **Advanced Oracle Cloud Setup**

### **Load Balancer (Optional):**
```bash
# If you need high availability
# Create Load Balancer in OCI Console
# Backend Set: Your compute instance on port 8000
# Health Check: /ai-signals/health
```

### **Object Storage for Backups:**
```bash
# Install OCI CLI
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Configure OCI CLI
oci setup config

# Create backup script with Object Storage
cat > backup_to_object_storage.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="models_backup_$DATE.tar.gz"

# Create backup
tar -czf $BACKUP_FILE python_backend/models/

# Upload to Object Storage
oci os object put \
  --bucket-name your-bucket-name \
  --file $BACKUP_FILE \
  --name backups/$BACKUP_FILE

echo "✅ Backup uploaded to Object Storage: $BACKUP_FILE"
rm $BACKUP_FILE
EOF
```

### **Auto-scaling (Advanced):**
```bash
# Create instance configuration and instance pool
# for auto-scaling based on CPU usage
# This is advanced and may require paid resources
```

## 📊 **Monitoring and Maintenance**

### **System Monitoring:**
```bash
# Create monitoring dashboard
cat > oracle_monitor.sh << 'EOF'
#!/bin/bash
while true; do
    clear
    echo "🏛️  ORACLE CLOUD MONITORING DASHBOARD"
    echo "Instance: VM.Standard.A1.Flex (4 OCPUs, 24GB)"
    echo "=" * 50
    
    # System info
    echo "💻 System Information:"
    echo "Uptime: $(uptime -p)"
    echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
    echo "CPU: $(nproc) cores"
    echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "Disk: $(df -h / | awk 'NR==2 {print $5 " used"}')"
    echo ""
    
    # Docker status
    echo "🐳 Docker Services:"
    docker-compose -f docker-compose.oracle.yml ps
    echo ""
    
    # API health
    echo "🏥 API Health:"
    curl -s http://localhost:8000/ai-signals/health | jq '.data.status' || echo "API Down"
    echo ""
    
    # Training progress
    echo "🤖 AI Training:"
    curl -s http://localhost:8000/ai-signals/stats | jq '.data.statistics.trained_models_count' || echo "0"
    echo " models trained"
    
    sleep 60
done
EOF

chmod +x oracle_monitor.sh
```

### **Automated Backups:**
```bash
# Create cron job for daily backups
crontab -e

# Add this line for daily backup at 2 AM
0 2 * * * /home/ubuntu/emergent-trader/backup_to_object_storage.sh
```

## 💰 **Cost Analysis (Always Free)**

### **Oracle Cloud Free Tier Usage:**
```
✅ Compute: VM.Standard.A1.Flex (4 OCPUs, 24GB) - $0/month
✅ Storage: 200 GB Boot Volume - $0/month  
✅ Network: 10 TB outbound transfer - $0/month
✅ Object Storage: 10 GB - $0/month
✅ Load Balancer: 1 instance - $0/month

Total Monthly Cost: $0 (Always Free)
Training Cost: $0 (no time limits)
```

### **Performance Comparison:**
```
Oracle Cloud (Free):     4 OCPUs, 24GB RAM - 4-8 hours training
AWS c5.2xlarge (Paid):   8 vCPUs, 16GB RAM - 6-10 hours training ($5-10)
GCP c2-standard-8 (Paid): 8 vCPUs, 32GB RAM - 4-6 hours training ($4-8)

Winner: Oracle Cloud (Free + Excellent Performance)
```

## 🚀 **Quick Start Commands**

### **Complete Deployment:**
```bash
# 1. Create Oracle Cloud account and Ampere A1 instance
# 2. SSH into instance
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP

# 3. Quick setup
curl -fsSL https://raw.githubusercontent.com/your-repo/emergent-trader/main/cloud_setup.sh | bash

# 4. Deploy with Docker
docker-compose -f docker-compose.oracle.yml up -d --build

# 5. Start AI training
./train_oracle_cloud.sh

# 6. Monitor progress
./monitor_oracle_training.sh
```

### **Access Your Application:**
```
Frontend: http://YOUR_PUBLIC_IP:3000
API: http://YOUR_PUBLIC_IP:8000
Swagger: http://YOUR_PUBLIC_IP:8000/docs
Health: http://YOUR_PUBLIC_IP:8000/ai-signals/health
```

## 🎯 **Expected Results**

After Oracle Cloud deployment:
- ✅ **Complete app deployed** on free tier
- ✅ **2000 AI models trained** in 4-8 hours
- ✅ **$0 monthly cost** (Always Free)
- ✅ **24/7 availability** with excellent performance
- ✅ **Professional deployment** with monitoring
- ✅ **Scalable architecture** ready for production

## 🔧 **Troubleshooting**

### **Common Issues:**
```bash
# Issue: Out of memory during training
# Solution: Reduce max_concurrent to 2-3
curl -X POST http://localhost:8000/ai-signals/train/batch \
  -d '{"max_concurrent": 2}'

# Issue: Docker build fails on ARM
# Solution: Use ARM-specific base images
FROM python:3.11-slim  # Works on ARM

# Issue: Slow training
# Solution: Optimize for ARM architecture
export OMP_NUM_THREADS=4
```

### **Performance Tuning:**
```bash
# Optimize for ARM Ampere processors
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'net.core.rmem_max=134217728' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Docker optimization
docker system prune -f
docker volume prune -f
```

## 🎉 **Conclusion**

Oracle Cloud's Always Free tier provides the **best value** for deploying and training your AI models:

- **4 OCPUs + 24GB RAM** - More powerful than most paid alternatives
- **Always Free** - No time limits or hidden costs
- **200GB Storage** - Plenty of space for models and data
- **Excellent Performance** - ARM Ampere processors are fast
- **Professional Infrastructure** - Enterprise-grade cloud platform

**Ready to deploy your entire EmergentTrader app on Oracle Cloud for free!** 🚀
