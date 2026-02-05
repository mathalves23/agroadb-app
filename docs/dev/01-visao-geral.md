# 1. Visão Geral do AgroADB

## 🌾 O que é o AgroADB?

O **AgroADB** (Agro Asset Database) é uma plataforma completa de inteligência patrimonial desenvolvida especificamente para o setor agropecuário brasileiro. O sistema permite realizar investigações detalhadas sobre propriedades rurais, empresas e pessoas físicas, oferecendo ferramentas avançadas para due diligence, análise de risco e compliance legal.

### Principais Objetivos

- 🔍 **Investigação Patrimonial**: Análise completa de ativos rurais e empresariais
- 📊 **Due Diligence**: Avaliação de riscos para transações comerciais
- ⚖️ **Compliance Legal**: Verificação de regularidade jurídica e ambiental
- 📈 **Análise de Risco**: Identificação de red flags e pendências
- 🤝 **Colaboração**: Trabalho em equipe com auditoria completa

---

## 🏗️ Arquitetura do Sistema

O AgroADB utiliza uma arquitetura moderna de **microserviços desacoplados**:

```
┌─────────────────────────────────────────────────────────┐
│                    USUÁRIO FINAL                         │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              FRONTEND (React + TypeScript)               │
│  • Single Page Application (SPA)                         │
│  • Design System completo                                │
│  • Estado gerenciado com Context API                     │
│  • WebSocket para tempo real                             │
└────────────────────┬────────────────────────────────────┘
                     │ REST API + WebSocket
┌────────────────────▼────────────────────────────────────┐
│              BACKEND (FastAPI + Python)                  │
│  • API REST com documentação automática                 │
│  • Autenticação JWT                                      │
│  • Sistema de filas (Redis Queue)                        │
│  • WebSocket para notificações em tempo real            │
└──┬────────┬────────┬────────┬────────┬──────────────────┘
   │        │        │        │        │
   │        │        │        │        └──────────┐
   │        │        │        │                   │
┌──▼───┐ ┌─▼──┐ ┌───▼───┐ ┌─▼────┐ ┌───────────▼────────┐
│ Post │ │Redis│ │INCRA  │ │ CAR  │ │ Integrações        │
│ greSQL│ │Cache│ │Scraper│ │Scraper│ │ Externas (PJe)     │
└──────┘ └────┘ └───────┘ └──────┘ └────────────────────┘
```

### Camadas da Aplicação

#### 1. **Camada de Apresentação (Frontend)**
- **Tecnologia**: React 18 + TypeScript
- **UI**: Tailwind CSS + Design System próprio
- **Estado**: React Context API
- **Animações**: Framer Motion
- **Comunicação**: Axios + WebSocket

#### 2. **Camada de API (Backend)**
- **Framework**: FastAPI (Python 3.11+)
- **Autenticação**: JWT + OAuth2
- **Validação**: Pydantic
- **Documentação**: OpenAPI/Swagger automático

#### 3. **Camada de Negócio (Services)**
- **Investigações**: Gerenciamento de casos
- **Scrapers**: Coleta automatizada de dados
- **Notificações**: Sistema de alertas
- **Relatórios**: Geração de PDFs e Excel
- **Colaboração**: Sistema de comentários e atividades

#### 4. **Camada de Dados**
- **Banco Principal**: PostgreSQL 15
- **Cache**: Redis 7
- **Fila de Jobs**: Redis Queue
- **Armazenamento**: Sistema de arquivos + S3 (opcional)

#### 5. **Camada de Infraestrutura**
- **Containers**: Docker + Docker Compose
- **Proxy**: Nginx
- **Monitoramento**: Prometheus + Grafana
- **CI/CD**: GitHub Actions

---

## 🛠️ Tecnologias Utilizadas

### Backend

| Tecnologia | Versão | Propósito |
|-----------|--------|-----------|
| Python | 3.11+ | Linguagem principal |
| FastAPI | 0.104+ | Framework web |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | 1.12+ | Migrações de banco |
| Pydantic | 2.5+ | Validação de dados |
| Redis | 7.0+ | Cache e filas |
| PostgreSQL | 15+ | Banco de dados |
| Pytest | 7.4+ | Testes |
| BeautifulSoup4 | 4.12+ | Web scraping |
| Celery | 5.3+ | Task queue |
| Passlib | 1.7+ | Hash de senhas |
| PyJWT | 2.8+ | JWT tokens |

### Frontend

