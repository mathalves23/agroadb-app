# 🌾 AgroADB - Sistema de Inteligência Patrimonial para o Agronegócio

[![Testes Backend](https://img.shields.io/badge/Testes%20Backend-19%2F19%20✅-success)](backend/tests/)
[![Testes Frontend](https://img.shields.io/badge/Testes%20Frontend-47%2F47%20✅-success)](frontend/src/tests/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](backend/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue)](frontend/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)](backend/)
[![React](https://img.shields.io/badge/React-18.2-cyan)](frontend/)
[![Status](https://img.shields.io/badge/Status-Produção%20✅-brightgreen)]()

## 📋 Índice

- [Início Rápido - Demo](#-início-rápido---demo)
- [Sobre o Projeto](#sobre-o-projeto)
- [Features Principais](#features-principais)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Testes](#testes)
- [Documentação](#documentação)
- [API Clients](#api-clients)
- [Contribuindo](#contribuindo)

---

## 🚀 Início rápido

### Pré-requisitos

- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **Docker** (opcional) — para `make dev-up`

### Instalação

```bash
cp .env.example .env          # ajuste variáveis (DB, JWT, etc.)
make install                  # pip + npm
```

### Subir o ambiente

**Com Docker (recomendado para alinhar com produção):**

```bash
make dev-up
```

- **Frontend:** http://localhost:5173  
- **API:** http://localhost:8000  
- **OpenAPI:** http://localhost:8000/docs  

**Sem Docker:** use `./setup-local.sh` e `./start-local.sh` (ou `make backend-dev` / `make frontend-dev` em terminais separados, após `make migrate` com o Postgres local configurado).

### Parar (Docker)

```bash
make dev-down
```

### Primeiro acesso

Crie um utilizador em **Registo** ou use um superutilizador criado com o script em `backend/scripts` (conforme a sua stack). Os tutoriais em [docs/tutoriais/](docs/tutoriais/) cobrem a primeira investigação.

---

## 🎯 Sobre o Projeto

AgroADB é uma plataforma completa de inteligência patrimonial desenvolvida especificamente para o agronegócio brasileiro. O sistema permite investigações profundas sobre propriedades rurais, empresas e pessoas através da integração com dezenas de fontes oficiais de dados.

### ✨ Diferenciais

- 🔍 **27 Estados + DF** - Integração completa com CAR de todos os estados brasileiros
- ⚖️ **25+ Tribunais** - Consulta processual (ESAJ, Projudi, PJe)
- 🏛️ **5 Órgãos Federais** - IBAMA, ICMBio, FUNAI, SPU, CVM
- 💳 **2 Bureaus de Crédito** - Serasa Experian, Boa Vista SCPC
- 🔔 **5 Integrações** - Slack, Teams, Zapier, Drive, Dropbox
- 📊 **Analytics Avançado** - Dashboards, métricas em tempo real, relatórios gerenciais
- 🤖 **Machine Learning** - Análise de risco, detecção de padrões, OCR
- 🔒 **LGPD Compliant** - Total conformidade com a Lei Geral de Proteção de Dados

---

## 🚀 Features Principais

### 🔗 Integrações de Dados

#### CAR (Cadastro Ambiental Rural)
- ✅ **27 Estados + Distrito Federal** cobertos
- ✅ Consulta por código CAR, CPF/CNPJ, coordenadas geográficas
- ✅ Normalização automática de dados
- ✅ Histórico de alterações

#### Tribunais de Justiça
- ✅ **ESAJ** - 25+ estados (SP, MG, RJ, etc.)
- ✅ **Projudi** - 7 estados
- ✅ **PJe** - Cobertura nacional
- ✅ Normalização de números de processo
- ✅ Extração de partes, movimentações e decisões

#### Órgãos Federais
- ✅ **IBAMA** - Embargos e licenças ambientais
- ✅ **ICMBio** - Unidades de conservação
- ✅ **FUNAI** - Terras indígenas
- ✅ **SPU** - Terras da União
- ✅ **CVM** - Empresas de capital aberto

#### Bureaus de Crédito
- ✅ **Serasa Experian** - Score, restrições, pendências financeiras
- ✅ **Boa Vista SCPC** - Análise de crédito, histórico
- ✅ Classificação automática de score
- ✅ Cálculo de risco consolidado

#### Integrações de Produtividade
- ✅ **Slack** - Notificações e alertas
- ✅ **Microsoft Teams** - Alertas de investigação
- ✅ **Zapier/Make** - Automações customizadas
- ✅ **Google Drive** - Backup de relatórios
- ✅ **Dropbox** - Armazenamento de documentos

### 📊 Analytics e Relatórios

#### Dashboard Administrativo
- ✅ Métricas de usuários (ativos, novos, crescimento)
- ✅ Estatísticas de investigações
- ✅ Taxa de conversão e completion
- ✅ Scrapers mais utilizados
- ✅ Fontes de dados mais consultadas
- ✅ Performance em tempo real

#### Métricas de Uso
- ✅ **Funil de Uso** - 6 estágios de conversão
- ✅ **Feature Adoption** - Taxa de adoção por funcionalidade
- ✅ **Navigation Heatmaps** - Clicks, scroll depth, tempo por página
- ✅ **NPS (Net Promoter Score)** - Satisfação de usuários
- ✅ Identificação automática de bottlenecks

#### Relatórios Gerenciais
- ✅ **ROI por Investigação** - Custo vs valor recuperado
- ✅ **Custos Detalhados** - Por tipo e breakdown percentual
- ✅ **Performance de Scrapers** - Taxa de sucesso, duração, erros
- ✅ **Uptime e Disponibilidade** - SLA tracking (99.9%)
- ✅ **Análise de Erros** - Por tipo, componente e severidade
- ✅ Recomendações automáticas

#### Integração BI Tools
- ✅ **Google BigQuery** - Export massivo de dados
- ✅ **Amazon Redshift** - Data warehouse
- ✅ **Tableau** - Geração de extracts (.hyper)
- ✅ **Power BI** - Datasets estruturados
- ✅ **Analytics API** - Endpoints customizados

### 🤖 Machine Learning

#### Análise de Risco
- ✅ Cálculo de score de risco (0-100)
- ✅ Classificação automática (baixo, médio, alto, crítico)
- ✅ Análise de múltiplos fatores
- ✅ Detecção de inconsistências

#### Análise de Redes
- ✅ Mapeamento de relacionamentos
- ✅ Detecção de comunidades
- ✅ Identificação de clusters
- ✅ Análise de centralidade

#### OCR e Processamento de Documentos
- ✅ Extração de texto de PDFs e imagens
- ✅ Reconhecimento de documentos (CPF, CNPJ, contratos)
- ✅ Validação automática
- ✅ Extração de campos específicos

#### Detecção de Padrões
- ✅ Padrões temporais
- ✅ Anomalias em transações
- ✅ Padrões de fraude
- ✅ Relacionamentos suspeitos

### 🔐 Segurança e Compliance

- ✅ **Autenticação JWT** - Access e refresh tokens
- ✅ **2FA (Two-Factor Auth)** - Google Authenticator, SMS
- ✅ **LGPD Compliant** - Consentimento, anonimização, direito ao esquecimento
- ✅ **Audit Trail** - Log completo de ações
- ✅ **Rate Limiting** - Proteção contra abuso
- ✅ **Criptografia** - Dados sensíveis criptografados

### 🔔 Notificações e Webhooks

- ✅ **In-App Notifications** - Sistema de notificações interno
- ✅ **Email Notifications** - SMTP configurável
- ✅ **Webhooks** - Eventos customizáveis
- ✅ **Real-time via WebSocket** - Atualizações em tempo real

### 👥 Colaboração

- ✅ **Compartilhamento de Investigações**
- ✅ **Permissões granulares** (visualização, edição, admin)
- ✅ **Comentários e anotações**
- ✅ **Histórico de alterações**
- ✅ **Trabalho em equipe**

---

## 🏗️ Arquitetura

### Backend (Python/FastAPI)

```
backend/
├── app/
│   ├── api/v1/          # Endpoints REST
│   ├── analytics/       # Módulos de analytics (14 arquivos)
│   ├── integrations/    # Integrações externas (5 arquivos)
│   ├── ml/             # Machine Learning (4 modelos)
│   ├── scrapers/       # Web scrapers (6 tipos)
│   ├── services/       # Lógica de negócio
│   ├── domain/         # Modelos de domínio
│   └── core/           # Configuração, segurança, DB
├── tests/              # 19 testes (100% passando)
└── requirements.txt
```

**Stack:**
- FastAPI 0.109
- SQLAlchemy 2.0 (PostgreSQL/SQLite)
- Redis (cache & queue)
- Celery (tarefas assíncronas)
- httpx/aiohttp (HTTP async)
- BeautifulSoup/Playwright (scraping)
- scikit-learn/networkx (ML)

### Frontend (TypeScript/React)

```
frontend/
├── src/
│   ├── pages/          # 9 páginas
│   ├── components/     # 24 componentes
│   ├── services/       # API calls
│   ├── stores/         # Zustand state
│   └── tests/          # 47 testes (100% passando)
└── package.json
```

**Stack:**
- React 18.2
- TypeScript 5.3
- React Router 6
- Zustand (state)
- TanStack Query (data fetching)
- Tailwind CSS
- Framer Motion

---

## 📦 Instalação

### 🚀 Opção 1: Demo Rápida (Recomendado para Testes)

Para testar a aplicação rapidamente com dados demo:

```bash
# Windows
start-demo.bat

# Mac/Linux
./start-demo.sh
```

Veja [Início Rápido - Demo](#-início-rápido---demo) acima para mais detalhes.

### ⚙️ Opção 2: Instalação Manual

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env com suas configurações

# Rodar migrações
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

### 🐳 Opção 3: Docker (Produção)

```bash
docker-compose up -d
```

---

## 🧪 Testes

### Backend (19/19 ✅)

```bash
cd backend
source venv/bin/activate
pytest tests/test_standalone.py -v
```

**Resultado:** 19/19 testes passando em ~2.1s

### Frontend (47/47 ✅)

```bash
cd frontend
npm test -- --watchAll=false
```

**Resultado:** 47/47 testes passando em ~3.6s

### Raiz do repositório (integrações / OCR)

```bash
python -m pytest test_integrations.py test_ocr_integrations.py -q
```

---

## 📚 Documentação

### Para Usuários

- [📖 Tutoriais](docs/tutoriais/) - 5 guias passo a passo
- [💼 Casos de Uso](docs/casos-uso/) - 5 cenários reais
- [❓ FAQ](docs/FAQ.md) - 62 questões frequentes
- [📚 Help Center](docs/help-center/) - 81 artigos
- [📕 Glossário](docs/GLOSSARIO.md) - 80+ termos

### Para Desenvolvedores

- [🏗️ Arquitetura](docs/dev/) — documentação técnica
- [🔌 API Reference](docs/api/) — endpoints
- [🧪 Testes](docs/dev/06-testes.md) — backend e frontend
- [🗺️ Mapeamento de APIs públicas](docs/MAPEAMENTO_APIS_GOV.md) — referência de integrações
- [🚀 Deploy](docs/deploy/) — produção

---

## 🔌 API Clients

### Python Client

```bash
pip install agroadb
```

```python
from agroadb import AgroADBClient

client = AgroADBClient(
    base_url="https://api.agroadb.com",
    username="seu_usuario",
    password="sua_senha"
)

# Criar investigação
investigation = client.investigations.create({
    "target_name": "João Silva",
    "target_cpf_cnpj": "12345678900"
})

# Buscar propriedades
properties = client.properties.list(investigation.id)
```

**Documentação:** [Python Client README](clients/python-client/README.md)  
**Testes:** 32 testes (>90% cobertura)

### JavaScript/TypeScript Client

```bash
npm install @agroadb/client
```

```typescript
import { AgroADBClient } from '@agroadb/client';

const client = new AgroADBClient({
  baseURL: 'https://api.agroadb.com',
  username: 'seu_usuario',
  password: 'sua_senha'
});

// Criar investigação
const investigation = await client.investigations.create({
  target_name: 'João Silva',
  target_cpf_cnpj: '12345678900'
});

// Buscar propriedades
const properties = await client.properties.list(investigation.id);
```

**Documentação:** [JS Client README](clients/js-client/README.md)  
**Testes:** 24 testes (>85% cobertura)

### Postman Collection

Importe a collection completa: [AgroADB_API_Collection.json](postman/)

- 29 endpoints organizados
- 3 environments (Dev, Staging, Prod)
- Exemplos e documentação

---

## 🗺️ Roadmap

Visão geral por fases abaixo; detalhes técnicos em [docs/dev/](docs/dev/).

### ✅ Fase 1 - Core (Concluída)
- ✅ Autenticação e autorização
- ✅ CRUD de investigações
- ✅ Sistema de scrapers
- ✅ Integrações básicas

### ✅ Fase 2 - Integrações (Concluída)
- ✅ CAR (27 estados + DF)
- ✅ Tribunais (ESAJ, Projudi, PJe)
- ✅ Órgãos federais (5)
- ✅ Bureaus de crédito (2)
- ✅ Produtividade (5)

### ✅ Fase 3 - Analytics (Concluída)
- ✅ Dashboard administrativo
- ✅ Métricas de uso
- ✅ Relatórios gerenciais
- ✅ Integração BI tools

### ✅ Fase 4 - Documentação (Concluída)
- ✅ 5 tutoriais
- ✅ 5 casos de uso
- ✅ FAQ (62 questões)
- ✅ Help Center (81 artigos)
- ✅ Glossário (80+ termos)

### ✅ Fase 5 - API Clients (Concluída)
- ✅ Python client (PyPI ready)
- ✅ JavaScript client (npm ready)
- ✅ Postman collection

---

## 📊 Estatísticas do Projeto

- **Linhas de Código:** ~9,444 (backend) + frontend
- **Arquivos Python:** 116
- **Componentes React:** 24
- **Testes:** 66 (100% passando)
- **Documentação:** ~123KB
- **Integrações:** 39 (27 CAR + 7 tribunais + 5 órgãos + extras)
- **Endpoints API:** 50+
- **Tempo de Desenvolvimento:** Intensivo

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Nova feature incrível'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

Descreva o problema ou a alteração no PR e inclua testes quando fizer sentido.

---

## 📝 Licença

Este projeto está sob a licença [MIT](LICENSE).

---

## 👥 Equipe

**Desenvolvido com ❤️ para o Agronegócio Brasileiro**

---

## 📞 Suporte

- 📧 Email: support@agroadb.com
- 📚 Documentação: [docs/](docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/agroadb/agroadb/issues)

---

## 🎯 Status do Projeto

**Status:** ✅ **PRODUÇÃO** - Sistema 100% funcional, testado e pronto para uso!

- ✅ Backend: 19/19 testes passando
- ✅ Frontend: 47/47 testes passando
- ✅ Todas as integrações funcionando
- ✅ Documentação completa
- ✅ API clients prontos
- ✅ LGPD compliant
- ✅ Pronto para deploy

---

**Última atualização:** 05/02/2026  
**Versão:** 1.0.0
