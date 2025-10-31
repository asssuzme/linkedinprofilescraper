#!/bin/bash

# LinkedIn Profile Scraper - Quick Setup Script

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║       LinkedIn Profile Scraper - Quick Setup          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "→ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  ✓ Python $python_version found"
echo ""

# Install dependencies
echo "→ Installing Python dependencies..."
pip install -r requirements.txt
echo "  ✓ Dependencies installed"
echo ""

# Install Playwright browsers
echo "→ Installing Playwright browsers..."
playwright install chromium
echo "  ✓ Playwright browsers installed"
echo ""

# Setup configuration
if [ ! -f .env ]; then
    echo "→ Creating .env configuration file..."
    cp env.example .env
    echo "  ✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your LinkedIn credentials!"
else
    echo "→ .env file already exists, skipping..."
fi
echo ""

# Create output directory
mkdir -p output
echo "  ✓ Output directory created"
echo ""

echo "╔════════════════════════════════════════════════════════╗"
echo "║                   Setup Complete!                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your LinkedIn credentials"
echo "2. Run: python main.py -i example_input.json"
echo ""
echo "For more information, see README.md"
