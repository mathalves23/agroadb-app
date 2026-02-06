#!/bin/bash

# =============================================================================
# SCRIPT DE INICIALIZAÇÃO LOCAL - AgroADB
# Inicia todos os serviços da aplicação
# =============================================================================

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 Iniciando AgroADB Localmente"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar se setup foi executado
if [ ! -f "backend/.env.local" ]; then
    echo "❌ ERRO: Arquivo .env.local não encontrado!"
    echo "   Execute primeiro: ./setup-local.sh"
    exit 1
fi

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ ERRO: Docker não está rodando!"
    echo "   Por favor, inicie o Docker Desktop e tente novamente."
    exit 1
fi

# Garantir que PostgreSQL e Redis estão rodando
echo "🐳 Verificando serviços Docker..."
if ! docker-compose ps | grep -q "postgres.*running"; then
    echo "   Iniciando PostgreSQL..."
    docker-compose up -d postgres
    sleep 10
fi

if ! docker-compose ps | grep -q "redis.*running"; then
    echo "   Iniciando Redis..."
    docker-compose up -d redis
    sleep 5
fi

echo "✅ PostgreSQL e Redis estão rodando"
echo ""

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Encerrando serviços..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    kill $CELERY_PID 2>/dev/null || true
    echo "✅ Serviços encerrados"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar Backend
echo "🔥 Iniciando Backend API..."
cd backend
source venv/bin/activate
cp .env.local .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "   Backend iniciado (PID: $BACKEND_PID)"
echo "   Logs: logs/backend.log"
echo "   Aguardando 5 segundos..."
sleep 5

# Verificar se backend está respondendo
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend está respondendo"
else
    echo "⚠️  Backend ainda está inicializando..."
fi
echo ""

# Iniciar Celery Worker (para scrapers assíncronos)
echo "⚙️  Iniciando Celery Worker..."
cd backend
source venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info > ../logs/celery.log 2>&1 &
CELERY_PID=$!
cd ..

echo "   Celery Worker iniciado (PID: $CELERY_PID)"
echo "   Logs: logs/celery.log"
echo ""

# Iniciar Frontend
echo "🎨 Iniciando Frontend..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "   Frontend iniciado (PID: $FRONTEND_PID)"
echo "   Logs: logs/frontend.log"
echo "   Aguardando 10 segundos..."
sleep 10

# Verificar se frontend está respondendo
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend está respondendo"
else
    echo "⚠️  Frontend ainda está inicializando..."
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ APLICAÇÃO INICIADA COM SUCESSO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 ACESSE A APLICAÇÃO:"
echo ""
echo "   🎨 Frontend:  http://localhost:5173"
echo "   🔥 Backend:   http://localhost:8000"
echo "   📚 API Docs:  http://localhost:8000/docs"
echo "   📖 ReDoc:     http://localhost:8000/redoc"
echo ""
echo "👤 LOGIN INICIAL:"
echo "   Email: admin@agroadb.com"
echo "   Senha: admin123"
echo ""
echo "📊 SERVIÇOS:"
echo "   ✅ PostgreSQL: localhost:5432"
echo "   ✅ Redis:      localhost:6379"
echo "   ✅ Backend:    PID $BACKEND_PID"
echo "   ✅ Celery:     PID $CELERY_PID"
echo "   ✅ Frontend:   PID $FRONTEND_PID"
echo ""
echo "📝 LOGS:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Celery:   tail -f logs/celery.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 PARAR SERVIÇOS:"
echo "   Pressione Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ Aplicação rodando... (Pressione Ctrl+C para parar)"
echo ""

# Manter script rodando
wait
