# 2. Configuração do Ambiente de Desenvolvimento

## 🎯 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

### Obrigatórios

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **Redis 7+** - [Download](https://redis.io/download)
- **Git** - [Download](https://git-scm.com/downloads)

### Recomendados

- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)
- **VS Code** ou **PyCharm** - IDEs recomendadas
- **Postman** ou **Insomnia** - Para testar APIs

---

## 📥 Instalação Local

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/agroadb.git
cd agroadb
```

### 2. Configure o Backend

```bash
# Entre na pasta do backend
cd backend

# Crie um ambiente virtual Python
python -m venv venv

# Ative o ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Volte para a raiz
cd ..
```

**Alinhar com o CI (GitHub Actions):** o job de backend instala exatamente `backend/requirements.txt`, corre `flake8` com o mesmo recorte de regras e executa o **mesmo subconjunto** de `pytest` que `make test` na raiz do repositório. Esse subconjunto assume **PostgreSQL** e **Redis** acessíveis quando a aplicação ou os testes de dependem (ver variáveis `DATABASE_URL` e `REDIS_URL` no ficheiro `.github/workflows/ci.yml`). Para reproduzir erros só observados no CI, use as mesmas URLs e segredos de teste nesse workflow ou suba serviços Docker nas mesmas portas.

Para **remoto Git, branch protection e segredos opcionais** (`CI_DATABASE_URL`, `CODECOV_TOKEN`, etc.), consulte também [github-setup.md](./github-setup.md).

### 3. Configure o Frontend

```bash
# Entre na pasta do frontend
cd frontend

# Instale as dependências
npm install

# Volte para a raiz
cd ..
```

### 4. Configure o Banco de Dados

```bash
# Crie o banco de dados PostgreSQL
createdb agroadb

# OU via psql:
psql -U postgres
CREATE DATABASE agroadb;
\q
```

### 5. Configure as Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas configurações
nano .env  # ou seu editor preferido
```

**Exemplo de `.env`:**

```env
# ==================== DATABASE ====================
DATABASE_URL=postgresql+asyncpg://postgres:senha@localhost:5432/agroadb

# ==================== REDIS ====================
REDIS_URL=redis://localhost:6379/0

# ==================== SECURITY ====================
SECRET_KEY=sua-chave-secreta-aqui-min-32-caracteres
ENCRYPTION_KEY=chave-base64-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ==================== ENVIRONMENT ====================
ENVIRONMENT=development
DEBUG=True
FORCE_HTTPS=False

# ==================== CORS ====================
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# ==================== EXTERNAL APIs ====================
INCRA_API_KEY=sua-chave-incra
CAR_API_KEY=sua-chave-car
SERPAPI_KEY=sua-chave-serpapi
PJE_API_URL=https://api.pje.jus.br
PJE_API_KEY=sua-chave-pje

# ==================== EMAIL ====================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
EMAIL_FROM=noreply@agroadb.com

# ==================== S3 (Opcional) ====================
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=
AWS_REGION=us-east-1
```

### 6. Execute as Migrações do Banco

```bash
cd backend
alembic upgrade head
cd ..
```

### 7. Inicie os Serviços

**Backend** (Terminal 1):
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
```

**Redis** (Terminal 3):
```bash
redis-server
```

**Worker de Filas** (Terminal 4):
```bash
cd backend
source venv/bin/activate
python -m app.services.queue worker
```

### 8. Acesse a Aplicação

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🐳 Instalação com Docker (Recomendado)

### 1. Clone e Configure

```bash
git clone https://github.com/seu-usuario/agroadb.git
cd agroadb
cp .env.example .env
# Edite o .env conforme necessário
```

### 2. Inicie com Docker Compose

```bash
docker-compose -f docker-compose.production.yml up -d
```

Isso iniciará:
- PostgreSQL (porta 5432)
- Redis (porta 6379)
- Backend (porta 8000)
- Frontend (porta 80/443)
- Prometheus (porta 9090)
- Grafana (porta 3001)

### 3. Execute Migrações

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Criar Superusuário

```bash
docker-compose exec backend python -m app.cli create-superuser \
  --email admin@agroadb.com \
  --password SenhaForte123! \
  --full-name "Admin User"
```

---

## 🛠️ Configuração de IDE

### Visual Studio Code

#### Extensões Recomendadas

**Para Python:**
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Python Test Explorer
- autoDocstring

**Para TypeScript/React:**
- ESLint
- Prettier
- ES7+ React/Redux/React-Native snippets
- Auto Rename Tag
- Path Intellisense

**Geral:**
- GitLens
- Docker
- REST Client
- Thunder Client (teste de APIs)

#### settings.json (VS Code)

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.pylintEnabled": false,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.updateImportsOnFileMove.enabled": "always",
  
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

### PyCharm

1. **Abra o projeto**: File > Open > Selecione a pasta `agroadb`
2. **Configure o interpretador Python**:
   - File > Settings > Project > Python Interpreter
   - Add Interpreter > Existing environment
   - Selecione `backend/venv/bin/python`
3. **Configure o PostgreSQL**:
   - View > Tool Windows > Database
   - + > Data Source > PostgreSQL
   - Configure a conexão com suas credenciais

---

## 🧪 Executando Testes

### Backend

```bash
cd backend
source venv/bin/activate

# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=app --cov-report=html

# Teste específico
pytest tests/test_auth.py -v

# Watch mode (reexecuta ao salvar)
ptw tests/ -v
```

### Frontend

```bash
cd frontend

# Todos os testes
npm run test

# Com cobertura
npm run test:ci

# Watch mode
npm run test:watch

# Teste específico
npm test -- Controls.test.tsx
```

### Todos os testes (raiz)

Execute os alvos do `Makefile` e os comandos de `pytest` / `npm run test:ci` descritos no [README](../../README.md) em cada pasta (`backend/`, `frontend/`).

---

## 📚 Comandos Úteis

### Backend

```bash
# Criar nova migração
alembic revision --autogenerate -m "Descrição"

# Reverter última migração
alembic downgrade -1

# Ver status das migrações
alembic current

# Gerar chave secreta
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Iniciar em debug
uvicorn app.main:app --reload --log-level debug

# Rodar linter
flake8 app --max-line-length=127

# Formatar código
black app/
```

### Frontend

```bash
# Build de produção
npm run build

# Preview do build
npm run preview

# Lint e fix
npm run lint:fix

# Analisar bundle
npm run build -- --mode analyze

# Limpar cache
rm -rf node_modules/.vite
```

### Docker

```bash
# Ver logs
docker-compose logs -f backend

# Reiniciar serviço
docker-compose restart backend

# Entrar no container
docker-compose exec backend bash

# Rebuild
docker-compose build --no-cache

# Limpar tudo
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Problema: Backend não inicia

**Erro**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solução**:
```bash
# Verifique se o PostgreSQL está rodando
pg_isready

# Se não estiver, inicie:
# Linux/Mac:
sudo service postgresql start
# Windows:
net start postgresql-x64-15
```

### Problema: Frontend não conecta ao backend

**Erro**: `Network Error` ou `CORS Error`

**Solução**:
1. Verifique se o backend está rodando em http://localhost:8000
2. Verifique o CORS_ORIGINS no `.env`
3. Limpe o cache do navegador (Ctrl+Shift+Del)

### Problema: Redis connection failed

**Solução**:
```bash
# Verifique se o Redis está rodando
redis-cli ping
# Deve retornar: PONG

# Se não estiver, inicie:
redis-server

# Ou com Docker:
docker run -d -p 6379:6379 redis:7-alpine
```

### Problema: Migrações falham

**Erro**: `Target database is not up to date`

**Solução**:
```bash
# Reverta todas as migrações
alembic downgrade base

# Reaplique
alembic upgrade head

# Se ainda falhar, recrie o banco:
dropdb agroadb
createdb agroadb
alembic upgrade head
```

### Problema: Testes falham

**Erro**: `ImportError: No module named 'app'`

**Solução**:
```bash
# Certifique-se de estar no ambiente virtual
source backend/venv/bin/activate

# Reinstale as dependências
pip install -r backend/requirements.txt

# Execute da raiz do projeto backend
cd backend
pytest tests/
```

---

## 📞 Suporte

Se encontrar problemas:

1. **Verifique a documentação** completa
2. **Procure em Issues** do GitHub
3. **Entre em contato**:
   - Email: dev@agroadb.com
   - Slack: #dev-support
   - GitHub: Abra uma issue

---

## ✅ Checklist de Configuração

- [ ] Python 3.11+ instalado
- [ ] Node.js 18+ instalado
- [ ] PostgreSQL 15+ instalado e rodando
- [ ] Redis 7+ instalado e rodando
- [ ] Repositório clonado
- [ ] Ambiente virtual Python criado
- [ ] Dependências Python instaladas
- [ ] Dependências Node instaladas
- [ ] Banco de dados criado
- [ ] Arquivo .env configurado
- [ ] Migrações executadas
- [ ] Backend inicia sem erros
- [ ] Frontend inicia sem erros
- [ ] Testes passam (backend)
- [ ] Testes passam (frontend)
- [ ] API docs acessível (http://localhost:8000/docs)
- [ ] Frontend acessível (http://localhost:5173)

---

**Próximo:** [Arquitetura Backend](./03-arquitetura-backend.md)
