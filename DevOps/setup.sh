#!/bin/bash

# Setup script for Amazon Bedrock Agent Core File Search App
# This script initializes the development environment

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  Amazon Bedrock Agent Core File Search App - Setup"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed. Please install Python 3.9+ and try again."
    exit 1
fi
echo "✓ Python $(python3 --version) found"

# Setup .env file
echo ""
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✓ Created .env from .env.example"
        echo "  ⚠ Please update .env with your AWS credentials"
    fi
else
    echo "✓ .env file already exists"
fi

# Setup Python virtual environment
echo ""
echo "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Python dependencies installed"

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✓ Setup Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Update .env with your AWS credentials:"
echo "   - AWS_REGION"
echo "   - AWS_ACCESS_KEY_ID"
echo "   - AWS_SECRET_ACCESS_KEY"
echo "   - BEDROCK_MODEL_ID (e.g., anthropic.claude-v2)"
echo ""
echo "2. To start development:"
echo "   • Python: source venv/bin/activate && python middleware/amazon-bedrock-app/main.py"
echo "   • Or use: make dev"
echo ""
echo "3. See README.md for more information"
echo ""
