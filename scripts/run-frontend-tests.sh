#!/bin/bash

# Frontend Tests Runner Script

set -e

echo "🧪 Running Frontend Tests..."
echo "==========================="

cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm ci
fi

# Run tests with coverage
echo ""
echo "🚀 Running tests..."
npm run test:ci

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All frontend tests passed!"
    echo "📊 Coverage report generated in coverage/index.html"
else
    echo ""
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi

cd ..
