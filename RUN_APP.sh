#!/bin/bash

# Football Intelligence Application - Setup & Run Script

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Football Intelligence - Application Launcher            ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if in correct directory
if [ ! -d "football_analytics" ]; then
    echo "✗ Error: Run this script from /home/baris/statsbomb directory"
    echo "  Current directory: $(pwd)"
    exit 1
fi

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate


# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r football_analytics/app_backend/requirements.txt

if [ $? -ne 0 ]; then
    echo "✗ Error installing dependencies"
    exit 1
fi

echo "✓ Dependencies installed successfully"
echo ""
echo "Starting Football Intelligence Application..."
echo "═══════════════════════════════════════════════════════════"
echo ""

# Run the Flask app
cd football_analytics
python app_backend/app.py
