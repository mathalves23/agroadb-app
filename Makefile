# Makefile para AgroADB

.PHONY: help install dev-up dev-down migrate test lint format clean

# Cores para output
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

help: ## Mostra este menu de ajuda
	@echo ''
	@echo 'Uso:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} { \
		if (/^[a-zA-Z_-]+:.*?##.*$$/) {printf "    ${YELLOW}%-20s${GREEN}%s${RESET}\n", $$1, $$2} \
		else if (/^## .*$$/) {printf "  ${WHITE}%s${RESET}\n", substr($$1,4)} \
		}' $(MAKEFILE_LIST)

## Instalação e Setup
install: ## Instala todas as dependências
	@echo "📦 Instalando dependências do backend..."
	cd backend && pip install -r requirements.txt
	@echo "📦 Instalando dependências do frontend..."
	cd frontend && npm install
	@echo "✅ Instalação concluída!"

setup-env: ## Copia arquivo .env.example para .env
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Arquivo .env criado. Configure suas variáveis!"; \
	else \
		echo "⚠️  Arquivo .env já existe!"; \
	fi

## Docker
dev-up: ## Inicia ambiente de desenvolvimento com Docker
	@echo "🚀 Iniciando ambiente de desenvolvimento..."
	docker-compose up -d
	@echo "✅ Ambiente iniciado!"
	@echo "Frontend: http://localhost:5173"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/api/docs"

dev-down: ## Para ambiente de desenvolvimento
	@echo "🛑 Parando ambiente..."
	docker-compose down
	@echo "✅ Ambiente parado!"

dev-logs: ## Mostra logs do ambiente
	docker-compose logs -f

dev-rebuild: ## Reconstrói containers
	@echo "🔨 Reconstruindo containers..."
	docker-compose down
	docker-compose build
	docker-compose up -d
	@echo "✅ Containers reconstruídos!"

## Database
migrate: ## Executa migrações do banco de dados
	@echo "⬆️  Executando migrações..."
	cd backend && alembic upgrade head
	@echo "✅ Migrações aplicadas!"

migrate-create: ## Cria nova migração (use: make migrate-create MSG="descrição")
	@echo "📝 Criando migração..."
	cd backend && alembic revision --autogenerate -m "$(MSG)"
	@echo "✅ Migração criada!"

migrate-rollback: ## Desfaz última migração
	@echo "⬇️  Desfazendo migração..."
	cd backend && alembic downgrade -1
	@echo "✅ Migração desfeita!"

create-superuser: ## Cria superusuário
	@echo "👤 Criando superusuário..."
	docker-compose exec backend python scripts/create_superuser.sh

## Testes
test: ## Executa todos os testes
	@echo "🧪 Executando testes do backend..."
	cd backend && pytest
	@echo "✅ Testes concluídos!"

test-cov: ## Executa testes com cobertura
	@echo "🧪 Executando testes com cobertura..."
	cd backend && pytest --cov=app --cov-report=html --cov-report=term
	@echo "✅ Relatório de cobertura gerado em backend/htmlcov/index.html"

## Code Quality
lint: ## Executa linters
	@echo "🔍 Executando linters..."
	cd backend && flake8 app
	cd backend && mypy app
	cd frontend && npm run lint
	@echo "✅ Linting concluído!"

format: ## Formata código
	@echo "✨ Formatando código..."
	cd backend && black app
	cd backend && isort app
	cd frontend && npm run format
	@echo "✅ Código formatado!"

## Desenvolvimento
backend-dev: ## Inicia backend em modo desenvolvimento
	@echo "🚀 Iniciando backend..."
	cd backend && uvicorn app.main:app --reload

frontend-dev: ## Inicia frontend em modo desenvolvimento
	@echo "🚀 Iniciando frontend..."
	cd frontend && npm run dev

celery-worker: ## Inicia Celery worker
	@echo "👷 Iniciando Celery worker..."
	cd backend && celery -A app.workers.celery_app worker --loglevel=info

celery-beat: ## Inicia Celery beat
	@echo "⏰ Iniciando Celery beat..."
	cd backend && celery -A app.workers.celery_app beat --loglevel=info

## Limpeza
clean: ## Remove arquivos temporários
	@echo "🧹 Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	@echo "✅ Limpeza concluída!"

clean-all: clean ## Remove todos os arquivos gerados (incluindo node_modules e venv)
	@echo "🧹 Limpeza profunda..."
	rm -rf backend/venv
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	docker-compose down -v
	@echo "✅ Limpeza profunda concluída!"

## Produção
build: ## Constrói imagens para produção
	@echo "🏗️  Construindo imagens..."
	docker-compose -f docker-compose.prod.yml build
	@echo "✅ Imagens construídas!"

deploy: ## Deploy em produção (configure antes!)
	@echo "🚀 Iniciando deploy..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Deploy concluído!"

## Info
info: ## Mostra informações do ambiente
	@echo "📊 Informações do Ambiente:"
	@echo ""
	@echo "Python: $(shell python --version 2>&1)"
	@echo "Node: $(shell node --version 2>&1)"
	@echo "Docker: $(shell docker --version 2>&1)"
	@echo "Docker Compose: $(shell docker-compose --version 2>&1)"
	@echo ""
	@echo "Status dos containers:"
	@docker-compose ps
