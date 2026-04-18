# Contribuir para o AgroADB

Obrigado pelo interesse. Este repositório é público: **não** envie chaves API, passwords, URLs internas nem dados pessoais reais.

## Desenvolvimento

- **Stack recomendada**: ver `README.md` (Docker Compose alinha com o CI).
- **Backend** (`backend/`): Python 3.11+, `pytest`, formatação com **Black** e **isort** (perfil em `backend/pyproject.toml`).
- **Frontend** (`frontend/`): Node 20+, `npm run lint`, `npm run type-check`, `npm run build`.

## Qualidade antes de abrir um PR

Na raiz do repositório (opcional mas recomendado):

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Ou manualmente:

```bash
cd backend && black app tests alembic && isort app tests alembic --profile black
cd ../frontend && npm run lint && npm run type-check && npm run test:ci
```

O workflow **CI** em `.github/workflows/ci.yml` valida lint, formatação, testes e build.

## Pull requests

Use o modelo que aparece ao criar o PR. PRs devem ser pequenos e focados, com descrição clara e passos de teste.
