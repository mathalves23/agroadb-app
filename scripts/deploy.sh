#!/bin/bash
# Script de Deploy Completo para Produção

set -e

echo "🚀 Iniciando deploy do AgroADB..."
echo "📅 Data: $(date)"
echo "---"

# Configurações
ENVIRONMENT="${1:-production}"
DOMAIN="${2:-app.agroadb.com}"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "🔧 Ambiente: $ENVIRONMENT"
echo "🌐 Domínio: $DOMAIN"
echo "☁️ AWS Region: $AWS_REGION"
echo "---"

# 1. Pré-requisitos
echo "✅ Verificando pré-requisitos..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instalando..."
    curl -fsSL https://get.docker.com | sh
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instalando..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI não encontrado. Instalando..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf awscliv2.zip aws/
fi

echo "✅ Pré-requisitos instalados!"
echo "---"

# 2. Verificar variáveis de ambiente
echo "🔐 Verificando variáveis de ambiente..."

if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "📝 Copie .env.example para .env e configure as variáveis"
    exit 1
fi

# Carregar variáveis
source .env

REQUIRED_VARS=(
    "SECRET_KEY"
    "ENCRYPTION_KEY"
    "POSTGRES_PASSWORD"
    "REDIS_PASSWORD"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Variável $var não definida no .env"
        exit 1
    fi
done

echo "✅ Variáveis de ambiente configuradas!"
echo "---"

# 3. Setup SSL/TLS
echo "🔐 Configurando SSL/TLS..."

if [ ! -f ./ssl/fullchain.pem ]; then
    echo "📜 Certificado SSL não encontrado. Executando setup-ssl.sh..."
    bash ./scripts/setup-ssl.sh $DOMAIN ${SSL_EMAIL:-admin@agroadb.com}
else
    echo "✅ Certificados SSL já existem"
fi

echo "---"

# 4. Backup do banco de dados (se já existir)
if [ "$ENVIRONMENT" = "production" ]; then
    echo "💾 Criando backup do banco de dados..."
    
    if docker ps | grep -q agroadb-postgres; then
        bash ./scripts/backup.sh || echo "⚠️ Backup falhou, continuando..."
    else
        echo "ℹ️ Banco de dados não encontrado, pulando backup"
    fi
    
    echo "---"
fi

# 5. Build das imagens Docker
echo "🏗️ Construindo imagens Docker..."

docker-compose -f docker-compose.production.yml build --no-cache

echo "✅ Imagens construídas!"
echo "---"

# 6. Push para ECR (opcional - para AWS)
if [ ! -z "$AWS_ECR_REGISTRY" ]; then
    echo "☁️ Fazendo push para AWS ECR..."
    
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ECR_REGISTRY
    
    docker tag agroadb-backend:latest $AWS_ECR_REGISTRY/agroadb-backend:$ENVIRONMENT
    docker tag agroadb-backend:latest $AWS_ECR_REGISTRY/agroadb-backend:latest
    
    docker push $AWS_ECR_REGISTRY/agroadb-backend:$ENVIRONMENT
    docker push $AWS_ECR_REGISTRY/agroadb-backend:latest
    
    echo "✅ Imagens enviadas para ECR!"
    echo "---"
fi

# 7. Parar containers antigos
echo "🛑 Parando containers antigos..."

docker-compose -f docker-compose.production.yml down || true

echo "✅ Containers antigos removidos!"
echo "---"

# 8. Iniciar novos containers
echo "🚀 Iniciando containers..."

docker-compose -f docker-compose.production.yml up -d

echo "✅ Containers iniciados!"
echo "---"

# 9. Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."

sleep 10

# Verificar saúde dos serviços
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend está saudável!"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "⏳ Tentativa $RETRY_COUNT/$MAX_RETRIES..."
    sleep 5
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Backend não ficou saudável após $MAX_RETRIES tentativas"
    exit 1
fi

echo "---"

# 10. Executar migrações do banco de dados
echo "🔄 Executando migrações do banco de dados..."

docker-compose -f docker-compose.production.yml exec -T backend alembic upgrade head || true

echo "✅ Migrações executadas!"
echo "---"

# 11. Configurar backup automático
echo "⏰ Configurando backup automático..."

# Adicionar ao crontab (backup diário às 2AM)
CRON_JOB="0 2 * * * cd $(pwd) && bash ./scripts/backup.sh >> ./logs/backup.log 2>&1"

(crontab -l 2>/dev/null | grep -v "backup.sh"; echo "$CRON_JOB") | crontab -

echo "✅ Backup automático configurado (diariamente às 2AM)"
echo "---"

# 12. Configurar monitoring
echo "📊 Configurando monitoring..."

# Verificar se Grafana está rodando
if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
    echo "✅ Grafana está rodando em http://localhost:3001"
    echo "👤 Usuário: admin"
    echo "🔑 Senha: ${GRAFANA_PASSWORD:-admin}"
else
    echo "⚠️ Grafana não está acessível"
fi

echo "---"

# 13. Status final
echo "📊 Status dos serviços:"
docker-compose -f docker-compose.production.yml ps

echo "---"
echo "✅ Deploy concluído com sucesso!"
echo ""
echo "🌐 URLs:"
echo "   - Frontend: https://$DOMAIN"
echo "   - Backend API: https://api.$DOMAIN"
echo "   - Grafana: http://localhost:3001"
echo "   - Prometheus: http://localhost:9090"
echo ""
echo "📋 Próximos passos:"
echo "   1. Configurar DNS para apontar para este servidor"
echo "   2. Testar acesso aos endpoints"
echo "   3. Configurar alertas no Grafana"
echo "   4. Verificar logs: docker-compose logs -f"
echo ""
echo "🎉 AgroADB está no ar!"
