#!/bin/bash

echo "========================================"
echo "  ScamGuard - Online Scam Awareness"
echo "========================================"
echo ""
echo "Starting the application..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check if Flask is installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Flask is not installed. Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "  Application is starting..."
echo "  Open your browser and go to:"
echo "  http://localhost:5000"
echo "========================================"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python3 app.py
