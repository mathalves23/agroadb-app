# AgroADB - Sistema de Inteligência Patrimonial

![Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![Tests](https://img.shields.io/badge/tests-156%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-60%25%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🌾 Sobre o Projeto

O **AgroADB** é uma plataforma completa de inteligência patrimonial desenvolvida especificamente para o setor agropecuário brasileiro. Permite realizar investigações detalhadas sobre propriedades rurais, empresas e pessoas físicas, oferecendo ferramentas avançadas para due diligence, análise de risco e compliance legal.

---

## ✨ Principais Funcionalidades

- 🔍 **Investigações Patrimoniais Completas**
- 🏡 **Análise de Propriedades Rurais** (INCRA, CAR)
- 🏢 **Due Diligence Empresarial** (Receita Federal)
- ⚖️ **Integração PJe** (Processo Judicial Eletrônico)
- 📊 **Relatórios Profissionais** (PDF, Excel)
- 🔐 **LGPD Compliance** completo
- 👥 **Colaboração em Tempo Real**
- 📧 **Notificações Inteligentes**
- 🎨 **UI/UX Moderna** (Dark Mode, Animações)

---

## 🚀 Quick Start

### Com Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/agroadb.git
cd agroadb

# 2. Configure as variáveis
cp .env.example .env
nano .env

# 3. Inicie os serviços
docker-compose -f docker-compose.production.yml up -d

# 4. Acesse
# Frontend: http://localhost
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Instalação Manual

Ver [Documentação Completa](./docs/README.md)

---

## 📚 Documentação

### 👨‍💻 Para Desenvolvedores

- [Visão Geral e Arquitetura](./docs/dev/01-visao-geral.md)
- [Configuração do Ambiente](./docs/dev/02-ambiente-desenvolvimento.md)
- [Testes e Qualidade](./docs/dev/06-testes.md)

### 🚀 Deploy

- [Deploy em Produção](./docs/deploy/01-deploy-producao.md)
- [CI/CD](./DEPLOY.md)
- [Monitoramento](./docs/deploy/03-monitoramento.md)

### 👥 Para Usuários

- [Guia do Usuário](./docs/user/01-guia-usuario.md)
- [FAQ](./docs/user/04-faq.md)

### 📖 API

- [API Reference](./docs/api/README.md)
- [Swagger UI](http://localhost:8000/docs)

---

## 🏗️ Tecnologias

### Backend
- Python 3.11+
- FastAPI
- PostgreSQL 15+
- Redis 7+
- SQLAlchemy
- Alembic

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- Framer Motion
- Recharts

### DevOps
- Docker
- GitHub Actions
- Prometheus
- Grafana

---

## 📊 Status do Projeto

| Módulo | Status | Testes | Docs |
|--------|--------|--------|------|
| Autenticação | ✅ | 25 | ✅ |
| Investigações | ✅ | 18 | ✅ |
| Scrapers | ✅ | ✅ | ✅ |
| Cache Redis | ✅ | 13 | ✅ |
| LGPD | ✅ | ✅ | ✅ |
| Notificações | ✅ | ✅ | ✅ |
| Relatórios | ✅ | ✅ | ✅ |
| Colaboração | ✅ | ✅ | ✅ |
| PJe | ✅ | 10 | ✅ |
| UI/UX | ✅ | 90 | ✅ |

**Total**: 156 testes | 60%+ cobertura | **Production Ready** ✅

---

## 🧪 Executando Testes

```bash
# Todos os testes
./scripts/run-all-tests.sh

# Backend apenas
./scripts/run-backend-tests.sh

# Frontend apenas
./scripts/run-frontend-tests.sh

# Verificação completa
./scripts/verify-all.sh
```

---

## 📁 Estrutura do Projeto

```
agroadb/
├── backend/          # FastAPI Backend
├── frontend/         # React Frontend
├── docs/            # 📚 Documentação Completa
│   ├── dev/         # Para desenvolvedores
│   ├── user/        # Para usuários
│   ├── api/         # API Reference
│   └── deploy/      # Guias de deploy
├── scripts/         # Scripts de automação
├── monitoring/      # Prometheus & Grafana
└── .github/        # CI/CD
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

Ver [CONTRIBUTING.md](./CONTRIBUTING.md) para mais detalhes.

---

## 📞 Suporte

- 📧 **Email**: suporte@agroadb.com
- 📚 **Documentação**: [docs/README.md](./docs/README.md)
- 💬 **GitHub Issues**: [Issues](https://github.com/seu-usuario/agroadb/issues)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.

---

## 🎯 Roadmap

Ver [PROXIMOS_PASSOS.md](./PROXIMOS_PASSOS.md) para o roadmap completo.

---

<div align="center">

**Desenvolvido com ❤️ para o agronegócio brasileiro**

[![GitHub Stars](https://img.shields.io/github/stars/seu-usuario/agroadb?style=social)](https://github.com/seu-usuario/agroadb)
[![GitHub Forks](https://img.shields.io/github/forks/seu-usuario/agroadb?style=social)](https://github.com/seu-usuario/agroadb)

**© 2026 AgroADB - Todos os direitos reservados**

</div>
