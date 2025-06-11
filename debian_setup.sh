#!/bin/bash

# setup.sh - Fully automated setup for Audit Trail API

set -e  # Exit on any error

PYTHON=python3
VENV_DIR="venv"

# Step 1: Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
fi

# Step 2: Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Step 3: Upgrade pip and install requirements
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Install the local package
if [ -f "setup.py" ]; then
    echo "Installing local package..."
    pip install .
else
    echo "Warning: setup.py not found, skipping package install."
fi

# Step 5: Run tests using pytest (if present)
if [ -f "test/test_logger.py" ]; then
    echo "Running tests with pytest..."
    pip install pytest  # in case it's not in requirements.txt
    pytest test/test_logger.py
else
    echo "Warning: test/test_logger.py not found. Skipping tests."
fi

# Step 6: Start API server in background
if [ -f "app.py" ]; then
    echo "Starting API server..."
    echo "----------------------------------------"
    echo "  API Docs: http://localhost:5000/docs"
    echo "  Client Example: python client_app/client.py"
    echo "  Press Ctrl+C to stop"
    echo "----------------------------------------"
    python app.py &
    API_PID=$!

    # Graceful shutdown
    trap "echo 'Stopping server...'; kill $API_PID; deactivate" EXIT
    wait $API_PID
else
    echo "Warning: app.py not found. Server not started."
fi
