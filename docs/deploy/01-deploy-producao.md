# Deploy em Produção - AgroADB

## 🚀 Guia Completo de Deploy

Este documento descreve como fazer deploy do AgroADB em ambiente de produção.

---

## 📋 Pré-requisitos

### Infraestrutura Mínima

- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disco**: 50 GB SSD
- **SO**: Ubuntu 20.04+ ou similar
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Domínio e DNS

- Domínio registado (ex.: `app.example.com`)
- Acesso ao DNS para configurar registros A/CNAME

### Contas Necessárias

- [ ] Conta AWS/GCP/Azure (opcional para cloud)
- [ ] Conta GitHub (para CI/CD)
- [ ] Conta SMTP (para emails)

---

## 🎯 Deploy Rápido (Docker Compose)

### 1. Preparar Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y git curl wget

# Instalar Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reiniciar sessão
exit
# Faça login novamente
```

### 2. Clonar e Configurar

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/agroadb.git
cd agroadb

# Configure variáveis
cp .env.example .env
nano .env
```

### 3. TLS (HTTPS)

Use o mecanismo da sua infraestrutura (por exemplo **Caddy**, **Traefik** na frente do Compose, **certbot** no anfitrião, ou balanceador gerido na cloud). Não versione chaves privadas nem `fullchain.pem` no Git.

### 4. Subir a stack

```bash
docker compose -f docker-compose.prod.yml up -d
# ou o ficheiro de compose que utilizar em produção
```

Aponte o DNS e o proxy reverso para os serviços expostos (frontend, API, documentação OpenAPI conforme a sua configuração).

---

## ☁️ Deploy em Cloud

### AWS (Amazon Web Services)

#### Passo 1: Criar ECR Repositories

```bash
aws ecr create-repository --repository-name agroadb-backend
aws ecr create-repository --repository-name agroadb-frontend
```

#### Passo 2: Criar RDS (PostgreSQL)

```bash
aws rds create-db-instance \
  --db-instance-identifier agroadb-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.3 \
  --master-username agroadb \
  --master-user-password SUA_SENHA_FORTE \
  --allocated-storage 50 \
  --storage-encrypted \
  --backup-retention-period 7
```

#### Passo 3: Criar ElastiCache (Redis)

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id agroadb-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

#### Passo 4: Criar S3 Bucket

```bash
aws s3 mb s3://agroadb-frontend
aws s3 website s3://agroadb-frontend --index-document index.html
```

#### Passo 5: Criar CloudFront Distribution

```bash
aws cloudfront create-distribution \
  --origin-domain-name agroadb-frontend.s3.amazonaws.com \
  --default-root-object index.html
```

#### Passo 6: CI e deploy

O ficheiro `.github/workflows/ci.yml` executa **lint, testes mínimos e build** em cada push/PR (backend: smoke + segurança; frontend: ESLint, TypeScript, Jest, Vite).

O **deploy** para AWS/GCP/etc. depende da sua conta e não deve ser hardcoded no repositório público: use `docker-compose.prod.yml`, imagens no seu registo e secrets apenas no ambiente de CI/CD que **você** configurar (por exemplo `workflow_dispatch` com credenciais armazenadas como GitHub Secrets).

### GCP (Google Cloud Platform)

```bash
# Criar projeto
gcloud projects create agroadb-prod

# Habilitar APIs
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Criar cluster GKE
gcloud container clusters create agroadb-cluster \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --region=us-central1

# Criar Cloud SQL
gcloud sql instances create agroadb-db \
  --database-version=POSTGRES_15 \
  --tier=db-n1-standard-2 \
  --region=us-central1

# Deploy
kubectl apply -f k8s/
```

### Azure

```bash
# Criar resource group
az group create --name agroadb-rg --location eastus

# Criar PostgreSQL
az postgres server create \
  --resource-group agroadb-rg \
  --name agroadb-db \
  --location eastus \
  --admin-user agroadb \
  --admin-password SUA_SENHA \
  --sku-name GP_Gen5_2

# Criar App Service
az webapp create \
  --resource-group agroadb-rg \
  --plan agroadb-plan \
  --name agroadb-backend \
  --runtime "PYTHON|3.11"
```

