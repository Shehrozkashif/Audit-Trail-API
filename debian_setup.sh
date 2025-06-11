#!/bin/bash

# setup.sh - Automated setup for Audit Trail API
# Usage: ./setup.sh

# Exit on error and log all commands
set -e

# Check for required Python version (3.7+)
PYTHON_REQ="3.7"
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python $PYTHON_REQ or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$PYTHON_VERSION >= $PYTHON_REQ" | bc -l) -eq 0 ]]; then
    echo "Python $PYTHON_REQ+ required. Found $PYTHON_VERSION."
    exit 1
fi

# Create virtual environment
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Build and install package
echo "Building and installing audit_trail_lib..."
pip install .

# Verify installation
echo "Verifying installation..."
python -c "import audit_trail_lib; print('audit_trail_lib version:', audit_trail_lib.__version__)" || {
    echo "Package verification failed"
    exit 1
}

# Run tests
echo "Running tests..."
cd test
python -m unittest test_logger.py
cd ..

# Start API server
echo "Starting API server..."
echo "----------------------------------------"
echo "  API Documentation: http://localhost:5000/docs"
echo "  Try the client: python client_app/client.py"
echo "  Press Ctrl+C to stop the server"
echo "----------------------------------------"

# Run API in background and capture PID
python app.py &
API_PID=$!

# Setup cleanup
trap "echo 'Stopping server...'; kill $API_PID; deactivate" EXIT

# Keep script running while server is active
wait $API_PID