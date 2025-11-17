#!/bin/bash

echo "🎮 Starting Weight Gain RPG! 🎮"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Create uploads directory
mkdir -p frontend/static/uploads

# Run the app
echo ""
echo "🚀 Launching app at http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

cd backend && python app.py
