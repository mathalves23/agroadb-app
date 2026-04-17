# ==================== DEPLOY & INFRASTRUCTURE DOCUMENTATION ====================

## 📦 Deployment Guide

Este guia fornece instruções completas para fazer deploy do AgroADB em produção.

### 📋 Pré-requisitos

- **Servidor**: Ubuntu 20.04+ ou similar
- **RAM**: Mínimo 4GB (recomendado 8GB+)
- **Disco**: Mínimo 50GB
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Domínio**: Configurado e apontando para o servidor
- **Conta AWS** (opcional): Para usar S3, CloudFront, ECR

---

## 🚀 Deploy Rápido

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/agroadb.git
cd agroadb
```

### 2. Configure variáveis de ambiente

```bash
cp .env.example .env
nano .env
```

**Variáveis obrigatórias:**

```bash
# Database
POSTGRES_USER=agroadb
POSTGRES_PASSWORD=<senha-forte>
POSTGRES_DB=agroadb

# Redis
REDIS_PASSWORD=<senha-forte>

# Security
SECRET_KEY=<chave-secreta-32-chars>
ENCRYPTION_KEY=<chave-base64>

# Environment
ENVIRONMENT=production
FORCE_HTTPS=true

# Domain
DOMAIN=app.agroadb.com
SSL_EMAIL=admin@agroadb.com
```

### 3. Execute o script de deploy

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh production app.agroadb.com
```

O script irá:
- ✅ Instalar dependências (Docker, AWS CLI)
- ✅ Configurar SSL/TLS com Let's Encrypt
- ✅ Fazer backup do banco de dados existente
- ✅ Construir imagens Docker
- ✅ Iniciar todos os serviços
- ✅ Executar migrações do banco
- ✅ Configurar backups automáticos
- ✅ Configurar monitoring (Prometheus + Grafana)

---

## 🔧 Configuração Manual

### Docker Compose - Produção

```bash
# Iniciar serviços
docker-compose -f docker-compose.production.yml up -d

# Ver logs
docker-compose -f docker-compose.production.yml logs -f

# Parar serviços
docker-compose -f docker-compose.production.yml down

# Reconstruir e reiniciar
docker-compose -f docker-compose.production.yml up -d --build
```

### SSL/TLS com Let's Encrypt

```bash
# Obter certificado SSL
./scripts/setup-ssl.sh app.agroadb.com admin@agroadb.com

# Renovar manualmente
sudo certbot renew

# Testar renovação
sudo certbot renew --dry-run
```

### Backups

```bash
# Backup manual
./scripts/backup.sh

# Restaurar backup
./scripts/restore.sh /backups/agroadb_backup_YYYYMMDD_HHMMSS.sql.gz

# Configurar backup automático (via crontab)
crontab -e

# Adicionar linha (backup diário às 2AM):
0 2 * * * /path/to/agroadb/scripts/backup.sh >> /path/to/agroadb/logs/backup.log 2>&1
```

---

## ☁️ Deploy em Cloud (AWS)

### 1. Configurar AWS CLI

```bash
aws configure
# AWS Access Key ID: [seu-access-key]
# AWS Secret Access Key: [seu-secret-key]
# Default region: us-east-1
# Default output format: json
```

### 2. Criar recursos AWS

#### a) Criar ECR Repository

```bash
aws ecr create-repository --repository-name agroadb-backend --region us-east-1
aws ecr create-repository --repository-name agroadb-frontend --region us-east-1
```

#### b) Criar S3 Bucket (Frontend)

```bash
aws s3 mb s3://agroadb-production-frontend --region us-east-1

# Configurar site estático
aws s3 website s3://agroadb-production-frontend \
    --index-document index.html \
    --error-document index.html
```

#### c) Criar CloudFront Distribution

```bash
aws cloudfront create-distribution \
    --origin-domain-name agroadb-production-frontend.s3.us-east-1.amazonaws.com \
    --default-root-object index.html
```

#### d) Criar RDS (PostgreSQL)

```bash
aws rds create-db-instance \
    --db-instance-identifier agroadb-prod \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --engine-version 15.3 \
    --master-username agroadb \
    --master-user-password <senha-forte> \
    --allocated-storage 50 \
    --storage-encrypted \
    --publicly-accessible false \
    --backup-retention-period 7
```

#### e) Criar ElastiCache (Redis)

```bash
aws elasticache create-cache-cluster \
    --cache-cluster-id agroadb-prod-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1
```

### 3. Deploy via GitHub Actions

O workflow em `.github/workflows/ci-cd.yml` está configurado para:

- ✅ Executar testes automaticamente
- ✅ Scan de segurança com Trivy
- ✅ Deploy em staging (branch `develop`)
- ✅ Deploy em produção (branch `main`)

