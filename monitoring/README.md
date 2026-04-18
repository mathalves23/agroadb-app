# Observabilidade AgroADB

Este guia descreve **métricas Prometheus** (`/metrics` na API e no worker Celery), **Grafana**, **Alertmanager** (Slack, PagerDuty, e-mail), **Grafana Tempo** (OTLP) e **tracing OpenTelemetry**.

## Arranque rápido (Docker Compose, perfil `obs`)

1. Opcional: no **directório do projecto**, crie ou edite o ficheiro `.env` (Compose usa-o para substituição `${VAR}` — ver `.env.example` na raiz):

```bash
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4318/v1/traces
# SLACK_WEBHOOK_URL — URL completo do Incoming Webhook do Slack (apenas no .env local).
# PAGERDUTY_ROUTING_KEY — chave de integração Events API v2 (opcional).
AM_EMAIL_TO=oncall@example.com
AM_SMTP_SMARTHOST=smtp.example.com:587
AM_SMTP_FROM=alertmanager@example.com

# Grafana (já não usa admin/admin por defeito)
GRAFANA_ADMIN_USER=grafana-admin
# GRAFANA_ADMIN_PASSWORD_FILE=./monitoring/secrets/grafana_admin_password
GRAFANA_ROOT_URL=http://localhost:3000
# GRAFANA_SECRET_KEY=…
```

2. Suba a stack com observabilidade:

```bash
docker compose --profile obs up -d
```

3. URLs úteis:

| Serviço | URL |
|---------|-----|
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (utilizador `GRAFANA_ADMIN_USER`, palavra-passe via ficheiro — ver abaixo) |
| Postgres exporter | http://localhost:9187/metrics |
| Redis exporter | http://localhost:9121/metrics |
| Alertmanager | http://localhost:9093 |
| Tempo (query HTTP) | http://localhost:3200 |
| OTLP HTTP (traces) | `http://tempo:4318` (rede Docker) / `http://localhost:4318` (host) |

O perfil `obs` inclui **prometheus**, **grafana**, **alertmanager**, **tempo**, **postgres-exporter** e **redis-exporter**, além de **backend** + **celery-worker**. O worker expõe métricas em `CELERY_METRICS_PORT=9464`.

### Rede Docker

Todos estes serviços estão na rede **`agroadb_net`** (`docker-compose.yml`), para o Prometheus resolver `backend`, `celery-worker`, `postgres-exporter` e `redis-exporter` por nome de serviço.

### Grafana — segredos e SSO

- **Palavra-passe do admin**: montada com `GF_SECURITY_ADMIN_PASSWORD__FILE` a partir de `GRAFANA_ADMIN_PASSWORD_FILE` (por omissão `./monitoring/secrets/grafana_admin_password.dev`, apenas para desenvolvimento). Em produção, crie `monitoring/secrets/grafana_admin_password` (fora do Git) e aponte `GRAFANA_ADMIN_PASSWORD_FILE` para esse caminho — ver `monitoring/secrets/README.md`.
- **Utilizador admin inicial**: `GRAFANA_ADMIN_USER` (por omissão `grafana-admin`).
- **URL pública**: `GRAFANA_ROOT_URL` (cookies e links OAuth).
- **Chave de assinatura**: `GF_SECURITY_SECRET_KEY` via `GRAFANA_SECRET_KEY` (altere em produção).
- **SSO / OIDC**: exemplo de variáveis em `monitoring/grafana/SSO.example.env` e [documentação Grafana](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/).

*O Grafana OSS não provisiona utilizadores locais por ficheiro como o LDAP; para equipas use OAuth/OIDC ou LDAP.*

## Métricas principais

| Origem | Endpoint / porta | Conteúdo |
|--------|------------------|----------|
| API FastAPI | `GET /metrics` | `http_requests_total`, histogramas de latência, gauges de filas/circuitos |
| Worker Celery | `http://celery-worker:9464/metrics` | `celery_task_runs_total`, `celery_task_duration_seconds` |
| Postgres (exporter) | `http://postgres-exporter:9187/metrics` | Métricas `pg_*` (Prometheus community exporter) |
| Redis (exporter) | `http://redis-exporter:9121/metrics` | Métricas `redis_*` |
| API (gauges) | idem | `agroadb_queue_tasks`, `agroadb_scraper_circuit_breaker_open`, `agroadb_external_circuit_breaker_open`, … |

