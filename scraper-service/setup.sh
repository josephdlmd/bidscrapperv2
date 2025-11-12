#!/bin/bash

# Setup script for PhilGEPS Scraper Service
# Run this to set up the environment

set -e

echo "========================================"
echo "🚀 PhilGEPS Scraper Setup"
echo "========================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "   Please install Python 3.11 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium
echo "✅ Playwright browser installed"
echo ""

# Setup .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials!"
    echo ""
    echo "nano .env"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Create browser profile directory
echo "📁 Creating browser profile directory..."
mkdir -p browser_profile
echo "✅ Browser profile directory created"
echo ""

# Summary
echo "========================================"
echo "✅ SETUP COMPLETE!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Test the setup:"
echo "   python test_scraper.py"
echo ""
echo "3. Run manual login 3-5 times (first-time setup):"
echo "   Select option 1 in test menu"
echo ""
echo "4. After trust is established, start the service:"
echo "   python main.py"
echo ""
echo "========================================"
echo ""
