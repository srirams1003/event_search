#!/bin/bash

# SF Tech Events Aggregator - Quick Start Script

echo "🚀 SF Tech Events Aggregator"
echo "=============================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/lib/python*/site-packages/flask" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  WARNING: .env file not found!"
    echo "Please copy env.example to .env and add your API keys:"
    echo "    cp env.example .env"
    echo "    nano .env"
    echo ""
    echo "See README.md for instructions on obtaining API keys."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run the application
echo ""
echo "🎉 Starting application..."
echo "📍 Open http://localhost:5000 in your browser"
echo ""
python app.py