As gauges de fila/circuito são actualizadas **periodicamente** (15 s) quando `PROMETHEUS_ENABLED=true` e a API liga ao Redis.

## Grafana

- Datasource **Prometheus** (UID `agroadb-prom`).
- Datasource **Tempo** (UID `agroadb-tempo`) — explore traces após activar OTEL.
- Dashboard **AgroADB — Operações** (pasta *AgroADB*).

## Alertmanager e receptores

- Configuração: `monitoring/alertmanager/alertmanager.yml` com **`--config.expand-env=true`**.
- **Crítico** (`severity=critical`): e-mail + **PagerDuty** (`PAGERDUTY_ROUTING_KEY`).
- **Aviso / info** (`severity=warning|info`): e-mail + **Slack** (`SLACK_WEBHOOK_URL`).
- **E-mail**: `AM_EMAIL_TO`, relay `AM_SMTP_SMARTHOST`, remetente `AM_SMTP_FROM`. Autenticação SMTP opcional (editar o ficheiro e descomentar `smtp_auth_*` se necessário).

Valores por omissão no `docker-compose.yml` evitam chaves vazias inválidas; **substitua** `SLACK_WEBHOOK_URL` e `PAGERDUTY_ROUTING_KEY` por integrações reais.

O Prometheus envia alertas para `alertmanager:9093` (`monitoring/prometheus.yml`).

## Regras Prometheus e validação

Ficheiro: `monitoring/alerts/agroadb.yml` (falhas/latência Celery, circuitos, profundidade de fila; thresholds calibrados para menos ruído).

Validação local:

```bash
make promtool-check
```

Equivalente com Docker:

```bash
docker run --rm -v "$(pwd)/monitoring/alerts:/rules:ro" prom/prometheus:v2.53.3 promtool check rules /rules/agroadb.yml
```

## Tracing (OpenTelemetry) com Tempo (staging local)

No **docker-compose**, o **backend** usa `OTEL_SERVICE_NAME=agroadb-api` e o **celery-worker** `OTEL_SERVICE_NAME=agroadb-celery`. Ambos leem `OTEL_ENABLED` e `OTEL_EXPORTER_OTLP_ENDPOINT` do `.env` do projecto.

Com o exemplo acima (`OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4318/v1/traces`), os spans OTLP HTTP chegam ao **Tempo** (`monitoring/tempo/tempo.yaml`).

A API instrumenta o FastAPI (exclui `/health` e `/metrics`). Celery: `instrument_celery()` em `app/core/telemetry.py`.

| Variável | Descrição |
|----------|-----------|
| `OTEL_ENABLED` | `true` para activar |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | URL completa OTLP HTTP, ex. `http://tempo:4318/v1/traces` |
| `ENVIRONMENT` | Atributo `deployment.environment` no recurso OTEL |

**Nota:** sem o perfil `obs`, o hostname `tempo` não existe; mantenha `OTEL_ENABLED=false` ou não defina o endpoint.

## Ficheiros

| Caminho | Função |
|---------|--------|
| `monitoring/prometheus.yml` | Scrape + Alertmanager |
| `monitoring/alerts/agroadb.yml` | Regras de alerta |
| `monitoring/alertmanager/alertmanager.yml` | Rotas e receptores |
| `monitoring/tempo/tempo.yaml` | Tempo (OTLP 4317/4318) |
| `monitoring/grafana/provisioning/` | Datasources e dashboards |
| `monitoring/grafana/dashboards/agroadb-operations.json` | Dashboard base |
| `monitoring/env.observability.example` | Variáveis de referência (cópia opcional) |
| `monitoring/secrets/grafana_admin_password.dev` | Palavra-passe Grafana só para dev (versionada) |
| `monitoring/grafana/SSO.example.env` | Variáveis OAuth/OIDC de exemplo |
