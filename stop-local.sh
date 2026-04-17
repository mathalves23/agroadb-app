#!/bin/bash

# =============================================================================
# SCRIPT DE PARADA - AgroADB
# Para todos os serviços da aplicação
# =============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🛑 Parando AgroADB"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Parar processos Python (uvicorn, celery)
echo "🛑 Parando processos Python..."
pkill -f "uvicorn app.main:app" || true
pkill -f "celery -A app.workers" || true
echo "✅ Processos Python parados"
echo ""

# Parar processo Node (frontend)
echo "🛑 Parando Frontend..."
pkill -f "vite" || true
pkill -f "npm run dev" || true
echo "✅ Frontend parado"
echo ""

# Parar containers Docker (opcional - manter rodando para próxima execução)
read -p "Deseja parar PostgreSQL e Redis? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "🛑 Parando containers Docker..."
    docker-compose down
    echo "✅ Containers Docker parados"
else
    echo "ℹ️  PostgreSQL e Redis continuarão rodando"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ APLICAÇÃO PARADA!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
