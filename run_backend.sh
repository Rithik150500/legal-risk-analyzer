#!/bin/bash
# Run the Legal Risk Analyzer backend server

# Change to script directory
cd "$(dirname "$0")"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check for virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install requirements if needed
if [ ! -f ".deps_installed" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    touch .deps_installed
fi

# Set default environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the backend server
echo "Starting backend server at http://localhost:8000"
echo "API documentation available at http://localhost:8000/docs"
echo ""
python backend/app.py
