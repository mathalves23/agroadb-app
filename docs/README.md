# 📚 Documentação Completa - AgroADB

## 🎯 Bem-vindo à Documentação Oficial

Esta é a documentação completa do **AgroADB** - Sistema de Inteligência Patrimonial para o Agronegócio.

---

## 📖 Índice Completo

### 👨‍💻 [Para Desenvolvedores](./dev/)

1. **[Visão Geral](./dev/01-visao-geral.md)**
   - O que é o AgroADB
   - Arquitetura do sistema
   - Tecnologias utilizadas
   - Fluxo de dados
   - Principais funcionalidades

2. **[Ambiente de Desenvolvimento](./dev/02-ambiente-desenvolvimento.md)**
   - Pré-requisitos (Python, Node, PostgreSQL, Redis)
   - Instalação local passo a passo
   - Instalação com Docker
   - Configuração de IDE (VS Code, PyCharm)
   - Comandos úteis
   - Troubleshooting

3. **[Arquitetura Backend](./dev/03-arquitetura-backend.md)**
   - Estrutura de pastas
   - Modelos de dados (SQLAlchemy)
   - Serviços e endpoints
   - Autenticação JWT
   - Cache Redis
   - Sistema de filas
   - Scrapers
   - Logging e métricas

4. **[Arquitetura Frontend](./dev/04-arquitetura-frontend.md)**
   - Estrutura de componentes
   - Design system completo
   - Gerenciamento de estado (Context API)
   - Rotas e navegação
   - Comunicação com API
   - WebSocket
   - Animações (Framer Motion)
   - Build de produção

5. **[Banco de Dados](./dev/05-banco-dados.md)**
   - Schema completo
   - Migrações (Alembic)
   - Relacionamentos
   - Índices otimizados
   - Queries comuns
   - Backup e restore

6. **[Testes](./dev/06-testes.md)**
   - Configuração Pytest (backend)
   - Configuração Jest (frontend)
   - 156 testes implementados
   - 60%+ cobertura garantida
   - Fixtures e mocks
   - Boas práticas
   - CI/CD integration

7. **[Scrapers](./dev/scrapers-incra.md)**
   - INCRA (propriedades rurais)
   - CAR (cadastro ambiental)
   - Receita Federal (empresas)

---

### 🚀 [Deploy e Infraestrutura](./deploy/)

1. **[Deploy em Produção](./deploy/01-deploy-producao.md)**
   - Requisitos de infraestrutura
   - Deploy com Docker Compose
   - Deploy em Cloud (AWS, GCP, Azure)
   - Configuração de DNS e SSL
   - Checklist completo

2. **[CI/CD](../../.github/workflows/ci-cd.yml)**
   - Pipeline GitHub Actions
   - Testes automáticos
   - Security scan
   - Deploy staging/production

3. **[Monitoramento](../../monitoring/prometheus.yml)**
   - Prometheus (métricas)
   - Grafana (dashboards)
   - Logs estruturados
   - Alertas

4. **[Backup e Recovery](../../scripts/backup.sh)**
   - Backup automático diário
   - Upload para S3
   - Retenção de 30 dias
   - Script de restore

---

### 👥 [Para Usuários](./user/)

1. **[Guia do Usuário](./user/01-guia-usuario.md)**
   - Primeiros passos
   - Tour da plataforma
   - Criando investigações
   - Dashboard
   - Gerando relatórios
   - Colaboração
   - Notificações
   - FAQ
   - Suporte

---

### 📖 [API Reference](./api/)

1. **[Documentação da API](./api/README.md)**
   - Autenticação (JWT)
   - Endpoints de investigações
   - Relatórios
   - Integrações jurídicas
   - Colaboração
   - Notificações
   - Códigos de status HTTP
   - Rate limiting
   - Exemplos de código (Python, JavaScript)

2. **[Swagger UI](http://localhost:8000/docs)**
   - Documentação interativa
   - Testar endpoints
   - Ver schemas

---

## 🎯 Acesso Rápido

### Para Começar

| Perfil | Documento Inicial |
|--------|------------------|
| Desenvolvedor Novo | [Ambiente de Desenvolvimento](./dev/02-ambiente-desenvolvimento.md) |
| DevOps | [Deploy em Produção](./deploy/01-deploy-producao.md) |
| Usuário Final | [Guia do Usuário](./user/01-guia-usuario.md) |
| Integrador | [API Reference](./api/README.md) |

### Comandos Mais Usados

```bash
# Desenvolvimento
docker-compose up -d           # Iniciar tudo
./scripts/verify-all.sh        # Verificar tudo
./scripts/run-all-tests.sh     # Executar testes

# Deploy
./scripts/deploy.sh production # Deploy completo
./scripts/backup.sh            # Backup manual

# Testes
pytest tests/ -v --cov=app     # Backend
npm run test:ci                # Frontend
```

---

## 📊 Status da Documentação

| Seção | Status | Páginas | Última Atualização |
|-------|--------|---------|-------------------|
| Dev | ✅ Completo | 6 | 05/02/2026 |
| Deploy | ✅ Completo | 4 | 05/02/2026 |
| Usuário | ✅ Completo | 1 | 05/02/2026 |
| API | ✅ Completo | 1 | 05/02/2026 |

---

## 🔍 Busca Rápida

**Procurando por...?**

- Como instalar? → [Ambiente de Desenvolvimento](./dev/02-ambiente-desenvolvimento.md)
- Como fazer deploy? → [Deploy em Produção](./deploy/01-deploy-producao.md)
- Como usar? → [Guia do Usuário](./user/01-guia-usuario.md)
- Endpoints da API? → [API Reference](./api/README.md)
- Como testar? → [Testes](./dev/06-testes.md)
- Arquitetura? → [Visão Geral](./dev/01-visao-geral.md)

---

## 🆘 Precisa de Ajuda?

1. **Consulte a documentação** relevante acima
2. **Procure em Issues** do GitHub
3. **Entre em contato**:
   - 📧 Email: suporte@agroadb.com
   - 💬 Slack: #help
   - 📱 WhatsApp: (11) 99999-9999

---

## 📝 Contribuindo com a Documentação

Encontrou algo errado ou quer melhorar?

1. Edite o arquivo markdown relevante
2. Siga o padrão de formatação
3. Envie um Pull Request

**Localização dos arquivos**: `agroadb/docs/`

---

## 📚 Recursos Externos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Docs](https://docs.docker.com/)

---

## 📅 Histórico de Versões

- **v1.0.0** (05/02/2026) - Release inicial com documentação completa

---

<div align="center">

**📚 Documentação Completa e Profissional**

**© 2026 AgroADB - Sistema de Inteligência Patrimonial**

*Desenvolvido com ❤️ para o agronegócio brasileiro*

</div>
