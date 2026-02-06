#!/bin/bash

# =============================================================================
# SETUP SEM DOCKER - AgroADB
# Configura aplicação para rodar apenas com processos locais
# =============================================================================

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 AgroADB - Setup Local (SEM Docker)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ ERRO: Python 3 não encontrado!"
    echo "   Instale: brew install python@3.11"
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ ERRO: Node.js não encontrado!"
    echo "   Instale: brew install node"
    exit 1
fi

echo "✅ Python e Node.js encontrados"
echo ""

# Criar arquivo .env para desenvolvimento local SEM Docker
echo "📝 Criando configuração local (.env)..."

cat > backend/.env << 'EOF'
# =============================================================================
# AgroADB - Configuração LOCAL SEM DOCKER
# =============================================================================

# Project Info
PROJECT_NAME=AgroADB
PROJECT_DESCRIPTION=Sistema de Inteligência Patrimonial para o Agronegócio
VERSION=1.0.0

# Environment
ENVIRONMENT=development
ENABLE_WORKERS=false

# Database (SQLite - não requer PostgreSQL!)
DATABASE_URL=sqlite+aiosqlite:///./agroadb_local.db

# Redis (necessário para workers em dados reais)
REDIS_URL=redis://localhost:6379/0

# Security & JWT
SECRET_KEY=local-dev-secret-key-min-32-chars-change-in-production-please
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=bG9jYWwtZGV2LWVuY3J5cHRpb24ta2V5LWJhc2U2NA==

# HTTPS
FORCE_HTTPS=false
HTTPS_REDIRECT=false

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE","PATCH"]
CORS_ALLOW_HEADERS=["*"]
CORS_MAX_AGE=600

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Rate Limiting
RATE_LIMIT_PER_MINUTE=1000

# Scraping
SCRAPING_TIMEOUT=30
SCRAPING_MAX_RETRIES=3
SCRAPING_DELAY=2.0

# External APIs (configure suas chaves reais aqui para dados verdadeiros)
INCRA_API_KEY=
CAR_API_KEY=
SERPAPI_KEY=
OPENAI_API_KEY=

# Legal Integration APIs
PJE_API_URL=
PJE_API_KEY=
DATAJUD_API_URL=https://api-publica.datajud.cnj.jus.br
DATAJUD_API_KEY=

# Conecta gov.br - SNCR
CONECTA_SNCR_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_SNCR_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_SNCR_CLIENT_ID=
CONECTA_SNCR_CLIENT_SECRET=
CONECTA_SNCR_API_KEY=
CONECTA_SNCR_IMOVEL_PATH=/api-sncr/v2/consultarImovelPorCodigo/{codigo}
CONECTA_SNCR_CPF_CNPJ_PATH=/api-sncr/v2/consultarImovelPorCpfCnpj/{cpf_cnpj}
CONECTA_SNCR_SITUACAO_PATH=/api-sncr/v2/verificarSituacaoImovel/{codigo}
CONECTA_SNCR_CCIR_PATH=/api-sncr/v2/baixarCcirPorCodigoImovel/{codigo}

# Conecta gov.br - SIGEF
CONECTA_SIGEF_API_URL=
CONECTA_SIGEF_CLIENT_ID=
CONECTA_SIGEF_CLIENT_SECRET=
CONECTA_SIGEF_API_KEY=
CONECTA_SIGEF_IMOVEL_PATH=
CONECTA_SIGEF_PARCELAS_PATH=

# Conecta gov.br - SICAR
CONECTA_SICAR_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_SICAR_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_SICAR_CLIENT_ID=
CONECTA_SICAR_CLIENT_SECRET=
CONECTA_SICAR_API_KEY=
CONECTA_SICAR_CPF_CNPJ_PATH=/api-sicar-cpfcnpj/v1/{cpf_cnpj}
CONECTA_SICAR_IMOVEL_PATH=

# Conecta gov.br - SNCCI
CONECTA_SNCCI_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_SNCCI_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_SNCCI_CLIENT_ID=
CONECTA_SNCCI_CLIENT_SECRET=
CONECTA_SNCCI_API_KEY=
CONECTA_SNCCI_PARCELAS_PATH=/sncci/v1/parcelas
CONECTA_SNCCI_CREDITOS_ATIVOS_PATH=/sncci/v1/creditos-ativos
CONECTA_SNCCI_CREDITOS_PATH=/sncci/v1/creditos/{codigo}
CONECTA_SNCCI_BOLETOS_PATH=/sncci/v1/boletos

# Conecta gov.br - SIGEF GEO
CONECTA_SIGEF_GEO_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_SIGEF_GEO_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_SIGEF_GEO_CLIENT_ID=
CONECTA_SIGEF_GEO_CLIENT_SECRET=
CONECTA_SIGEF_GEO_API_KEY=
CONECTA_SIGEF_GEO_PARCELAS_PATH=/api-sigef-geo/v1/parcelas
CONECTA_SIGEF_GEO_PARCELAS_GEOJSON_PATH=/api-sigef-geo/v1/parcelas/serpro

# Conecta gov.br - Consulta CNPJ (RFB)
CONECTA_CNPJ_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_CNPJ_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_CNPJ_CLIENT_ID=
CONECTA_CNPJ_CLIENT_SECRET=
CONECTA_CNPJ_API_KEY=
CONECTA_CNPJ_BASICA_PATH=/api-cnpj-basica/v2/basica/{cnpj}
CONECTA_CNPJ_QSA_PATH=/api-cnpj-qsa/v2/qsa/{cnpj}
CONECTA_CNPJ_EMPRESA_PATH=/api-cnpj-empresa/v2/empresa/{cnpj}

