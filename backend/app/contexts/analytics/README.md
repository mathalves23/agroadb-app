# Bounded context: Analytics & BI

## Estado actual

- Implementação em `app/analytics/*` (métricas, dashboards, relatórios, export DW).
- O router histórico `app/analytics/routes.py` usa **sessão SQLAlchemy síncrona** e prefixo `/api/analytics` — **não está montado** no `FastAPI` principal (`main.py`) para evitar mistura com a stack async de `/api/v1`.

## Direcção técnica

1. Introduzir serviços async alinhados a `AsyncSession` e `get_db` actual.
2. Expor sob `/api/v1/analytics/...` com contratos testados em `tests/contract/`.
3. Manter exportações e jobs pesados em workers quando necessário.

Ver também `docs/bounded-contexts/README.md`.
