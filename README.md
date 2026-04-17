# AgroADB

Aplicação **full-stack** para apoiar investigações patrimoniais no contexto do agronegócio brasileiro: consolida dados de **fontes públicas** (cadastros rurais, transparência, tribunais onde aplicável, APIs abertas, etc.) numa API **FastAPI** e numa interface **React** (TypeScript).

Este repositório é **público**. Não inclua nele chaves API, passwords, URLs internas, tokens ou dados pessoais reais. Use sempre variáveis de ambiente e ficheiros ignorados pelo Git (por exemplo `.env`, nunca commitado).

---

## Conteúdo do repositório

| Pasta | Descrição |
|--------|------------|
| `backend/` | API REST, autenticação JWT, serviços de integração, ML/utilitários |
| `frontend/` | SPA Vite + React, formulários, dashboards, exportações |
| `docs/dev/` | Notas técnicas para quem desenvolve |
| `docs/deploy/` | Orientações genéricas de deploy com Docker |
| `docs/MAPEAMENTO_APIS_GOV.md` | Referência de **APIs e fontes públicas** (sem credenciais) |
| `clients/` | Clientes de exemplo (Python / JS) para consumir a API **na sua instância** |
| `postman/` | Coleção Postman para testar endpoints localmente |

---

## Requisitos

- **Docker** e **Docker Compose** (caminho recomendado para alinhar com CI e produção), ou
- **Python 3.11+**, **Node.js 18+** e PostgreSQL (ou SQLite conforme configuração) para desenvolvimento manual.

---

## Início rápido com Docker

Na raiz do projeto:

```bash
cp .env.example .env
# Edite .env: segredos apenas aqui ou no ambiente do CI — nunca no Git.

make install          # dependências locais (opcional, útil para IDEs)
make dev-up           # sobe stack (ver docker-compose.yml)
```

Por omissão (ajuste no `docker-compose` se mudou):

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Documentação interativa da API: `http://localhost:8000/docs` (caminho pode variar conforme `app`)

Para parar:

```bash
make dev-down
```

Migrações de base de dados:

```bash
make migrate
```

---

## Desenvolvimento sem Docker

1. Configure `backend` (virtualenv, `pip install -r requirements.txt`, `.env` com `DATABASE_URL` coerente com async/sync esperado pelo projeto).
2. `alembic upgrade head` no diretório `backend/` se usar migrações Alembic.
3. `make backend-dev` e, noutro terminal, `make frontend-dev` (ou `uvicorn` / `npm run dev` equivalentes).

Consulte `docs/dev/02-ambiente-desenvolvimento.md` para detalhes e armadilhas comuns.

---

## Primeiro utilizador administrador

**Não** existem credenciais pré-definidas neste repositório.

- Pode registar um utilizador pela UI/API se o registo estiver ativo no seu ambiente, ou
- Criar um superutilizador com o script que lê **apenas** variáveis de ambiente:

```bash
export AGROADB_ADMIN_EMAIL='admin@example.org'
export AGROADB_ADMIN_PASSWORD='escolha-uma-senha-forte'
# opcional: AGROADB_ADMIN_USERNAME, AGROADB_ADMIN_FULL_NAME

docker-compose exec -e AGROADB_ADMIN_EMAIL -e AGROADB_ADMIN_PASSWORD \
  -e AGROADB_ADMIN_USERNAME -e AGROADB_ADMIN_FULL_NAME \
  backend python scripts/create_superuser.py
```

Sem Docker, execute o mesmo `python scripts/create_superuser.py` a partir de `backend/` com o ambiente e `PYTHONPATH` configurados como no resto do projeto.

---

## Testes e qualidade

```bash
# Frontend (na pasta frontend/)
npm run lint
npm run build
npm run test:ci

# Backend (na pasta backend/, com dependências de teste instaladas)
pytest
```

Os números exatos de testes mudam com o tempo; o objetivo é manter a suíte verde em pull requests.

---

## Integrações e “features”

O código inclui **conectores, scrapers e módulos opcionais** para várias fontes. O que estará disponível **na sua instalação** depende de:

- variáveis de ambiente e chaves que **você** configura fora do Git;
- limites legais e técnicos de cada fonte (termos de uso, cadastro, IP, etc.).

Trate o `README` como descrição de **arquitetura e intenção**, não como catálogo comercial com SLA ou cobertura garantida. Para mapeamento de endpoints públicos, veja `docs/MAPEAMENTO_APIS_GOV.md`.

---

## Clientes API (`clients/`)

Os pacotes em `clients/python-client` e `clients/js-client` servem como **SDK de referência** ou instalação em modo editable a partir deste repositório. Não assuma que exista um pacote publicado com o mesmo nome no npm/PyPI — verifique o `package.json` / `pyproject.toml` de cada cliente.

---

## Contribuir

1. Fork e branch a partir da política de branches do repositório (ex.: `develop`).
2. Alterações pequenas e bem testadas; sem segredos nos commits.
3. Pull request com descrição clara do problema e da solução.

---

## Licença

Ver ficheiro [LICENSE](LICENSE) na raiz (tipicamente MIT — confirme no próprio ficheiro).

---

## Segurança

Se encontrar uma vulnerabilidade, **não** abra issue pública com exploit: use o canal de segurança indicado pelo mantenedor do fork (por exemplo “Security advisories” no GitHub, se ativado).
