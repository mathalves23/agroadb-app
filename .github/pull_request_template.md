## Objetivo

Descreva de forma breve o problema ou a melhoria que este PR resolve.

## Alterações

- 
- 

## Como testar

1. 
2. 

## Checklist

- [ ] Backend afetado: `make backend-check` passou localmente.
- [ ] Frontend afetado: `make frontend-check` passou localmente.
- [ ] Lint, tipagem e build foram validados nas áreas alteradas.
- [ ] Há cobertura nova ou ajuste de testes para regras, fluxos ou regressões relevantes.
- [ ] Acessibilidade básica foi revisada nas jornadas alteradas:
  - foco visível
  - navegação por teclado
  - mensagens de erro/loading
- [ ] Impacto em offline/PWA foi avaliado:
  - conectividade
  - fila offline/sincronização
  - snapshots/service worker quando aplicável
- [ ] Impacto em telemetria/observabilidade foi avaliado:
  - logs
  - métricas
  - health/startup/bootstrap quando aplicável
- [ ] Não foram incluídos segredos, tokens nem dados pessoais reais.
- [ ] Backend: `black` e `isort` alinhados com `backend/pyproject.toml` (ou `pre-commit run --all-files`).
