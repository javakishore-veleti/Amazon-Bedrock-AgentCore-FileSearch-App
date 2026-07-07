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
echo "1. Configuration uses YAML profiles (default: local)."
echo "   See middleware/amazon-bedrock-app/config/README.md"
echo ""
echo "2. Export secrets as environment variables when needed, e.g.:"
echo "   export VECTOR_DB_OPENAI_API_KEY=sk-..."
echo "   export AWS_ACCESS_KEY_ID=..."
echo "   export AWS_SECRET_ACCESS_KEY=..."
echo ""
echo "3. Optional: select a profile"
echo "   export APP_PROFILE=local    # default"
echo "   export APP_PROFILE=docker"
echo ""
echo "4. To start development:"
echo "   source venv/bin/activate && python middleware/amazon-bedrock-app/main.py"
echo ""
echo "5. See README.md for more information"
echo ""
