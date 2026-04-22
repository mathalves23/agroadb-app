# Arquitetura limpa e código moderno — AgroADB

Este documento define **o que significa “arquitetura limpa” neste repositório** e como evoluir sem exigir um rewrite total de imediato. O objetivo é **fronteiras claras**, **dependências num só sentido** e **ferramentas automáticas** onde fizer sentido.

## Princípios (resumo)

1. **Dependências para dentro:** camadas externas conhecem as internas; o inverso não (ex.: `domain` não importa `api`).
2. **Um motivo para mudar:** agrupar código por **caso de uso / contexto** (ver `docs/bounded-contexts/README.md`), não só por tipo de ficheiro.
3. **Contratos explícitos:** schemas Pydantic na fronteira HTTP; tipos TypeScript nas fronteiras da UI.
4. **Efeitos colaterais na borda:** I/O (HTTP, DB, fila, disco) em adaptadores; regra de negócio preferencialmente testável sem rede.

## Backend (FastAPI)

| Camada | Pasta / módulo | Responsabilidade |
|--------|----------------|------------------|
| **Entrega HTTP** | `app/api/v1/endpoints/`, `deps.py` | Rotas, status HTTP, validação de entrada, orquestração fina |
| **Caso de uso / aplicação** | `app/services/` | Regras, transações, coordenação entre repositórios e integrações |
| **Domínio** | `app/domain/` | Entidades e invariantes (sem FastAPI) |
| **Persistência** | `app/repositories/` | Acesso a dados; queries encapsuladas |
| **Infra transversal** | `app/core/` | Config, segurança, DB session, métricas |
| **Contextos delimitados** | `app/contexts/*` | Texto, políticas e código que pertencem a um subdomínio (ex.: comercial) |

**Regras práticas**

- Endpoints **não** devem acumular lógica de negócio nem SQL complexo; delegar a **services** + **repositories**.
- Novos endpoints públicos devem ter cobertura em **testes de contrato** quando expuserem contrato estável (`tests/contract/`).
- Workers Celery tratam-se como **adaptadores de processamento assíncrono**; o núcleo da tarefa deve reutilizar services quando possível.

**Formatação e estilo Python**

- `black` + `isort` (perfis em `backend/pyproject.toml`).
- CI mantém `flake8` com regras críticas (E9/F63/F7/F82); alargar select gradualmente, não de uma vez.

## Frontend (React + Vite)

| Camada | Pasta | Responsabilidade |
|--------|-------|------------------|
| **Páginas** | `src/pages/` | Rotas, composição, estado de página |
| **Componentes** | `src/components/` | UI reutilizável, acessível |
| **Dados remotos** | `src/services/` | Chamadas HTTP, mapeamento DTO |
| **Infra cliente** | `src/lib/` | Axios, utilitários, eventos cross-cutting |
| **Estado global mínimo** | `src/stores/` | Sessão / preferências |

**Regras práticas**

- Páginas **não** importam outras páginas.
- Lógica de API concentrada em **services**; `axios` configurado em `lib/axios.ts`.
- Preferir **componentes pequenos** e listas de dependências de hooks corretas (avisos ESLint tratados por ficheiro ao refatorar).
- Páginas grandes devem ser quebradas em cinco tipos de módulo, sempre que o tamanho ou acoplamento crescer:
  - **composição visual** na própria página;
  - **hooks de dados** em `src/pages/<contexto>/use*.ts`;
  - **regras puras** em `analysis.ts`, `summary.ts`, `utils.ts`;
  - **componentes de seção/aba** em `src/pages/<contexto>/`;
  - **efeitos transversais** em `src/services/` ou `src/lib/`.
- Componentes visuais não devem fazer `fetch`/`axios` direto; chamadas remotas ficam em `services/` e coordenação com browser state em hooks dedicados.
- Estado compartilhado do app shell deve privilegiar `hooks + services + eventos` antes de crescer a store global.
- Recursos de resiliência como PWA, offline queue, snapshots, conectividade e sessão devem ser tratados como **infra cliente**, não espalhados por páginas.

## Convenções por tipo de artefacto

### Páginas

- Arquivos de rota em `src/pages/`.
- Páginas devem orquestrar layout, estado derivado e navegação, mas evitar regras longas e mutações inline.
- Quando uma página passar de um único fluxo claro, extrair para pasta própria com `hook + componentes + utilitários`.

### Hooks

- Hooks de domínio e de UI devem ficar próximos do contexto (`src/hooks/` para transversais, `src/pages/<contexto>/` para específicos).
- Hooks devem expor estado e ações; detalhes de transporte, cache e side effects ficam encapsulados.
- Hooks com temporizadores, listeners globais ou browser APIs precisam de limpeza explícita (`removeEventListener`, `clearInterval`, etc.).

### Services

- Todo acesso HTTP parte de `src/services/` ou `backend/app/services/`.
- Services devem ser o ponto único para chamadas remotas, retries, sincronização offline e mapeamento DTO.
- Componentes e páginas não devem reconstruir URLs, headers de autenticação ou lógica de fallback já existente.

### Schemas e contratos

- Backend: schemas Pydantic ficam na fronteira HTTP e models de domínio ficam desacoplados de FastAPI.
- Frontend: tipos de API em `src/types/` e utilitários puros recebem tipos explícitos; evitar `any` novo sem justificativa.
- Mudanças de contrato estável devem vir com teste de contrato, smoke ou teste de integração equivalente.

### Testes

- Testes unitários cobrem utilitários, hooks e componentes com regra relevante.
- Testes de integração cobrem páginas grandes, fluxos críticos e side effects entre camadas.
- E2E cobrem jornadas de valor: autenticação, navegação principal, PWA/offline, resiliência e regressões visíveis.
- Para frontend, qualquer mudança em app shell, sessão, PWA, conectividade ou offline queue deve vir com teste direcionado.
- Para backend, alterações em startup/bootstrap, segurança, contrato público ou integrações devem ampliar cobertura correspondente.

### Bootstrap e startup (backend)

- `app/main.py` deve permanecer como entrypoint fino: app factory, middlewares, routers e health endpoints.
- Qualquer side effect de startup deve ir para `app/bootstrap.py` ou módulos equivalentes, com flags de ambiente e testes dedicados.
- Workers, fila, telemetria e métricas devem poder ser habilitados/desabilitados sem quebrar o boot HTTP.

## Fluxo de mudança recomendado

1. Alterar primeiro o artefacto mais interno possível: utilitário, service ou hook.
2. Subir a mudança para página/componente apenas depois de a regra estar isolada.
3. Validar impacto em offline/PWA, acessibilidade, telemetria e cobertura antes de considerar a entrega pronta.
4. Registrar decisões maiores em ADR quando a mudança criar uma convenção nova ou tradeoff duradouro.

**ESLint** (`.eslintrc.cjs`): regras alinhadas a TypeScript moderno; `any` só como aviso até a suíte de tipos estabilizar.

## O que “garantido” significa na prática

- **Garantido:** convenções escritas, CI, formatação base e fronteiras documentadas.
- **Em evolução:** ficheiros legados grandes (ex.: alguns endpoints e páginas) devem ser tocados **só** com refactors pequenos e testados, não “big bang”.

## Próximos passos recomendados (prioridade)

1. Continuar a partir `integrations/remainder.py` em sub-routers por domínio (dados abertos, transparência, etc.).
2. Extrair casos de uso repetidos de `investigations` / `legal_integration` para services dedicados.
3. No frontend, alinhar páginas restantes aos padrões de loading/empty state já usados em Dashboard/Investigações.

Para decisões de desenho, use ADRs em `docs/adr/`.
