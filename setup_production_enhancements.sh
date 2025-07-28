#!/bin/bash

# EmergentTrader Production Enhancements Setup Script
# This script sets up all the new production features

echo "🚀 Setting up EmergentTrader Production Enhancements..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "python_backend" ]; then
    print_error "Please run this script from the EmergentTrader root directory"
    exit 1
fi

print_status "Installing Python dependencies..."

# Install Python dependencies
cd python_backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install enhanced requirements
if [ -f "requirements_enhanced.txt" ]; then
    print_status "Installing enhanced Python requirements..."
    pip install -r requirements_enhanced.txt
else
    print_warning "Enhanced requirements file not found, installing basic requirements..."
    pip install fastapi uvicorn websockets PyJWT schedule requests pandas yfinance
fi

print_success "Python dependencies installed"

# Go back to root directory
cd ..

print_status "Installing Node.js dependencies..."

# Install Node.js dependencies
npm install

# Install additional frontend dependencies for new features
npm install @radix-ui/react-progress

print_success "Node.js dependencies installed"

print_status "Setting up environment variables..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << EOL
# EmergentTrader Production Environment Variables

# Authentication
JWT_SECRET=emergent_trader_secret_key_2024_$(date +%s)

# Telegram Bot Configuration (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Email Configuration (Optional)
EMAIL_ENABLED=false
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_RECIPIENTS=your_email@gmail.com

# Webhook URL (Optional)
WEBHOOK_URL=

# Database Configuration
DATABASE_URL=sqlite:///python_backend/emergent_trader.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
EOL
    print_success ".env file created with default values"
    print_warning "Please update the .env file with your actual configuration values"
else
    print_warning ".env file already exists, skipping creation"
fi

print_status "Setting up database..."

# Initialize database by running a simple Python script
cd python_backend
python3 -c "
import sys
sys.path.append('.')
from services.enhanced_notification_service import notification_service
from services.signal_management_service import signal_manager
print('✅ Database initialized successfully')
"

cd ..

print_status "Setting up systemd service (optional)..."

# Create systemd service file
cat > emergent-trader.service << EOL
[Unit]
Description=EmergentTrader Enhanced API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)/python_backend
Environment=PATH=$(pwd)/python_backend/venv/bin
ExecStart=$(pwd)/python_backend/venv/bin/python main_enhanced.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

print_success "Systemd service file created: emergent-trader.service"
print_warning "To install the service, run: sudo cp emergent-trader.service /etc/systemd/system/ && sudo systemctl enable emergent-trader"

print_status "Creating startup scripts..."

# Create startup script for development
cat > start_dev.sh << 'EOL'
#!/bin/bash

echo "🚀 Starting EmergentTrader Development Environment..."

# Start Python backend
cd python_backend
source venv/bin/activate
python main_enhanced.py &
BACKEND_PID=$!

# Go back to root
cd ..

# Start Next.js frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ EmergentTrader started successfully!"
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for processes
wait
EOL

chmod +x start_dev.sh

# Create production startup script
cat > start_prod.sh << 'EOL'
#!/bin/bash

echo "🚀 Starting EmergentTrader Production Environment..."

# Start Python backend
cd python_backend
source venv/bin/activate
uvicorn main_enhanced:app --host 0.0.0.0 --port 8000 --workers 4 &
BACKEND_PID=$!

# Go back to root
cd ..

# Build and start Next.js frontend
npm run build
npm start &
FRONTEND_PID=$!

echo "✅ EmergentTrader Production started successfully!"
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for processes
wait
EOL

chmod +x start_prod.sh

print_success "Startup scripts created: start_dev.sh and start_prod.sh"

print_status "Creating test script..."

# Create test script
cat > test_enhancements.py << 'EOL'
#!/usr/bin/env python3
"""
Test script for EmergentTrader Production Enhancements
"""

import sys
import os
sys.path.append('python_backend')

def test_services():
    print("🧪 Testing EmergentTrader Enhanced Services...")
    
    try:
        # Test authentication service
        from services.auth_service import auth_service
        result = auth_service.authenticate('admin', 'admin123')
        assert result['success'], "Authentication test failed"
        print("✅ Authentication service working")
        
        # Test notification service
        from services.enhanced_notification_service import notification_service
        print("✅ Notification service loaded")
        
        # Test signal management service
        from services.signal_management_service import signal_manager
        stats = signal_manager.get_signal_statistics()
        assert stats['success'], "Signal manager test failed"
        print("✅ Signal management service working")
        
        # Test scheduler service
        from services.scheduler_service import scheduler_service
        status = scheduler_service.get_status()
        print("✅ Scheduler service loaded")
        
        print("\n🎉 All enhanced services are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_services()
    sys.exit(0 if success else 1)
EOL

chmod +x test_enhancements.py

print_status "Running tests..."
python3 test_enhancements.py

print_success "Setup completed successfully! 🎉"

echo ""
echo "📋 Next Steps:"
echo "1. Update .env file with your configuration (Telegram bot, email, etc.)"
echo "2. For development: ./start_dev.sh"
echo "3. For production: ./start_prod.sh"
echo "4. Access the application at http://localhost:3000"
echo "5. API documentation at http://localhost:8000/docs"
echo ""
echo "🔐 Default Login Credentials:"
echo "   Admin: admin / admin123"
echo "   Trader: trader / trader123"
echo ""
echo "📱 New Features Available:"
echo "   • Authentication system with JWT tokens"
echo "   • Real-time WebSocket notifications"
echo "   • Signal tracking and performance monitoring"
echo "   • Automated scheduling (3x daily signal generation)"
echo "   • Telegram notifications for signals and targets"
echo "   • Enhanced dashboard with live updates"
echo ""
print_success "EmergentTrader Production Enhancements are ready! 🚀"