| Tecnologia | Versão | Propósito |
|-----------|--------|-----------|
| React | 18.2+ | Framework UI |
| TypeScript | 5.3+ | Type safety |
| Vite | 5.0+ | Build tool |
| Tailwind CSS | 3.3+ | Styling |
| Framer Motion | 10.16+ | Animações |
| React Router | 6.20+ | Roteamento |
| Axios | 1.6+ | HTTP client |
| Recharts | 2.10+ | Gráficos |
| Lucide React | 0.294+ | Ícones |
| Jest | 29.7+ | Testes |

### DevOps

| Tecnologia | Propósito |
|-----------|-----------|
| Docker | Containerização |
| Docker Compose | Orquestração local |
| Nginx | Proxy reverso |
| Let's Encrypt | Certificados SSL |
| GitHub Actions | CI/CD |
| Prometheus | Métricas |
| Grafana | Dashboards |

---

## 📁 Estrutura do Projeto

```
agroadb/
│
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── api/               # Endpoints REST
│   │   │   └── v1/
│   │   │       ├── endpoints/ # Rotas por módulo
│   │   │       └── router.py  # Router principal
│   │   ├── core/              # Configurações centrais
│   │   │   ├── config.py      # Settings
│   │   │   ├── security.py    # Auth/JWT
│   │   │   ├── database.py    # DB connection
│   │   │   └── cache.py       # Redis cache
│   │   ├── models/            # Modelos SQLAlchemy
│   │   │   ├── user.py
│   │   │   ├── investigation.py
│   │   │   └── ...
│   │   ├── services/          # Lógica de negócio
│   │   │   ├── investigation.py
│   │   │   ├── notifications.py
│   │   │   ├── reports.py
│   │   │   └── ...
│   │   ├── scrapers/          # Web scrapers
│   │   │   ├── incra.py
│   │   │   ├── car.py
│   │   │   └── receita.py
│   │   └── main.py            # App principal
│   ├── tests/                 # Testes (66 testes)
│   │   ├── test_auth.py
│   │   ├── test_investigation_service.py
│   │   └── ...
│   ├── requirements.txt       # Dependências Python
│   ├── pyproject.toml         # Config do projeto
│   └── Dockerfile             # Imagem Docker
│
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── components/        # Componentes React
│   │   │   └── ui/           # 40+ componentes UI
│   │   │       ├── Controls.tsx
│   │   │       ├── Cards.tsx
│   │   │       ├── Navigation.tsx
│   │   │       └── ...
│   │   ├── pages/            # Páginas da aplicação
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Investigations.tsx
│   │   │   └── ...
│   │   ├── contexts/         # React Contexts
│   │   │   ├── AuthContext.tsx
│   │   │   ├── ThemeContext.tsx
│   │   │   └── WebSocketContext.tsx
│   │   ├── lib/              # Utilitários
│   │   │   ├── design-system.ts
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   ├── index.css         # Estilos globais
│   │   └── main.tsx          # Entry point
│   ├── __tests__/            # Testes (90 testes)
│   ├── package.json          # Dependências Node
│   ├── tsconfig.json         # Config TypeScript
│   └── Dockerfile            # Imagem Docker
│
├── docs/                      # Documentação
│   ├── dev/                  # Docs para devs
│   ├── user/                 # Docs para usuários
│   ├── api/                  # API reference
│   └── deploy/               # Guias de deploy
│
├── scripts/                   # Scripts de automação
│   ├── backup.sh             # Backup DB
│   ├── restore.sh            # Restore DB
│   ├── deploy.sh             # Deploy completo
│   ├── setup-ssl.sh          # Configurar SSL
│   └── verify-all.sh         # Verificação completa
│
├── monitoring/               # Configuração de monitoramento
│   ├── prometheus.yml        # Config Prometheus
│   └── grafana/             # Dashboards Grafana
│
├── .github/                  # GitHub Actions
│   └── workflows/
│       └── ci-cd.yml        # Pipeline CI/CD
│
├── docker-compose.production.yml  # Stack de produção
├── .env.example              # Exemplo de variáveis
├── README.md                 # Documentação principal
└── PROXIMOS_PASSOS.md       # Roadmap do projeto
```

---

## 🔄 Fluxo de Dados

### 1. Criação de uma Investigação

```
Usuário                Frontend              Backend              Database
   │                      │                     │                    │
   │  1. Criar Investigação│                    │                    │
   ├──────────────────────>│                    │                    │
   │                      │  2. POST /api/v1/   │                    │
   │                      │     investigations  │                    │
   │                      ├────────────────────>│                    │
   │                      │                     │  3. INSERT INTO    │
   │                      │                     │     investigations │
   │                      │                     ├───────────────────>│
   │                      │                     │<───────────────────┤
   │                      │  4. Response 201    │                    │
   │                      │<────────────────────┤                    │
   │  5. Exibir Sucesso   │                    │                    │
   │<──────────────────────                    │                    │
   │                      │                     │  6. Queue Scraper  │
   │                      │                     │     Job (Redis)    │
   │                      │                     ├────────────>       │
```

