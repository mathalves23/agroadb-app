# Analytics & BI (legado síncrono)

## Onde está o código

- Implementação: `app/analytics/*` (métricas, relatórios, export DW).
- Router histórico: `app/analytics/routes.py` usa **sessão SQLAlchemy síncrona** e prefixo `/api/analytics` — **não está montado** no `FastAPI` principal (`main.py`) para não misturar com a stack async de `/api/v1`.

## Evolução

- Contexto delimitado e roadmap: [`docs/bounded-contexts/README.md`](../../../docs/bounded-contexts/README.md).
- Exposição alvo: `/api/v1/analytics/...` com contratos em `tests/contract/`.
