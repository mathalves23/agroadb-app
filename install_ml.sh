#!/bin/bash
# Script de instalação rápida para ML e Análise de Rede

echo "========================================================"
echo "🚀 AgroADB - Instalação ML e Análise de Rede"
echo "========================================================"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Backend - Instalar dependências
echo "1️⃣ Instalando dependências do backend..."
cd backend
if pip install -r requirements.txt; then
    echo -e "${GREEN}✅ Dependências do backend instaladas${NC}"
else
    echo -e "${RED}❌ Erro ao instalar dependências do backend${NC}"
    exit 1
fi
echo ""

# 2. Executar migrations
echo "2️⃣ Executando migrations do banco de dados..."
if alembic upgrade head; then
    echo -e "${GREEN}✅ Migrations executadas com sucesso${NC}"
else
    echo -e "${YELLOW}⚠️ Erro ao executar migrations (pode ser que já estejam aplicadas)${NC}"
fi
echo ""
cd ..

# 3. Frontend - Instalar dependências
echo "3️⃣ Instalando dependências do frontend..."
cd frontend
if npm install; then
    echo -e "${GREEN}✅ Dependências do frontend instaladas${NC}"
else
    echo -e "${RED}❌ Erro ao instalar dependências do frontend${NC}"
    exit 1
fi
echo ""
cd ..

# 4. Executar teste
echo "4️⃣ Testando instalação..."
if python test_ml_setup.py; then
    echo -e "${GREEN}✅ Todos os testes passaram!${NC}"
else
    echo -e "${RED}❌ Alguns testes falharam${NC}"
    exit 1
fi
echo ""

# 5. Instruções finais
echo "========================================================"
echo -e "${GREEN}✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!${NC}"
echo "========================================================"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Iniciar o backend:"
echo "   cd backend && uvicorn app.main:app --reload"
echo ""
echo "2. Em outro terminal, iniciar o frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Acessar a aplicação:"
echo "   http://localhost:5173"
echo ""
echo "4. Testar as novas funcionalidades:"
echo "   - Criar ou abrir uma investigação"
echo "   - Adicionar dados (empresas, propriedades, contratos)"
echo "   - Acessar a aba '🌐 Rede' para visualização de relacionamentos"
echo "   - Acessar a aba '🧠 Análise ML' para score de risco e padrões"
echo ""
echo "📚 Documentação completa:"
echo "   docs/dev/07-machine-learning.md"
echo ""
echo "🎉 Tudo pronto para investigações com IA!"
echo ""
