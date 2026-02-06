#!/bin/bash

# =============================================================================
# PARAR APLICAÇÃO SEM DOCKER - AgroADB
# =============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🛑 Parando AgroADB"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Parar Backend
echo "🛑 Parando Backend..."
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "✅ Backend parado" || echo "⚠️  Backend não estava rodando"

# Parar Frontend
echo "🛑 Parando Frontend..."
pkill -f "vite" 2>/dev/null && echo "✅ Frontend parado" || echo "⚠️  Frontend não estava rodando"
pkill -f "npm run dev" 2>/dev/null || true

# Parar Celery (se estiver rodando)
echo "🛑 Parando Celery..."
pkill -f "celery" 2>/dev/null && echo "✅ Celery parado" || echo "⚠️  Celery não estava rodando"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ APLICAÇÃO PARADA!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Para iniciar novamente: ./start-sem-docker.sh"
echo ""
