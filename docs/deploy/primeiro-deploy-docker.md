# Primeiro deploy — Docker (Compose)

Este guia assume máquina Linux ou macOS com **Docker** e **Docker Compose** v2.

## 1. Pré-requisitos

- Variáveis mínimas: `SECRET_KEY` (≥32 caracteres), `DATABASE_URL`, `REDIS_URL`, `ENCRYPTION_KEY` (32 bytes base64 se usar cifra de dados).
- Ficheiros: `docker-compose.yml` (raiz ou `docker-compose.production.yml`).

## 2. Configurar ambiente

```bash
cp backend/.env.example backend/.env   # se existir modelo
# Editar SECRET_KEY, DATABASE_URL, REDIS_URL, etc.
```

Opcional ML:

- `RISK_CALIBRATION_PATH` — caminho absoluto para JSON de calibração (ver `backend/app/services/ml/data/default_risk_calibration.json`).
- `RISK_SHAP_NEUTRAL_BASELINE` — default `50` (baseline dos valores SHAP aditivos).

## 3. Subir stack

```bash
docker compose up -d --build
```

Aguarde Postgres/Redis saudáveis. A API expõe normalmente a porta **8000** (confirmar no compose).

## 4. Migrações e smoke

```bash
docker compose exec api alembic upgrade head   # se o serviço se chamar assim
curl -sSf http://localhost:8000/health
```

## 5. Frontend (opcional no mesmo host)

Build estático ou serviço `frontend` no compose; definir `VITE_API_URL` apontando para a API.

## 6. Observabilidade

- Prometheus: `PROMETHEUS_ENABLED`, rota `/metrics`.
- OpenTelemetry: `OTEL_ENABLED`, `OTEL_EXPORTER_OTLP_ENDPOINT`.

## Rollback

```bash
docker compose down
docker compose up -d --build <imagem_anterior>
```

---

Para orquestração em cluster, veja [primeiro-deploy-kubernetes.md](./primeiro-deploy-kubernetes.md).