# Conecta gov.br - Consulta CND (RFB/PGFN)
CONECTA_CND_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_CND_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_CND_CLIENT_ID=
CONECTA_CND_CLIENT_SECRET=
CONECTA_CND_API_KEY=
CONECTA_CND_CERTIDAO_PATH=/api-cnd/v1/ConsultaCnd/certidao

# Conecta gov.br - CADIN Consulta/Contratante
CONECTA_CADIN_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_CADIN_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_CADIN_CLIENT_ID=
CONECTA_CADIN_CLIENT_SECRET=
CONECTA_CADIN_API_KEY=
CONECTA_CADIN_INFO_CPF_PATH=/registro/info/{cpf}/cpf
CONECTA_CADIN_INFO_CNPJ_PATH=/registro/info/{cnpj}/cnpj
CONECTA_CADIN_COMPLETA_CPF_PATH=/registro/consultaCompleta/{cpf}/cpf
CONECTA_CADIN_COMPLETA_CNPJ_PATH=/registro/consultaCompleta/{cnpj}/cnpj
CONECTA_CADIN_VERSAO_PATH=/registro/versaoApi

# Portal gov.br - API de Serviços
PORTAL_SERVICOS_API_URL=https://www.servicos.gov.br/api/v1
PORTAL_SERVICOS_AUTH_TOKEN=

# Portal gov.br - API de Serviços Estaduais
SERVICOS_ESTADUAIS_API_URL=https://gov.br/apiestados
SERVICOS_ESTADUAIS_AUTH_TOKEN=

# SIGEF Parcelas (Infosimples / WS)
SIGEF_PARCELAS_API_URL=
SIGEF_PARCELAS_MAX_PAGES=5
SIGEF_LOGIN_CPF=
SIGEF_LOGIN_SENHA=
SIGEF_PKCS12_CERT=
SIGEF_PKCS12_PASS=

# Portal da Transparência (CGU) — Obter chave gratuita em https://portaldatransparencia.gov.br/api-de-dados
PORTAL_TRANSPARENCIA_API_KEY=
EOF

echo "✅ Configuração criada: backend/.env"
echo ""

# Criar pastas necessárias
echo "📁 Criando estrutura de pastas..."
mkdir -p logs
mkdir -p backend/htmlcov
echo "✅ Pastas criadas"
echo ""

# Instalar dependências do Backend
echo "📦 Instalando dependências do Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "   Criando ambiente virtual Python..."
    python3 -m venv venv
fi

echo "   Ativando ambiente virtual..."
source venv/bin/activate

echo "   Instalando pacotes Python... (pode demorar 2-3 minutos)"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt 2>&1 | grep -E "(Successfully|ERROR)" || echo "   Instalando..."
pip install greenlet aiosqlite > /dev/null 2>&1

echo "✅ Dependências do Backend instaladas"
cd ..
echo ""

# Criar banco de dados SQLite e tabelas
echo "🗄️  Criando banco de dados SQLite..."
cd backend
source venv/bin/activate

python << 'PYTHON_EOF'
import asyncio
from app.core.database import engine, Base
from app.domain.user import User
from app.domain.investigation import Investigation
from app.domain.property import Property
from app.domain.company import Company
from app.domain.lease_contract import LeaseContract

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Banco de dados criado com sucesso!")
        return True
    except Exception as e:
        print(f"⚠️  Erro ao criar banco: {e}")
        return False

if asyncio.run(init_db()):
    print("✅ Tabelas: users, investigations, properties, companies, lease_contracts")
PYTHON_EOF

cd ..
echo ""

# Criar usuário admin
echo "👤 Criando usuário administrador..."
cd backend
source venv/bin/activate

python << 'PYTHON_EOF'
import asyncio
from app.core.database import AsyncSessionLocal
from app.domain.user import User
from app.core.security import get_password_hash
from sqlalchemy import select
from datetime import datetime

async def create_admin():
    try:
        async with AsyncSessionLocal() as db:
            # Verificar se já existe
            result = await db.execute(select(User).where(User.email == 'admin@agroadb.com'))
            existing = result.scalar_one_or_none()
            
            if existing:
                print('⚠️  Usuário admin já existe')
                print('   Email: admin@agroadb.com')
                print('   Senha: admin123')
                return
            
            # Criar admin
            admin = User(
                email='admin@agroadb.com',
                username='admin',
                full_name='Administrador AgroADB',
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
    except Exception as e:
        print(f'⚠️  Erro ao criar admin: {e}')

asyncio.run(create_admin())
PYTHON_EOF

cd ..
echo ""

# Instalar dependências do Frontend
echo "📦 Instalando dependências do Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "   Instalando pacotes Node.js... (pode demorar 2-3 minutos)"
    npm install 2>&1 | grep -E "(added|ERROR)" || echo "   Instalando..."
    echo "✅ Dependências do Frontend instaladas"
else
    echo "✅ Dependências do Frontend já instaladas"
fi

cd ..
echo ""

# Criar arquivo .env para frontend
echo "📝 Criando configuração do Frontend..."
cat > frontend/.env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=AgroADB
VITE_APP_VERSION=1.0.0
EOF

echo "✅ Configuração do Frontend criada"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ SETUP COMPLETO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 BANCO DE DADOS:"
echo "   SQLite: backend/agroadb_local.db"
echo ""
echo "👤 USUÁRIO CRIADO:"
echo "   Email: admin@agroadb.com"
echo "   Senha: admin123"
echo ""
echo "🚀 PRÓXIMO PASSO:"
echo "   Execute: ./start-sem-docker.sh"
echo ""
echo "🔑 OPCIONAL - Configurar API keys para dados reais:"
echo "   Edite: backend/.env"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
