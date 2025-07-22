#!/bin/bash
# Audio Processing System - Linux/Unix Setup Script

set -e  # Exit on any error

echo "🐧 Setting up Audio Processing System for Linux/Unix..."
echo "=================================================="

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install minimal requirements first
echo "📥 Installing minimal requirements..."
pip install -r pytest/requirements-minimal.txt

# Try to install full requirements (with fallback)
echo "📥 Attempting to install full requirements..."
if pip install -r pytest/requirements.txt; then
    echo "✅ Full requirements installed successfully"
else
    echo "⚠️ Some dependencies failed, using minimal setup"
    echo "This is normal on systems without PostgreSQL development libraries"
fi

# Make scripts executable
chmod +x scripts/*.sh

# Create directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p test-reports
mkdir -p performance_results

echo ""
echo "✅ Setup completed!"
echo ""
echo "🚀 Quick start:"
echo "   source .venv/bin/activate"
echo "   python pytest/demo_test.py"
echo ""
echo "📖 For more options, see:"
echo "   ./scripts/run_tests.sh --help"
echo "   cat pytest/RUN_TESTS.md" 