#!/bin/bash
# Run both backend and frontend servers for development

# Change to script directory
cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Legal Risk Analyzer - Development Environment${NC}"
echo "============================================="
echo ""

# Check dependencies
echo "Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is required but not installed.${NC}"
    exit 1
fi

echo -e "${GREEN}Dependencies OK${NC}"
echo ""

# Start backend
echo -e "${YELLOW}Starting backend server...${NC}"
./run_backend.sh &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${YELLOW}Starting frontend server...${NC}"
./run_frontend.sh &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}Both servers are now running:${NC}"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
