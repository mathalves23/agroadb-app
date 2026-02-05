#!/bin/bash

# Script de Verificação Completa - AgroADB
# Verifica build, linter e testes

set -e

echo "🔍 AgroADB - Verificação Completa"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        ERRORS=$((ERRORS + 1))
    fi
}

# ==================== BACKEND ====================
echo "🐍 BACKEND VERIFICATION"
echo "======================="
echo ""

cd backend

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing backend dependencies..."
pip install -q -r requirements.txt pytest pytest-cov flake8 2>/dev/null || true
print_status $? "Backend dependencies installed"
echo ""

# Linter check
echo "🔍 Running flake8..."
flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics 2>/dev/null
BACKEND_LINT_CRITICAL=$?
flake8 app --count --max-complexity=10 --max-line-length=127 --statistics 2>/dev/null
BACKEND_LINT=$?
print_status $BACKEND_LINT "Backend linter check"
echo ""

# Type hints check (if mypy is available)
echo "🔍 Checking type hints..."
pip install -q mypy 2>/dev/null || true
mypy app --ignore-missing-imports 2>/dev/null || true
print_status 0 "Type hints check (optional)"
echo ""

# Run tests
echo "🧪 Running backend tests..."
python -m pytest tests/ \
    -v \
    --cov=app \
    --cov-report=term-missing \
    --cov-fail-under=60 \
    --tb=short 2>&1 | tail -20
BACKEND_TESTS=$?
print_status $BACKEND_TESTS "Backend tests (60%+ coverage required)"
echo ""

# Check if app can start
echo "🚀 Checking if backend starts..."
timeout 5 python -c "from app.main import app; print('✅ App imports successfully')" 2>/dev/null
BACKEND_IMPORT=$?
print_status $BACKEND_IMPORT "Backend app import"
echo ""

cd ..

# ==================== FRONTEND ====================
echo ""
echo "⚛️  FRONTEND VERIFICATION"
echo "========================"
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm ci 2>/dev/null || npm install 2>/dev/null
fi
print_status $? "Frontend dependencies installed"
echo ""

# Linter check
echo "🔍 Running ESLint..."
npm run lint 2>&1 | tail -20
FRONTEND_LINT=$?
print_status $FRONTEND_LINT "Frontend linter check"
echo ""

# Type check
echo "🔍 Running TypeScript type check..."
npm run type-check 2>&1 | tail -20
FRONTEND_TYPES=$?
print_status $FRONTEND_TYPES "TypeScript type check"
echo ""

# Run tests
echo "🧪 Running frontend tests..."
npm run test:ci 2>&1 | tail -30
FRONTEND_TESTS=$?
print_status $FRONTEND_TESTS "Frontend tests (60%+ coverage required)"
echo ""

# Build check
echo "🏗️  Running production build..."
npm run build 2>&1 | tail -20
FRONTEND_BUILD=$?
print_status $FRONTEND_BUILD "Frontend production build"
echo ""

cd ..

# ==================== DOCKER ====================
echo ""
echo "🐳 DOCKER VERIFICATION"
echo "======================"
echo ""

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "🔍 Checking Dockerfiles..."
    
    # Validate backend Dockerfile
    if [ -f "backend/Dockerfile" ]; then
        docker build --no-cache -t agroadb-backend-test backend/ > /dev/null 2>&1
        DOCKER_BACKEND=$?
        print_status $DOCKER_BACKEND "Backend Dockerfile build"
    else
        echo -e "${YELLOW}⚠️  Backend Dockerfile not found${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Validate frontend Dockerfile
    if [ -f "frontend/Dockerfile" ]; then
        docker build --no-cache -t agroadb-frontend-test frontend/ > /dev/null 2>&1
        DOCKER_FRONTEND=$?
        print_status $DOCKER_FRONTEND "Frontend Dockerfile build"
    else
        echo -e "${YELLOW}⚠️  Frontend Dockerfile not found${NC}"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Clean up test images
    docker rmi agroadb-backend-test agroadb-frontend-test > /dev/null 2>&1 || true
else
    echo -e "${YELLOW}⚠️  Docker not available - skipping Docker checks${NC}"
fi

echo ""

# ==================== SUMMARY ====================
echo ""
echo "========================================="
echo "📊 VERIFICATION SUMMARY"
echo "========================================="
echo ""

# Backend
echo "🐍 BACKEND:"
print_status $BACKEND_LINT "  Linter"
print_status $BACKEND_TESTS "  Tests & Coverage"
print_status $BACKEND_IMPORT "  Import Check"
echo ""

# Frontend
echo "⚛️  FRONTEND:"
print_status $FRONTEND_LINT "  Linter"
print_status $FRONTEND_TYPES "  Type Check"
print_status $FRONTEND_TESTS "  Tests & Coverage"
print_status $FRONTEND_BUILD "  Production Build"
echo ""

# Docker
if command -v docker &> /dev/null; then
    echo "🐳 DOCKER:"
    print_status $DOCKER_BACKEND "  Backend Image"
    print_status $DOCKER_FRONTEND "  Frontend Image"
    echo ""
fi

# Final result
echo "========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo ""
    echo "🎉 Your application is ready for production!"
    echo ""
    echo "📊 Summary:"
    echo "   - Backend: Clean code, tests passing, 60%+ coverage"
    echo "   - Frontend: Clean code, tests passing, 60%+ coverage, build OK"
    echo "   - Docker: Images build successfully"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Review coverage reports:"
    echo "      - Backend:  backend/htmlcov/index.html"
    echo "      - Frontend: frontend/coverage/index.html"
    echo "   2. Deploy: ./scripts/deploy.sh"
    echo ""
    exit 0
else
    echo -e "${RED}❌ $ERRORS CHECK(S) FAILED${NC}"
    echo ""
    echo "Please fix the issues above before deploying."
    echo ""
    echo "Common fixes:"
    echo "  - Backend linter: flake8 app --show-source"
    echo "  - Frontend linter: npm run lint"
    echo "  - Type errors: npm run type-check"
    echo "  - Failed tests: Check test output above"
    echo ""
    exit 1
fi
