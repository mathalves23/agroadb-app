#!/bin/bash
# Script de Restauração de Backup

set -e

if [ -z "$1" ]; then
    echo "❌ Erro: Especifique o arquivo de backup"
    echo "Uso: ./restore.sh <arquivo_backup.sql.gz>"
    echo ""
    echo "Backups disponíveis:"
    ls -lh /backups/*.sql.gz
    exit 1
fi

BACKUP_FILE=$1
DB_NAME="${POSTGRES_DB:-agroadb}"
DB_USER="${POSTGRES_USER:-agroadb}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"

echo "⚠️  ATENÇÃO: Esta operação vai SOBRESCREVER o banco de dados atual!"
echo "🗄️ Banco: $DB_NAME"
echo "📦 Backup: $BACKUP_FILE"
echo ""
read -p "Tem certeza? (digite 'sim' para confirmar): " CONFIRM

if [ "$CONFIRM" != "sim" ]; then
    echo "❌ Restauração cancelada."
    exit 0
fi

echo "🔄 Iniciando restauração..."

# Dropar conexões existentes
PGPASSWORD="${POSTGRES_PASSWORD}" psql \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d postgres \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();"

# Dropar e recriar banco
PGPASSWORD="${POSTGRES_PASSWORD}" psql \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d postgres \
    -c "DROP DATABASE IF EXISTS $DB_NAME;"

PGPASSWORD="${POSTGRES_PASSWORD}" psql \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d postgres \
    -c "CREATE DATABASE $DB_NAME;"

# Restaurar backup
gunzip < $BACKUP_FILE | PGPASSWORD="${POSTGRES_PASSWORD}" psql \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d $DB_NAME

if [ $? -eq 0 ]; then
    echo "✅ Restauração concluída com sucesso!"
else
    echo "❌ Erro ao restaurar backup!"
    exit 1
fi

echo "✅ Banco de dados restaurado: $DB_NAME"
echo "📅 Data: $(date)"