**Configurar secrets no GitHub:**

1. Vá em Settings > Secrets and variables > Actions
2. Adicione os seguintes secrets:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
CLOUDFRONT_STAGING_ID
CLOUDFRONT_PRODUCTION_ID
SECRET_KEY
ENCRYPTION_KEY
SLACK_WEBHOOK (opcional)
GRAFANA_PASSWORD
```

**Para fazer deploy:**

```bash
# Staging
git push origin develop

# Production
git push origin main
```

---

## 📊 Monitoring & Observability

### Prometheus

Acesse: `http://seu-servidor:9090`

**Queries úteis:**

```promql
# CPU usage
rate(process_cpu_seconds_total[5m])

# Memory usage
process_resident_memory_bytes

# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

### Grafana

Acesse: `http://seu-servidor:3001`

- **Usuário**: admin
- **Senha**: (definida em `GRAFANA_PASSWORD`)

**Dashboards recomendados:**

1. Node Exporter Full
2. PostgreSQL Database
3. Redis Dashboard
4. FastAPI Application Metrics

### Logs

```bash
# Ver logs de todos os serviços
docker-compose -f docker-compose.production.yml logs -f

# Ver logs de um serviço específico
docker-compose -f docker-compose.production.yml logs -f backend

# Ver últimas 100 linhas
docker-compose -f docker-compose.production.yml logs --tail=100 backend

# Filtrar logs por palavra-chave
docker-compose -f docker-compose.production.yml logs backend | grep ERROR
```

---

## 🔐 Segurança

### Firewall

```bash
# Permitir apenas portas necessárias
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### SSL/TLS Headers

O Nginx já está configurado com:
- ✅ Force HTTPS
- ✅ HSTS (HTTP Strict Transport Security)
- ✅ X-Frame-Options
- ✅ X-Content-Type-Options
- ✅ X-XSS-Protection
- ✅ Referrer-Policy

### Rate Limiting

Configurado no backend (FastAPI middleware):
- 60 requisições por minuto por IP
- Headers de rate limit na resposta

---

## 🧪 Testes Pós-Deploy

### Health Checks

```bash
# Backend
curl https://api.agroadb.com/health

# Frontend
curl https://app.agroadb.com/health

# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3001/api/health
```

### Smoke Tests

```bash
# Registrar usuário
curl -X POST https://api.agroadb.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# Login
curl -X POST https://api.agroadb.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Buscar investigações
curl https://api.agroadb.com/api/v1/investigations \
  -H "Authorization: Bearer <token>"
```

---

## 🔄 Atualizações

### Atualizar aplicação

```bash
# Pull das últimas mudanças
git pull origin main

# Reconstruir e reiniciar
docker-compose -f docker-compose.production.yml up -d --build

# Executar migrações
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head
```

### Rollback

```bash
# Voltar para versão anterior
git checkout <commit-hash>

# Rebuild
docker-compose -f docker-compose.production.yml up -d --build

# Rollback de migração
docker-compose -f docker-compose.production.yml exec backend alembic downgrade -1
```

---

## 📞 Troubleshooting

### Serviço não inicia

```bash
# Ver logs
docker-compose logs <service-name>

# Verificar configuração
docker-compose config

# Recriar container
docker-compose up -d --force-recreate <service-name>
```

### Erro de conexão com banco de dados

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Testar conexão
docker-compose exec postgres psql -U agroadb -d agroadb -c "SELECT 1;"

# Ver logs do PostgreSQL
docker-compose logs postgres
```

### Erro de memória

```bash
# Ver uso de recursos
docker stats

# Aumentar limite de memória no docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### SSL expirado

```bash
# Renovar manualmente
sudo certbot renew

# Copiar certificados
sudo cp /etc/letsencrypt/live/seu-dominio/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/seu-dominio/privkey.pem ./ssl/

# Recarregar nginx
docker-compose exec nginx nginx -s reload
```

---

## 📚 Recursos Adicionais

- [Documentação Docker](https://docs.docker.com/)
- [Let's Encrypt](https://letsencrypt.org/)
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

---

## 📝 Checklist de Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] SSL/TLS configurado
- [ ] Firewall configurado
- [ ] Backups automáticos configurados
- [ ] Monitoring (Prometheus + Grafana) funcionando
- [ ] Health checks passando
- [ ] DNS configurado
- [ ] Secrets rotacionados em produção
- [ ] Logs configurados
- [ ] Alertas configurados
- [ ] Documentação atualizada
- [ ] Time notificado sobre o deploy

---

🎉 **Deploy completo! Sua aplicação AgroADB está no ar!**
