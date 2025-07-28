#!/bin/bash

# Simple Authentication Setup Script for EmergentTrader
echo "🔐 Setting up EmergentTrader Authentication..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

# Test authentication service
echo "🧪 Testing authentication service..."

python3 -c "
import sys
sys.path.append('python_backend')

try:
    # Try to import JWT-based auth service first
    try:
        from services.auth_service import auth_service
        auth_service_instance = auth_service
        print('✅ JWT-based authentication available')
    except ImportError:
        # Fallback to simple auth service if JWT not available
        from services.fallback_auth_service import fallback_auth_service
        auth_service_instance = fallback_auth_service
        print('✅ Using fallback authentication (JWT not available)')
    
    # Test login
    result = auth_service_instance.authenticate('admin', 'admin123')
    if result['success']:
        print('✅ Authentication test passed')
        
        # Test token verification
        token = result['token']
        verify_result = auth_service_instance.verify_token(token)
        if verify_result['success']:
            print('✅ Token verification test passed')
        else:
            print('❌ Token verification failed')
            exit(1)
    else:
        print('❌ Authentication test failed')
        exit(1)
        
except Exception as e:
    print(f'❌ Authentication setup failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Authentication service is working correctly!"
else
    print_error "Authentication setup failed"
    exit 1
fi

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOL
# EmergentTrader Environment Variables

# Authentication
JWT_SECRET=emergent_trader_secret_key_2024_$(date +%s)

# Telegram Bot Configuration (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Database
DATABASE_URL=sqlite:///python_backend/emergent_trader.db
EOL
    print_success ".env file created"
else
    print_warning ".env file already exists"
fi

echo ""
echo "🎉 Authentication setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Start the application: npm run dev"
echo "2. Open http://localhost:3000/login"
echo "3. Login with:"
echo "   • Admin: admin / admin123"
echo "   • Trader: trader / trader123"
echo ""
echo "✅ Authentication is ready to use!"
