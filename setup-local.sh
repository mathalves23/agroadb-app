#!/bin/bash

# =============================================================================
# SCRIPT DE SETUP LOCAL - AgroADB
# Prepara e inicia a aplicação completa localmente
# =============================================================================

set -e  # Para em caso de erro

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 AgroADB - Setup Local Completo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ ERRO: Docker não está rodando!"
    echo "   Por favor, inicie o Docker Desktop e tente novamente."
    exit 1
fi

echo "✅ Docker está rodando"
echo ""

# Criar arquivo .env.local para produção local
echo "📝 Criando arquivo de configuração local (.env.local)..."

cat > backend/.env.local << 'EOF'
# =============================================================================
# AgroADB - Configuração LOCAL (Desenvolvimento com Docker)
# =============================================================================

# Project Info
PROJECT_NAME=AgroADB
PROJECT_DESCRIPTION=Sistema de Inteligência Patrimonial para o Agronegócio
VERSION=1.0.0

# Environment
ENVIRONMENT=development

# Database (PostgreSQL via Docker)
DATABASE_URL=postgresql+asyncpg://agroadb:agroadb_dev_password@localhost:5432/agroadb

# Redis (via Docker)
REDIS_URL=redis://localhost:6379/0

# Security & JWT
SECRET_KEY=local-dev-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=bG9jYWwtZGV2LWVuY3J5cHRpb24ta2V5LWJhc2U2NC1mb3JtYXQ=

# HTTPS
FORCE_HTTPS=false
HTTPS_REDIRECT=false

# CORS (permite acesso do frontend local)
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://localhost:8000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE","PATCH","OPTIONS"]
CORS_ALLOW_HEADERS=["*"]
CORS_MAX_AGE=600

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Rate Limiting (mais permissivo para desenvolvimento)
RATE_LIMIT_PER_MINUTE=1000

# Scraping (configurações reais)
SCRAPING_TIMEOUT=30
SCRAPING_MAX_RETRIES=3
SCRAPING_DELAY=2

# External APIs (SUBSTITUA com suas chaves reais!)
# Obtenha as chaves em:
# - INCRA: https://acervofundiario.incra.gov.br/
# - CAR: Consulte o órgão ambiental do seu estado
# - SerpAPI: https://serpapi.com/ (para Google Search)
# - OpenAI: https://platform.openai.com/ (para ML/OCR)
INCRA_API_KEY=your_incra_api_key_here
CAR_API_KEY=your_car_api_key_here
SERPAPI_KEY=your_serpapi_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Legal Integration APIs
PJE_API_URL=https://api.pje.jus.br
PJE_API_KEY=your_pje_api_key_here

# Email (opcional - para notificações)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
SMTP_FROM=noreply@agroadb.com

# Celery (para tarefas assíncronas)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Logs
LOG_LEVEL=INFO
LOG_FORMAT=json
EOF

echo "✅ Arquivo .env.local criado em backend/.env.local"
echo ""

# Parar containers antigos se existirem
echo "🛑 Parando containers antigos (se existirem)..."
docker-compose down -v 2>/dev/null || true
echo ""

# Limpar volumes antigos
echo "🧹 Limpando volumes antigos..."
docker volume prune -f 2>/dev/null || true
echo ""

# Iniciar serviços de infraestrutura (PostgreSQL + Redis)
echo "🐳 Iniciando PostgreSQL e Redis..."
docker-compose up -d postgres redis

echo "⏳ Aguardando serviços ficarem prontos (30 segundos)..."
sleep 30

# Verificar se serviços estão prontos
echo "🔍 Verificando saúde dos serviços..."

if docker-compose ps | grep -q "postgres.*healthy"; then
    echo "✅ PostgreSQL está pronto"
else
    echo "⚠️  PostgreSQL ainda está iniciando..."
fi

if docker-compose ps | grep -q "redis.*healthy"; then
    echo "✅ Redis está pronto"
else
    echo "⚠️  Redis ainda está iniciando..."
fi

echo ""

# Copiar .env.local para .env
echo "📋 Configurando variáveis de ambiente do backend..."
cp backend/.env.local backend/.env
echo "✅ Backend configurado"
echo ""

# Instalar dependências do backend
echo "📦 Instalando dependências do backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "   Criando ambiente virtual Python..."
    python3 -m venv venv
fi

echo "   Ativando ambiente virtual e instalando pacotes..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependências do backend instaladas"
cd ..
echo ""

# Criar banco de dados e executar migrações
echo "🗄️  Preparando banco de dados..."
cd backend
source venv/bin/activate

echo "   Criando tabelas..."
python -c "
from app.core.database import engine, Base
from app.domain.user import User
from app.domain.investigation import Investigation
from app.domain.property import Property
from app.domain.company import Company
from app.domain.lease_contract import LeaseContract

import asyncio

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print('✅ Tabelas criadas com sucesso!')

asyncio.run(init_db())
" || echo "⚠️  Tabelas já existem ou erro na criação"

cd ..
echo ""

# Criar usuário admin inicial
echo "👤 Criando usuário administrador..."
cd backend
source venv/bin/activate

python -c "
from app.core.database import async_session_maker
from app.domain.user import User
from app.core.security import get_password_hash
from datetime import datetime
import asyncio

async def create_admin():
    async with async_session_maker() as db:
        # Verificar se admin já existe
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == 'admin@agroadb.com'))
        existing = result.scalar_one_or_none()
        
        if existing:
            print('⚠️  Usuário admin já existe')
            return
        
        # Criar admin
        admin = User(
            email='admin@agroadb.com',
            username='admin',
            full_name='Administrador',
            hashed_password=get_password_hash('admin123'),
            is_active=True,
            is_superuser=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin)
        await db.commit()
        print('✅ Usuário admin criado!')
        print('   Email: admin@agroadb.com')
        print('   Senha: admin123')

asyncio.run(create_admin())
" || echo "⚠️  Erro ao criar usuário admin"

cd ..
echo ""

# Instalar dependências do frontend
echo "📦 Instalando dependências do frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install > /dev/null 2>&1
    echo "✅ Dependências do frontend instaladas"
else
    echo "✅ Dependências do frontend já instaladas"
fi
cd ..
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ SETUP COMPLETO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 PRÓXIMOS PASSOS:"
echo ""
echo "1. Configure suas API Keys em: backend/.env.local"
echo "   - INCRA_API_KEY"
echo "   - CAR_API_KEY"
echo "   - SERPAPI_KEY (opcional)"
echo "   - OPENAI_API_KEY (opcional)"
echo ""
echo "2. Inicie a aplicação com:"
echo "   ./start-local.sh"
echo ""
echo "3. Acesse:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend API: http://localhost:8000"
echo "   - Docs API: http://localhost:8000/docs"
echo ""
echo "4. Login inicial:"
echo "   Email: admin@agroadb.com"
echo "   Senha: admin123"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
