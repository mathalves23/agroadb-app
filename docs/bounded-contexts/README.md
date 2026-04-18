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
| **Analytics & BI** | Métricas, relatórios, export DW (legado sync) | `app/analytics/*` — *router legacy não montado em `/api/v1`; evoluir para async antes de expor.* |
| **ML** | Risco, padrões, rede, export de grafo | `app/services/ml/`, `app/api/v1/endpoints/ml.py` |

## Redução de dívida técnica

1. **Integrações:** helpers em `integrations_helpers.py`; rotas particionadas em `integrations/` (`conecta`, `tribunais`, `biros_orgaos_notify`, `remainder`). Próximo passo: partir `remainder.py` por domínio (dados abertos, transparência, fiscalização…).
2. **Analytics:** introduzir camada de aplicação async e montar sob `/api/v1/analytics` com os mesmos contratos testados.
3. **Contratos:** ver `tests/contract/test_public_api_contract.py` e expandir a lista de rotas críticas.
