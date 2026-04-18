# Observabilidade AgroADB

Este guia descreve **métricas Prometheus** (`/metrics` na API e no worker Celery), **dashboards Grafana**, **alertas** e **tracing OpenTelemetry** em produção.

## Arranque rápido (Docker Compose)

1. Suba a stack habitual e active o perfil de observabilidade:

```bash
docker compose --profile obs up -d
```

2. **Prometheus**: http://localhost:9090  
3. **Grafana**: http://localhost:3000 (utilizador `admin` / palavra-passe `admin` — altere em produção)

O perfil `obs` inclui `prometheus` e `grafana`. O worker Celery expõe métricas em `CELERY_METRICS_PORT=9464` (mapeado para o host).

## Métricas principais

| Origem | Endpoint / porta | Conteúdo |
|--------|------------------|----------|
| API FastAPI | `GET /metrics` | `http_requests_total`, histogramas de latência (`prometheus-fastapi-instrumentator`), gauges de filas/circuitos |
| Worker Celery | `http://celery-worker:9464/metrics` | `celery_task_runs_total`, `celery_task_duration_seconds` |
| API (gauges) | idem | `agroadb_queue_tasks`, `agroadb_scraper_circuit_breaker_open`, `agroadb_external_circuit_breaker_open`, `agroadb_scraper_circuit_breaker_opened_total` |

As gauges de fila e circuitos são actualizadas **periodicamente** (15 s) quando `PROMETHEUS_ENABLED=true` e a API consegue ligar ao Redis.

## Grafana

- Datasource **Prometheus** (UID `agroadb-prom`) é provisionada automaticamente.
- Dashboard **AgroADB — Operações** em *AgroADB* → painéis HTTP, filas Redis, circuit breakers e Celery.

## Alertas Prometheus

Ficheiro: `monitoring/alerts/agroadb.yml` (montado em `/etc/prometheus/alerts/`). Inclui regras para:

- falhas Celery;
- latência Celery elevada;
- circuit breaker de scrapers (Redis) aberto;
- circuit breaker HTTP (serviços externos) aberto;
- profundidade de fila elevada.

Ligue um **Alertmanager** e actualize `alerting.alertmanagers` em `prometheus.yml` para encaminhar notificações (Slack, PagerDuty, e-mail).

## Tracing (OpenTelemetry) em produção

Defina no ambiente da **API** e dos **workers**:

| Variável | Exemplo | Descrição |
|----------|---------|-----------|
| `OTEL_ENABLED` | `true` | Activa tracing |
| `OTEL_SERVICE_NAME` | `agroadb-api` / `agroadb-celery` | Nome do serviço no trace |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `https://otel-collector.example.com/v1/traces` | Endpoint OTLP HTTP (Jaeger, Tempo, Datadog, etc.) |
| `ENVIRONMENT` | `production` | Atributo `deployment.environment` |

A API instrumenta o FastAPI (exclui `/health` e `/metrics`). Os workers Celery são instrumentados em `instrument_celery()` quando `OTEL_ENABLED=true`.

Para **Grafana Tempo** auto-hospedado, pode expor OTLP na porta 4318 e apontar `OTEL_EXPORTER_OTLP_ENDPOINT` para esse URL.

## Ficheiros

- `monitoring/prometheus.yml` — scrape da API e do Celery  
- `monitoring/alerts/agroadb.yml` — regras de alerta  
- `monitoring/grafana/provisioning/` — datasource e pastas de dashboards  
- `monitoring/grafana/dashboards/agroadb-operations.json` — dashboard base  
