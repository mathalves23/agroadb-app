#!/bin/bash

# Run All Tests (Backend + Frontend)

set -e

echo "🧪 AgroADB - Full Test Suite"
echo "============================"
echo ""

# Run backend tests
echo "1️⃣ BACKEND TESTS"
echo "=================="
bash ./scripts/run-backend-tests.sh

echo ""
echo ""

# Run frontend tests
echo "2️⃣ FRONTEND TESTS"
echo "=================="
bash ./scripts/run-frontend-tests.sh

echo ""
echo ""
echo "========================================="
echo "✅ ALL TESTS PASSED!"
echo "========================================="
echo ""
echo "📊 Coverage Reports:"
echo "   Backend:  backend/htmlcov/index.html"
echo "   Frontend: frontend/coverage/index.html"
echo ""
echo "🎉 Your application is well-tested and ready for production!"
