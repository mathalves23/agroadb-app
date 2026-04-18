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

**ESLint** (`.eslintrc.cjs`): regras alinhadas a TypeScript moderno; `any` só como aviso até a suíte de tipos estabilizar.

## O que “garantido” significa na prática

- **Garantido:** convenções escritas, CI, formatação base e fronteiras documentadas.
- **Em evolução:** ficheiros legados grandes (ex.: alguns endpoints e páginas) devem ser tocados **só** com refactors pequenos e testados, não “big bang”.

## Próximos passos recomendados (prioridade)

1. Dividir `integrations.py` em sub-routers por família de integração (já referido em bounded contexts).
2. Extrair casos de uso repetidos de `investigations` / `legal_integration` para services dedicados.
3. No frontend, alinhar páginas restantes aos padrões de loading/empty state já usados em Dashboard/Investigações.

Para decisões de desenho, use ADRs em `docs/adr/`.
