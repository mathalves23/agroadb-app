# 9. Governança e qualidade contínua

## Objetivo

Sustentar a qualidade do AgroADB no médio prazo com convenções simples, validações repetíveis e pontos de controlo visíveis no dia a dia.

## Fonte de verdade

- Padrões de arquitetura e convenções: `docs/padroes-arquitetura-codigo.md`
- Auditoria e roadmap técnico: `docs/reports/application-audit-2026-04-22.md`
- Checklist de PR: `.github/pull_request_template.md`

## Gate mínimo de entrega

### Backend

```bash
make backend-check
```

Esse alvo valida:
- lint crítico (`flake8`, `black --check`, `isort --check-only`);
- subset de testes alinhado ao CI;
- cobertura crítica mínima em:
  - `app/bootstrap.py`
  - `app/main.py`
  - `app/core/security.py`

### Frontend

```bash
make frontend-check
```

Esse alvo valida:
- `npm run lint`
- `npm run type-check`
- `npm run check-product-manual`
- `npm run build`
- `npm run test:ci`
- `npm run coverage:critical`

## Cobertura crítica monitorada

Além do threshold global baixo da suíte, o repositório agora vigia áreas sensíveis com mínimos por arquivo.

### Frontend

Verificação em `frontend/scripts/check-critical-coverage.mjs`.

Arquivos monitorados:
- `src/components/ConnectionStatus.tsx`
- `src/components/GlobalCommandPalette.tsx`
- `src/hooks/useSessionGuard.ts`
- `src/hooks/usePwaUpdatePrompt.ts`
- `src/lib/offlineQueue.ts`

### Backend

Verificação em `backend/scripts/check_critical_coverage.py`.

Arquivos monitorados:
- `app/bootstrap.py`
- `app/main.py`
- `app/core/security.py`

## O que deve ser revalidado sempre

- Mudanças em shell, navegação, conectividade, PWA, fila offline ou sessão:
  - validar UX básica;
  - validar acessibilidade mínima;
  - validar impacto em testes e cobertura crítica.
- Mudanças em bootstrap, telemetria, workers, fila ou segurança:
  - validar startup com e sem integrações externas;
  - validar flags de ambiente;
  - validar observabilidade mínima (`/health`, métricas, logs).

## Sinais de alerta para refactor obrigatório

- Página ou endpoint acumulando composição, regra, transporte e side effect no mesmo arquivo.
- Duplicação de chamadas HTTP, headers ou retries fora de `services/`.
- Lógica offline/PWA/sessão aparecendo em componentes de domínio.
- Testes novos que exigem mocks excessivos porque o acoplamento cresceu demais.

## Ritmo recomendado

- A cada PR: cumprir checklist e gates mínimos.
- A cada semana: observar regressões de cobertura crítica e warnings novos no CI.
- A cada decisão estrutural maior: registrar ADR curta.
