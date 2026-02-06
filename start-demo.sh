#!/bin/bash

# Configurar encoding UTF-8
export LANG=pt_BR.UTF-8
export LC_ALL=pt_BR.UTF-8

clear

echo "═══════════════════════════════════════════════════════════════════"
echo "  🚀 AgroADB - DEMO RÁPIDA"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python não encontrado! Instale Python 3.11+ primeiro."
    echo "   Download: https://www.python.org/downloads/"
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado! Instale Node.js 18+ primeiro."
    echo "   Download: https://nodejs.org/"
    exit 1
fi

echo "✅ Python e Node.js encontrados"
echo ""

# ═══════════════════════════════════════════════════════════════════
# BACKEND
# ═══════════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════════════════════════"
echo "  📦 CONFIGURANDO BACKEND"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

cd backend

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📝 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências do backend..."
pip install -q -r requirements.txt

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "📝 Criando configuração (.env)..."
    cat > .env << EOF
DATABASE_URL=sqlite:///./agroadb.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
EOF
fi

# Criar banco de dados
echo "🗄️  Criando banco de dados..."
python -c "from app.core.database import create_tables; import asyncio; asyncio.run(create_tables())" 2>/dev/null

# Popular com dados demo
echo "🎬 Criando dados de demonstração..."
echo ""
python -m scripts.seed_demo_data
echo ""

# Iniciar backend em background
echo "🚀 Iniciando backend na porta 8000..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

cd ..

# ═══════════════════════════════════════════════════════════════════
# FRONTEND
# ═══════════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════════════════════════"
echo "  🎨 CONFIGURANDO FRONTEND"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

cd frontend

# Instalar dependências
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências do frontend..."
    npm install --silent
else
    echo "✅ Dependências do frontend já instaladas"
fi

# Iniciar frontend em background
echo "🚀 Iniciando frontend na porta 5173..."
echo ""
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid

cd ..

# ═══════════════════════════════════════════════════════════════════
# FINALIZAÇÃO
# ═══════════════════════════════════════════════════════════════════
sleep 5

clear
echo "═══════════════════════════════════════════════════════════════════"
echo "  ✅ AgroADB DEMO INICIADA COM SUCESSO!"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 ACESSE A APLICAÇÃO:"
echo "   http://localhost:5173"
echo ""
echo "🔐 CREDENCIAIS DE TESTE:"
echo ""
echo "   👤 Usuário 1 (Principal):"
echo "      Email: demo@agroadb.com"
echo "      Senha: demo123"
echo ""
echo "   👤 Usuário 2:"
echo "      Email: maria.silva@agroadb.com"
echo "      Senha: demo123"
echo ""
echo "   👤 Usuário 3:"
echo "      Email: joao.santos@agroadb.com"
echo "      Senha: demo123"
echo ""
echo "📊 DADOS DISPONÍVEIS:"
echo "   ✓ Múltiplos usuários e investigações"
echo "   ✓ Propriedades rurais"
echo "   ✓ Empresas e contratos"
echo "   ✓ Notificações e comentários"
echo ""
echo "⚙️  BACKEND API:"
echo "   http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  Para PARAR: Execute ./stop-demo.sh"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
