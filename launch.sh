#!/bin/bash
# Launch script for Meme Video Generator

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Set Python path to include our project
export PYTHONPATH="$DIR:$DIR/src:$PYTHONPATH"

# Check if virtual environment exists
if [ ! -d "Project-Env" ]; then
    echo "Creating virtual environment..."
    python3.12 -m venv Project-Env
fi

# Use virtual environment Python
PYTHON="$DIR/Project-Env/bin/python"
PIP="$DIR/Project-Env/bin/pip"

# Check tkinter (system requirement)
if ! python3.12 -c "import tkinter" 2>/dev/null; then
    echo "❌ tkinter not found. Please install it:"
    echo "  macOS: brew install python-tk@3.12"
    echo "  Ubuntu: sudo apt install python3-tk"
    exit 1
fi

# Install dependencies in virtual environment
if ! $PYTHON -c "import yaml" 2>/dev/null; then
    echo "Installing dependencies..."
    $PIP install -r requirements.txt
fi

# Launch the app
echo "Launching Meme Video Generator..."
$PYTHON run_app.py
