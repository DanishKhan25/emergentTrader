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
