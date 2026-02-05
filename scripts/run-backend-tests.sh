#!/bin/bash

# Backend Tests Runner Script

set -e

echo "🧪 Running Backend Tests..."
echo "=========================="

cd backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install test dependencies if needed
echo "📦 Installing test dependencies..."
pip install -q pytest pytest-cov pytest-asyncio httpx

# Run tests with coverage
echo ""
echo "🚀 Running tests..."
python -m pytest tests/ \
    -v \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-fail-under=60 \
    --tb=short

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All backend tests passed!"
    echo "📊 Coverage report generated in htmlcov/index.html"
else
    echo ""
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi

# Display coverage summary
echo ""
echo "📈 Coverage Summary:"
python -m coverage report --skip-empty

cd ..
