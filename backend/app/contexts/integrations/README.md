# Bounded context: Integrações externas

## Estado actual

- Rotas HTTP: `app/api/v1/endpoints/integrations.py` (ficheiro grande).
- **Helpers extraídos:** `integrations_helpers.py` (`result_count`, `conecta_items`, resposta padronizada, detecção de credenciais em falta).

## Próximo refactor recomendado

1. Partir `integrations.py` em sub-routers por família: `conecta_router`, `tribunais_router`, `birôs_router`, `dados_abertos_router`, `notificacoes_router`.
2. Agregar com `APIRouter.include_router` mantendo o prefixo `/integrations`.
3. Para cada sub-router, adicionar entradas em `tests/contract/test_public_api_contract.py` para os `POST` críticos (contratos de input/output mínimos).

Isto reduz conflitos de merge e acelera testes de contrato focados.
