#!/bin/bash

echo "🚀 Starting EmergentTrader System"
echo "================================="

# Kill any existing processes on these ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

echo "📦 Installing dependencies..."
cd python_backend && pip3 install -r requirements.txt
cd ..
npm install

echo "🔧 Starting Backend (FastAPI)..."
cd python_backend
python3 main.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
cd ..

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🎨 Starting Frontend (Next.js)..."
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo "⏳ Waiting for frontend to start..."
sleep 10

echo ""
echo "🎉 System Started!"
echo "=================="
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Process IDs:"
echo "Backend: $BACKEND_PID"
echo "Frontend: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep script running
while true; do
    sleep 1
done
