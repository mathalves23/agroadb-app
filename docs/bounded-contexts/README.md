# Bounded contexts — AgroADB

Mapa de contextos delimitados para reduzir acoplamento e orientar refactors e **testes de contrato** na API pública.

Para camadas alvo (API → services → domain), convenções de código e limitações do legado, veja também **[`docs/padroes-arquitetura-codigo.md`](../padroes-arquitetura-codigo.md)**.

| Contexto | Responsabilidade principal | Código de referência |
|----------|-----------------------------|----------------------|
| **Commercial & compliance** | Proposta B2B, LGPD, mensagens de conformidade | `app/contexts/commercial/`, `app/api/v1/endpoints/platform.py` |
| **Core domain** | Utilizadores, organizações, autenticação | `app/api/v1/endpoints/auth.py`, `users.py`, `domain/` |
| **Investigations** | Ciclo de vida das investigações e entidades | `app/api/v1/endpoints/investigations.py`, `services/investigation.py` |
| **Integrations (externas)** | Conecta, tribunais, birôs, APIs abertas | `app/api/v1/endpoints/integrations/` (pacote), `integrations_helpers.py`, `app/services/*` |
| **Legal & queries** | Orquestração de consultas legais e proxy | `app/api/v1/endpoints/legal_integration.py` |
| **Analytics & BI** | Métricas, relatórios, export DW | `app/analytics/*` (legado sync), `app/services/analytics_application.py`, `app/api/v1/endpoints/analytics.py` — *exposto em `/api/v1/analytics` (async sobre `run_sync`).* |
| **ML** | Risco, padrões, rede, export de grafo | `app/services/ml/`, `app/api/v1/endpoints/ml.py` |

## Redução de dívida técnica

1. **Integrações:** helpers em `integrations_helpers.py`; rotas particionadas em `integrations/` (`conecta`, `tribunais`, `biros_orgaos_notify`, `remainder_open_data`, `remainder_transparency`, `remainder_supervision`, `remainder_environment`).
2. **Analytics:** camada `analytics_application` + router `/api/v1/analytics` (contrato mínimo em testes de contrato; sumário executivo sem schema rígido).
3. **Contratos:** ver `tests/contract/test_public_api_contract.py` e expandir a lista de rotas críticas.
4. **Jurídico / PJe:** fluxos PJe + auditoria em `app/services/legal_pje_workflows.py`; persistência de consulta por `investigation_id` em integrações via `app/services/legal_query_audit.py` (migrar gradualmente `conecta` / `tribunais` se desejado).
5. **Enriquecimento:** dados `MOCK_DEMO` controlados por `ENABLE_INVESTIGATION_ENRICH_DEMO_SEED` + bloqueio em produção (`investigation_enrich_demo.py`).