### 2. Execução de Scraper

```
Scheduler          Redis Queue         Worker            External API
   │                  │                   │                   │
   │  1. Check Jobs   │                  │                   │
   ├─────────────────>│                  │                   │
   │<─────────────────┤                  │                   │
   │  2. Get Job      │                  │                   │
   │                  ├─────────────────>│                   │
   │                  │                  │  3. Fetch Data    │
   │                  │                  ├──────────────────>│
   │                  │                  │<──────────────────┤
   │                  │  4. Job Complete │                   │
   │                  │<─────────────────┤                   │
   │                  │  5. Notify (WS)  │                   │
   │                  ├──────────────────────> Frontend      │
```

---

## 🎯 Principais Funcionalidades

### 1. **Investigações Patrimoniais**
- Criação e gerenciamento de casos
- Status tracking (rascunho, ativo, concluído)
- Cálculo automático de progresso
- Timeline de atividades
- Tags e categorização

### 2. **Web Scrapers Automatizados**
- **INCRA**: Dados de propriedades rurais
- **CAR**: Cadastro Ambiental Rural
- **Receita Federal**: Dados empresariais
- **PJe**: Processos judiciais
- Sistema de filas com retry
- Rate limiting e respeito a robots.txt

### 3. **Sistema de Relatórios**
- Geração de PDFs profissionais
- Export para Excel
- Relatórios customizáveis
- Templates por tipo de investigação
- Assinatura digital (opcional)

### 4. **Colaboração em Tempo Real**
- Sistema de comentários
- Menções de usuários (@user)
- Activity feed
- Notificações instantâneas (WebSocket)
- Controle de permissões por usuário

### 5. **Segurança e LGPD**
- Criptografia de dados sensíveis
- Audit log completo
- Gestão de consentimento
- Anonimização de dados
- Right to be forgotten
- Exportação de dados pessoais

### 6. **Dashboard Analytics**
- Métricas em tempo real
- Gráficos interativos
- Comparação de períodos
- Export de dados
- Filtros avançados

---

## 🔐 Segurança

### Autenticação e Autorização
- **JWT (JSON Web Tokens)** para autenticação
- **Refresh tokens** para sessões longas
- **RBAC** (Role-Based Access Control)
- **OAuth2** password flow
- **Rate limiting** (60 req/min por IP)

### Proteções Implementadas
- ✅ **SQL Injection**: Prevenido com SQLAlchemy ORM
- ✅ **XSS**: React escapa conteúdo automaticamente
- ✅ **CSRF**: Tokens CSRF em formulários
- ✅ **Clickjacking**: Headers X-Frame-Options
- ✅ **HTTPS**: SSL/TLS obrigatório em produção
- ✅ **Password Hashing**: Bcrypt com salt
- ✅ **Data Encryption**: AES-256 para dados sensíveis

### Compliance LGPD
- Consentimento explícito
- Transparência no uso de dados
- Portabilidade de dados
- Direito ao esquecimento
- Anonimização
- Auditoria completa

---

## 📊 Performance

### Otimizações Implementadas

1. **Backend**
   - Cache Redis para queries frequentes
   - Índices de banco de dados otimizados
   - Connection pooling (SQLAlchemy)
   - Lazy loading de relacionamentos
   - Paginação cursor-based

2. **Frontend**
   - Code splitting (Vite)
   - Lazy loading de componentes
   - Memoização de componentes pesados
   - Virtual scrolling em listas grandes
   - Debounce em busca

3. **Infraestrutura**
   - CDN para assets estáticos
   - Gzip compression (Nginx)
   - HTTP/2 habilitado
   - Cache de 1 ano para assets

### Métricas Alvo
- ⚡ Tempo de resposta API: < 100ms (p95)
- 🚀 First Contentful Paint: < 1.5s
- 📊 Time to Interactive: < 3s
- 💾 Cache hit rate: > 80%

---

## 🔄 Próximos Passos

Ver [PROXIMOS_PASSOS.md](../../PROXIMOS_PASSOS.md) para o roadmap completo.

---

## 📞 Suporte Técnico

- **Email**: dev@agroadb.com
- **Slack**: #dev-agroadb
- **GitHub**: Issues e Pull Requests
- **Documentação**: Esta wiki
