#!/bin/bash
# Script de Backup Automático do Banco de Dados
# Execute via cron: 0 2 * * * /path/to/backup.sh

set -e

# Configurações
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="${POSTGRES_DB:-agroadb}"
DB_USER="${POSTGRES_USER:-agroadb}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
RETENTION_DAYS=30

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Nome do arquivo
BACKUP_FILE="$BACKUP_DIR/agroadb_backup_$TIMESTAMP.sql.gz"

echo "🔄 Iniciando backup do banco de dados..."
echo "📅 Data: $(date)"
echo "🗄️ Banco: $DB_NAME"

# Fazer backup
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d $DB_NAME \
    --format=plain \
    --no-owner \
    --no-acl \
    | gzip > $BACKUP_FILE

# Verificar sucesso
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "✅ Backup concluído com sucesso!"
    echo "📦 Arquivo: $BACKUP_FILE"
    echo "💾 Tamanho: $BACKUP_SIZE"
else
    echo "❌ Erro ao fazer backup!"
    exit 1
fi

# Upload para S3 (opcional)
if [ ! -z "$AWS_S3_BUCKET" ]; then
    echo "☁️ Enviando para S3..."
    aws s3 cp $BACKUP_FILE s3://$AWS_S3_BUCKET/backups/database/
    
    if [ $? -eq 0 ]; then
        echo "✅ Backup enviado para S3: s3://$AWS_S3_BUCKET/backups/database/"
    else
        echo "⚠️ Erro ao enviar para S3 (backup local mantido)"
    fi
fi

# Limpar backups antigos (manter últimos 30 dias)
echo "🗑️ Limpando backups antigos (>$RETENTION_DAYS dias)..."
find $BACKUP_DIR -name "agroadb_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

REMAINING=$(find $BACKUP_DIR -name "agroadb_backup_*.sql.gz" -type f | wc -l)
echo "📊 Backups mantidos: $REMAINING"

# Notificar sucesso (webhook ou email - opcional)
if [ ! -z "$WEBHOOK_URL" ]; then
    curl -X POST $WEBHOOK_URL \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"✅ Backup do banco de dados concluído: $BACKUP_FILE ($BACKUP_SIZE)\"}"
fi

echo "✅ Script de backup finalizado!"
echo "---"
