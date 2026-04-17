#!/bin/bash

# =============================================================================
# INICIAR APLICAÇÃO SEM DOCKER - AgroADB
# Inicia Backend e Frontend apenas com processos locais
# =============================================================================

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 Iniciando AgroADB (SEM Docker)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar se setup foi executado
if [ ! -f "backend/.env" ]; then
    echo "❌ ERRO: Configuração não encontrada!"
    echo "   Execute primeiro: ./setup-sem-docker.sh"
    exit 1
fi

# Criar pasta de logs se não existir
mkdir -p logs

# Função para limpar ao sair
cleanup() {
    echo ""
    echo "🛑 Encerrando serviços..."
    
    # Matar processos
    [ ! -z "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null && echo "   ✅ Backend parado"
    [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null && echo "   ✅ Frontend parado"
    
    # Matar qualquer processo restante
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    echo "✅ Todos os serviços foram encerrados"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Limpar logs antigos
echo "🧹 Limpando logs antigos..."
rm -f logs/backend.log logs/frontend.log
echo "✅ Logs limpos"
echo ""

# Iniciar Redis (se habilitado)
ENABLE_WORKERS=$(grep -E "^ENABLE_WORKERS=" backend/.env 2>/dev/null | cut -d '=' -f2)
if [ "$ENABLE_WORKERS" = "true" ]; then
    echo "🧠 ENABLE_WORKERS=true → Iniciando Redis..."
    if command -v redis-server >/dev/null 2>&1; then
        if ! pgrep -x "redis-server" >/dev/null; then
            if command -v brew >/dev/null 2>&1; then
                brew services start redis >/dev/null 2>&1 || true
            fi
            # fallback
            redis-server --daemonize yes >/dev/null 2>&1 || true
        fi
        echo "   ✅ Redis iniciado"
    else
        echo "   ❌ Redis não encontrado. Instale: brew install redis"
    fi
    echo ""
fi

# Iniciar Backend
echo "🔥 Iniciando Backend API..."
cd backend
source venv/bin/activate

# Iniciar em background
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

cd ..

echo "   Backend iniciado (PID: $BACKEND_PID)"
echo "   URL: http://localhost:8000"
echo "   Logs: logs/backend.log"
echo "   Aguardando inicialização..."
sleep 5

# Verificar se backend está respondendo
echo -n "   Verificando saúde... "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend está respondendo!"
else
    echo "⚠️  Backend ainda está inicializando..."
fi
echo ""

# Iniciar Celery Worker (se habilitado)
if [ "$ENABLE_WORKERS" = "true" ]; then
    echo "⚙️  Iniciando Celery Worker..."
    cd backend
    source venv/bin/activate
    nohup celery -A app.workers.celery_app.celery_app worker -l info > ../logs/celery.log 2>&1 &
    CELERY_PID=$!
    cd ..
    echo "   ✅ Celery iniciado (PID: $CELERY_PID)"
    echo "   Logs: logs/celery.log"
    echo ""
fi

# Iniciar Frontend
echo "🎨 Iniciando Frontend..."
cd frontend

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "   ⚠️  node_modules não encontrado. Execute: ./setup-sem-docker.sh"
    exit 1
fi

# Iniciar em background
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

echo "   Frontend iniciado (PID: $FRONTEND_PID)"
echo "   URL: http://localhost:5173"
echo "   Logs: logs/frontend.log"
echo "   Aguardando inicialização..."
sleep 8

# Verificar se frontend está respondendo
echo -n "   Verificando saúde... "
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend está respondendo!"
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
echo "📊 SERVIÇOS RODANDO:"
echo "   ✅ Backend:  PID $BACKEND_PID (porta 8000)"
echo "   ✅ Frontend: PID $FRONTEND_PID (porta 5173)"
echo "   💾 Banco:    SQLite (backend/agroadb_local.db)"
echo ""
echo "📝 MONITORAR LOGS:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 PARAR APLICAÇÃO:"
echo "   Pressione Ctrl+C OU execute: ./stop-sem-docker.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ Aplicação rodando... (Ctrl+C para parar)"
echo ""
echo "💡 DICA: Abra http://localhost:5173 no navegador agora!"
echo ""

# Aguardar até receber Ctrl+C
wait
