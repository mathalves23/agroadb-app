# Primeiro deploy — Kubernetes (K8s)

Visão genérica: cada organização usa **Ingress**, **Secrets** e **operators** diferentes; abaixo está o fluxo mínimo comum.

## 1. Pré-requisitos

- Cluster K8s ≥ 1.26 (recomendado).
- `kubectl` configurado para o contexto certo.
- Imagem da API publicada num registry (ex.: `ghcr.io/org/agroadb-api:1.0.0`).

## 2. Secrets

Nunca commite segredos. Crie um `Secret` (ou use External Secrets / Sealed Secrets):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: agroadb-api-secret
type: Opaque
stringData:
  SECRET_KEY: "substituir-pelo-menos-32-caracteres-aleatorios"
  DATABASE_URL: "postgresql+asyncpg://user:pass@postgres:5432/agroadb"
  REDIS_URL: "redis://redis:6379/0"
  ENCRYPTION_KEY: "base64-32-bytes"
```

Aplicar: `kubectl apply -f secret.yaml -n agroadb`

## 3. Deploy da API

- **Deployment:** réplicas ≥2 para HA; `readinessProbe` HTTP em `/health`; `livenessProbe` igual ou mais brando.
- **Service:** `ClusterIP` ou `LoadBalancer` conforme o cloud.
- **Recursos:** CPU/memória conforme carga (workers scraping podem precisar de réplicas separadas).

Variáveis opcionais ML (como no Docker):

- `RISK_CALIBRATION_PATH` — montar `ConfigMap` ou volume só-leitura com o JSON.
- `RISK_SHAP_NEUTRAL_BASELINE`

## 4. Postgres e Redis

- **Produção:** preferir serviços geridos (RDS, Cloud SQL, ElastiCache) em vez de Pods sem operador.
- Se usar Helm charts oficiais, configure `persistence.enabled=true` e backups.

## 5. Ingress / TLS

- `Ingress` com cert-manager (`ClusterIssuer` Let's Encrypt ou certificado interno).
- CORS: restrinja `CORS_ORIGINS` ao domínio do frontend.

## 6. Workers Celery

Deployment separado com o mesmo `image` da API, `command` apontando para o worker Celery, mesmas env vars de `DATABASE_URL` / `REDIS_URL` / broker.

## 7. Observabilidade

- Scraping Prometheus do path `/metrics` (se activo).
- OTLP: configurar `OTEL_EXPORTER_OTLP_ENDPOINT` e sidecar/collector conforme a stack (Grafana Agent, OpenTelemetry Collector).

## 8. Primeiro rollout

```bash
kubectl apply -k overlays/staging   # exemplo kustomize
kubectl rollout status deployment/agroadb-api -n agroadb
```

---

Referência local rápida: [primeiro-deploy-docker.md](./primeiro-deploy-docker.md).
