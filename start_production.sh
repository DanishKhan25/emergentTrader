#!/bin/bash

# EmergentTrader Production Startup Script
# Starts both FastAPI backend and Next.js frontend

echo "🚀 Starting EmergentTrader Production System"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}Port $1 is already in use${NC}"
        return 1
    else
        return 0
    fi
}

# Function to start FastAPI backend
start_backend() {
    echo -e "${BLUE}Starting FastAPI Backend on port 8000...${NC}"
    
    cd python_backend
    
    # Install/update Python dependencies
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip3 install -r requirements.txt
    
    # Start FastAPI server
    if check_port 8000; then
        echo -e "${GREEN}Starting FastAPI server...${NC}"
        python3 main.py &
        BACKEND_PID=$!
        echo "Backend PID: $BACKEND_PID"
        
        # Wait for backend to start
        sleep 5
        
        # Check if backend is running
        if curl -s http://localhost:8000/health > /dev/null; then
            echo -e "${GREEN}✅ Backend started successfully${NC}"
        else
            echo -e "${RED}❌ Backend failed to start${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Cannot start backend - port 8000 in use${NC}"
        return 1
    fi
    
    cd ..
}

# Function to start Next.js frontend
start_frontend() {
    echo -e "${BLUE}Starting Next.js Frontend on port 3000...${NC}"
    
    # Install/update Node dependencies
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    npm install
    
    # Build Next.js app
    echo -e "${YELLOW}Building Next.js application...${NC}"
    npm run build
    
    # Start Next.js server
    if check_port 3000; then
        echo -e "${GREEN}Starting Next.js server...${NC}"
        npm start &
        FRONTEND_PID=$!
        echo "Frontend PID: $FRONTEND_PID"
        
        # Wait for frontend to start
        sleep 10
        
        # Check if frontend is running
        if curl -s http://localhost:3000 > /dev/null; then
            echo -e "${GREEN}✅ Frontend started successfully${NC}"
        else
            echo -e "${RED}❌ Frontend failed to start${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Cannot start frontend - port 3000 in use${NC}"
        return 1
    fi
}

# Function to show system status
show_status() {
    echo -e "${GREEN}"
    echo "🎉 EmergentTrader System Started Successfully!"
    echo "============================================="
    echo -e "${NC}"
    echo "📊 System URLs:"
    echo "   • Frontend Dashboard: http://localhost:3000"
    echo "   • Backend API: http://localhost:8000"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • API Redoc: http://localhost:8000/redoc"
    echo ""
    echo "🎯 Features Available:"
    echo "   • 10 Trading Strategies"
    echo "   • ML-Enhanced Signals (87% success rate)"
    echo "   • Shariah Compliance Filter"
    echo "   • Real-time Signal Generation"
    echo "   • Comprehensive Backtesting"
    echo "   • Performance Tracking"
    echo ""
    echo "🔧 Process IDs:"
    echo "   • Backend PID: $BACKEND_PID"
    echo "   • Frontend PID: $FRONTEND_PID"
    echo ""
    echo "⚠️  To stop the system:"
    echo "   kill $BACKEND_PID $FRONTEND_PID"
    echo "   or use Ctrl+C"
}

# Function to cleanup on exit
cleanup() {
    echo -e "${YELLOW}Shutting down EmergentTrader system...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "Frontend stopped"
    fi
    echo -e "${GREEN}System shutdown complete${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
echo -e "${BLUE}Checking system requirements...${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is required but not installed${NC}"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is required but not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ System requirements met${NC}"

# Start services
start_backend
if [ $? -eq 0 ]; then
    start_frontend
    if [ $? -eq 0 ]; then
        show_status
        
        # Keep script running
        echo -e "${YELLOW}Press Ctrl+C to stop the system${NC}"
        while true; do
            sleep 1
        done
    else
        echo -e "${RED}❌ Failed to start frontend${NC}"
        cleanup
        exit 1
    fi
else
    echo -e "${RED}❌ Failed to start backend${NC}"
    exit 1
fi
