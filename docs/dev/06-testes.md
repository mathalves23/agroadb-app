# 6. Testes - AgroADB

## Visão geral

O AgroADB usa três camadas complementares de validação:

- **backend**: pytest para serviços, contrato público, segurança, observabilidade e bootstrap;
- **frontend**: Jest + Testing Library para componentes, hooks, utilitários e páginas;
- **E2E**: Playwright para fluxos críticos, PWA/offline e resiliência do app shell.

Os números exatos de testes variam ao longo do tempo; a referência operacional é sempre o CI e os comandos abaixo.

## Comandos oficiais

### Backend

```bash
make backend-check
```

Esse comando roda:
- lint crítico Python;
- subset de testes alinhado ao CI;
- cobertura XML;
- verificação de cobertura crítica por arquivo.

Execução manual equivalente:

```bash
cd backend
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -p pytest_asyncio.plugin tests/ -q
```

### Frontend

```bash
make frontend-check
```

Esse comando roda:
- `npm run lint`
- `npm run type-check`
- `npm run check-product-manual`
- `npm run build`
- `npm run test:ci`
- `npm run coverage:critical`

### E2E

```bash
cd frontend
npm run test:e2e:ci
```

## Onde colocar cada tipo de teste

### Backend

- `tests/services/`: regras de negócio e serviços de aplicação
- `tests/contract/`: endpoints e contratos públicos estáveis
- `tests/test_bootstrap.py`, `tests/test_main_application.py`: startup, app factory e side effects de infraestrutura
- `tests/test_security.py`, `tests/test_auth.py`: autenticação, sessão e segurança

### Frontend

- `src/tests/lib/`: utilitários puros e infraestrutura cliente
- `src/tests/hooks/`: hooks com timers, browser APIs, sessão, PWA e conectividade
- `src/tests/components/`: componentes compartilhados e app shell
- `src/tests/pages/`: páginas e fluxos por rota
- `src/tests/integration/`: jornadas maiores que cruzam várias camadas

### E2E

- `frontend/e2e/critical-flows.spec.ts`: fluxos centrais de navegação/autenticação
- `frontend/e2e/pwa-offline-resilience.spec.ts`: PWA, offline, reconexão, snapshots e sessão persistida

## Cobertura mínima contínua

O projeto mantém dois níveis de controlo:

### 1. Threshold global da suíte frontend

Definido no `package.json` do frontend para evitar regressões muito grandes na base como um todo.

### 2. Threshold por área crítica

Aplicado automaticamente no CI e localmente pelos scripts:

- frontend: `frontend/scripts/check-critical-coverage.mjs`
- backend: `backend/scripts/check_critical_coverage.py`

Arquivos críticos atualmente monitorados:

### Frontend

- `src/components/ConnectionStatus.tsx`
- `src/components/GlobalCommandPalette.tsx`
- `src/hooks/useSessionGuard.ts`
- `src/hooks/usePwaUpdatePrompt.ts`
- `src/lib/offlineQueue.ts`

### Backend

- `app/bootstrap.py`
- `app/main.py`
- `app/core/security.py`

## Regras práticas

- Mudou regra de negócio: adicionar ou ajustar teste unitário/integrado.
- Mudou shell, sessão, PWA, offline ou conectividade: adicionar teste focado no componente/hook e rever E2E quando necessário.
- Mudou startup, workers, fila, telemetria ou health checks: ampliar teste de bootstrap/app factory.
- Evitar testes frágeis dependentes de detalhes de implementação quando um comportamento observável resolve melhor.

## Critérios mínimos antes de subir PR

- Comandos oficiais passaram localmente nas áreas afetadas.
- Cobertura crítica continua verde.
- Não houve regressão de acessibilidade básica nos fluxos alterados.
- Impacto em offline/PWA e telemetria foi avaliado quando aplicável.
