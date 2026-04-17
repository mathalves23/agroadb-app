#!/bin/bash

# Script para inicializar o banco de dados

echo "🔄 Criando banco de dados..."

# Criar diretório de migrações se não existir
mkdir -p alembic/versions

# Gerar migração inicial
echo "📝 Gerando migração inicial..."
alembic revision --autogenerate -m "Initial migration"

# Aplicar migrações
echo "⬆️ Aplicando migrações..."
alembic upgrade head

echo "✅ Banco de dados inicializado com sucesso!"