---

## 🔧 Configurações de Produção

### .env de Produção

```env
# CRITICAL: Use valores seguros!

DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/agroadb
REDIS_URL=redis://redis-host:6379/0

# Gere com: openssl rand -hex 32
SECRET_KEY=sua-chave-super-secreta-aqui-64-caracteres
ENCRYPTION_KEY=base64-encoded-key-aqui

ENVIRONMENT=production
DEBUG=False
FORCE_HTTPS=True

CORS_ORIGINS=["https://app.example.com"]

# Email
SMTP_HOST=smtp.sendgrid.net
SMTP_USER=apikey
SMTP_PASSWORD=SG.sua-api-key

# Sentry (opcional)
SENTRY_DSN=https://...@sentry.io/...

# AWS (opcional)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=agroadb-uploads
```

---

## 📊 Monitoramento

### Prometheus

Acesse: `http://seu-servidor:9090`

Queries úteis:
```promql
# CPU usage
rate(process_cpu_seconds_total[5m])

# Memory usage
process_resident_memory_bytes

# Request rate
rate(http_requests_total[5m])
```

### Grafana

Acesse: `http://seu-servidor:3001`
- User: `admin`
- Pass: (definido em GRAFANA_PASSWORD)

Dashboards incluídos:
- System Metrics
- PostgreSQL Stats
- Redis Stats
- Application Metrics

---

## 💾 Backup e Recovery

### Backup

Agende `pg_dump` (ou snapshots de volume) com **cron**, systemd timer ou serviço gerido. Guarde artefactos fora do servidor de aplicação (ex.: bucket com política de retenção e encriptação).

```bash
# Exemplo manual (ajuste utilizador/host/base)
pg_dump -h localhost -U agroadb agroadb | gzip > "backup_$(date +%Y%m%d_%H%M).sql.gz"
```

### Restore

```bash
gunzip -c backup_YYYYMMDD_HHMM.sql.gz | psql -h localhost -U agroadb agroadb
```

---

## 🔍 Health Checks

### Endpoints

- Backend: `https://api.example.com/health` (ajuste ao seu domínio)
- Frontend: `https://app.example.com/health`

### Monitoramento Externo

Configure em serviços como:
- [UptimeRobot](https://uptimerobot.com)
- [Pingdom](https://pingdom.com)
- [StatusCake](https://statuscake.com)

---

## 🔄 Atualização

### Zero Downtime Update

```bash
# Pull latest
git pull origin main

# Build novas imagens
docker-compose build

# Rolling update
docker-compose up -d --no-deps backend
docker-compose up -d --no-deps frontend

# Verificar
docker-compose ps
```

### Rollback

```bash
# Voltar para commit anterior
git checkout HEAD~1

# Rebuild
docker-compose up -d --build
```

---

## 🛡️ Segurança

### Firewall

```bash
# Permitir apenas necessário
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### SSL/TLS

Renovação automática configurada!

Verificar:
```bash
certbot certificates
```

Renovar manualmente:
```bash
certbot renew
```

---

## 📝 Checklist de Deploy

- [ ] Servidor provisionado
- [ ] Docker instalado
- [ ] Domínio configurado (DNS)
- [ ] .env configurado com valores de produção
- [ ] SSL/TLS configurado
- [ ] Backups automáticos configurados
- [ ] Monitoramento ativo (Prometheus + Grafana)
- [ ] Logs centralizados
- [ ] Health checks configurados
- [ ] Firewall configurado
- [ ] Migrações executadas
- [ ] Primeiro superuser criado
- [ ] Smoke tests executados
- [ ] Documentação atualizada
- [ ] Equipe notificada

---

## 📞 Suporte

Problemas durante o deploy?

- 📧 Contacto de operações: configure o canal da sua equipa (não publique e-mails pessoais no Git)
- 💬 Slack: #deploy-support
- 📚 Docs: OpenAPI na sua API (`/docs` ou equivalente)

---

**Última atualização**: 05/02/2026
