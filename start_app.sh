#!/bin/bash

echo "🚀 Starting EmergentTrader Application..."
echo "========================================"

# Check if MongoDB is running
if ! brew services list | grep -q "mongodb-community.*started"; then
    echo "📦 Starting MongoDB..."
    brew services start mongodb/brew/mongodb-community
    sleep 3
else
    echo "✅ MongoDB is already running"
fi

# Check if Node.js dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Check if Python dependencies are installed
echo "🐍 Checking Python dependencies..."
if ! python3 -c "import yfinance" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip3 install --break-system-packages -r python_backend/requirements.txt
fi

echo ""
echo "🌟 EmergentTrader is starting..."
echo "📊 Frontend: http://localhost:3000"
echo "🔗 API Base: http://localhost:3000/api"
echo ""
echo "Available API endpoints:"
echo "  GET  /api/                    - API status"
echo "  GET  /api/stocks/all          - Get all NSE stocks"
echo "  POST /api/stocks/refresh      - Refresh stock data"
echo "  GET  /api/stocks/shariah      - Get Shariah-compliant stocks"
echo "  POST /api/signals/generate    - Generate trading signals"
echo "  POST /api/signals/track       - Track signal performance"
echo "  GET  /api/signals/today       - Get today's signals"
echo "  POST /api/backtest            - Run strategy backtest"
echo ""
echo "Press Ctrl+C to stop the application"
echo "========================================"

# Start the Next.js development server
npm run dev
