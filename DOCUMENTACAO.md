# 📚 Índice de Documentação - AgroADB

## 🎯 Documentação Completa em Português

Toda a documentação do AgroADB está organizada na pasta `docs/`.

---

## 📖 Guias por Tipo de Usuário

### 👨‍💻 **Sou Desenvolvedor**

**Início Rápido:**
1. [Visão Geral do Sistema](./docs/dev/01-visao-geral.md) - Entenda a arquitetura
2. [Configurar Ambiente](./docs/dev/02-ambiente-desenvolvimento.md) - Setup completo
3. [Arquitetura Backend](./docs/dev/03-arquitetura-backend.md) - FastAPI em detalhes
4. [Arquitetura Frontend](./docs/dev/04-arquitetura-frontend.md) - React em detalhes

**Desenvolvimento:**
- [Banco de Dados](./docs/dev/05-banco-dados.md) - Schema e queries
- [Testes](./docs/dev/06-testes.md) - 156 testes, 60%+ cobertura
- [Scrapers](./docs/dev/scrapers-incra.md) - Web scraping

---

### 🚀 **Sou DevOps/SysAdmin**

**Deploy:**
1. [Deploy em Produção](./docs/deploy/01-deploy-producao.md) - Guia completo
2. [CI/CD Pipeline](./.github/workflows/ci-cd.yml) - GitHub Actions
3. [Monitoramento](./monitoring/prometheus.yml) - Prometheus & Grafana
4. [Backup](./scripts/backup.sh) - Backup automático

**Scripts:**
- `./scripts/deploy.sh` - Deploy completo automatizado
- `./scripts/setup-ssl.sh` - Configurar SSL/TLS
- `./scripts/verify-all.sh` - Verificar tudo

---

### 👤 **Sou Usuário Final**

**Começar a Usar:**
1. [Guia do Usuário](./docs/user/01-guia-usuario.md) - Tutorial completo
   - Como criar conta
   - Primeira investigação
   - Gerar relatórios
   - Trabalhar em equipe

---

### 🔌 **Quero Integrar com a API**

**API Reference:**
1. [Documentação da API](./docs/api/README.md) - Endpoints completos
   - Autenticação
   - Investigações
   - Relatórios
   - Integrações jurídicas
   - Exemplos de código

2. **[Swagger UI](http://localhost:8000/docs)** - Documentação interativa

---

## 📁 Estrutura da Documentação

```
docs/
├── README.md                      # Este arquivo (índice)
│
├── dev/                           # Para Desenvolvedores
│   ├── 01-visao-geral.md         # ⭐ Comece aqui
│   ├── 02-ambiente-desenvolvimento.md
│   ├── 03-arquitetura-backend.md
│   ├── 04-arquitetura-frontend.md
│   ├── 05-banco-dados.md
│   ├── 06-testes.md
│   ├── scrapers-incra.md
│   ├── scrapers-car.md
│   └── scrapers-receita.md
│
├── deploy/                        # Deploy e Infraestrutura
│   └── 01-deploy-producao.md     # ⭐ Guia de deploy
│
├── user/                          # Para Usuários
│   └── 01-guia-usuario.md        # ⭐ Tutorial completo
│
└── api/                           # API Reference
    └── README.md                  # ⭐ Documentação da API
```

---

## 🎯 Fluxos Comuns

### Novo Desenvolvedor

```
1. Visão Geral → 2. Setup Ambiente → 3. Arquitetura Backend/Frontend → 4. Começar a Desenvolver
```

### Deploy em Produção

```
1. Deploy Produção → 2. Verificar SSL → 3. Configurar Monitoring → 4. Testar Health Checks
```

### Usuário Novo

```
1. Guia do Usuário → 2. Criar Conta → 3. Tour Guiado → 4. Primeira Investigação
```

### Integração API

```
1. API Reference → 2. Autenticar → 3. Testar Endpoints → 4. Implementar
```

---

## ⚡ Comandos Essenciais

### Desenvolvimento Local

```bash
# Backend
cd backend && uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev

# Com Docker
docker-compose up -d
```

### Testes

```bash
# Todos
./scripts/run-all-tests.sh

# Backend
./scripts/run-backend-tests.sh

# Frontend
./scripts/run-frontend-tests.sh

# Verificação completa
./scripts/verify-all.sh
```

### Deploy

```bash
# Produção
./scripts/deploy.sh production app.agroadb.com

# Staging
./scripts/deploy.sh staging staging.agroadb.com
```

---

## 📊 Documentação por Tema

### Autenticação
- [Backend: JWT](./dev/03-arquitetura-backend.md#autenticação-e-segurança)
- [API: Endpoints](./api/README.md#autenticação)

### Investigações
- [Backend: Service](./dev/03-arquitetura-backend.md#fluxo-de-uma-requisição)
- [Frontend: Página](./dev/04-arquitetura-frontend.md)
- [API: Endpoints](./api/README.md#investigações)
- [Usuário: Como Usar](./user/01-guia-usuario.md#criando-sua-primeira-investigação)

### Scrapers
- [INCRA](./dev/scrapers-incra.md)
- [CAR](./dev/scrapers-car.md)
- [Receita Federal](./dev/scrapers-receita.md)

### Deploy
- [Produção](./deploy/01-deploy-producao.md)
- [Docker](../docker-compose.production.yml)
- [CI/CD](../.github/workflows/ci-cd.yml)

---

## 🔍 Procurando Algo Específico?

| Preciso... | Vá para... |
|-----------|------------|
| Instalar localmente | [Ambiente de Desenvolvimento](./dev/02-ambiente-desenvolvimento.md) |
| Entender a arquitetura | [Visão Geral](./dev/01-visao-geral.md) |
| Fazer deploy | [Deploy Produção](./deploy/01-deploy-producao.md) |
| Usar a API | [API Reference](./api/README.md) |
| Rodar testes | [Testes](./dev/06-testes.md) |
| Criar scrapers | [Scrapers](./dev/scrapers-incra.md) |
| Configurar banco | [Banco de Dados](./dev/05-banco-dados.md) |
| Manual do usuário | [Guia do Usuário](./user/01-guia-usuario.md) |

---

## ✅ Status da Documentação

- ✅ **12 documentos** criados
- ✅ **100% em português**
- ✅ **Para dev, user e deploy**
- ✅ **Exemplos de código**
- ✅ **Diagramas e fluxos**
- ✅ **Troubleshooting**
- ✅ **Última atualização**: 05/02/2026

---

## 📞 Suporte

**Não encontrou o que procura?**

- 📧 Email: suporte@agroadb.com
- 💬 GitHub Issues: [Reportar problema](https://github.com/seu-usuario/agroadb/issues)
- 📱 WhatsApp: (11) 99999-9999
- 📚 Docs Online: https://docs.agroadb.com

---

## 🔄 Atualizações

Esta documentação é atualizada regularmente. Para ver as mudanças:

```bash
git log docs/
```

---

## 📝 Convenções

### Emojis Usados

- 🎯 = Importante
- ✅ = Completo/Verificado
- ⚠️ = Atenção
- 💡 = Dica
- 🔧 = Configuração
- 📊 = Dados/Métricas
- 🚀 = Deploy/Produção

### Blocos de Código

```bash
# Comandos shell
```

```python
# Código Python
```

```typescript
# Código TypeScript
```

---

<div align="center">

**📚 Documentação Completa e Profissional**

Desenvolvida para desenvolvedores, DevOps e usuários finais.

**© 2026 AgroADB**

</div>
