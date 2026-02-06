# 🚀 Guia de Demonstração - AgroADB

Este guia permite que qualquer pessoa execute a aplicação AgroADB completa com dados de demonstração em apenas **uma linha de comando**.

## 📋 Pré-requisitos

Antes de executar, certifique-se de ter instalado:

### Windows, Mac e Linux:

1. **Python 3.11+**
   - Download: https://www.python.org/downloads/
   - Verificar: `python --version` ou `python3 --version`

2. **Node.js 18+**
   - Download: https://nodejs.org/
   - Verificar: `node --version`

## 🎯 Execução Rápida

### Windows:

```bash
start-demo.bat
```

### Mac/Linux:

```bash
chmod +x start-demo.sh
./start-demo.sh
```

## ⏱️ Tempo de Execução

- **Primeira vez:** 5-10 minutos (instalação de dependências)
- **Execuções seguintes:** 1-2 minutos

## 🌐 Acessando a Aplicação

Após a execução, acesse:

**Frontend:** http://localhost:5173

**Backend API:** http://localhost:8000

**Documentação da API:** http://localhost:8000/docs

## 🔐 Credenciais de Acesso

O script cria automaticamente 3 usuários demo com dados completos:

### 👤 Usuário 1 (Principal)
- **Email:** `demo@agroadb.com`
- **Senha:** `demo123`
- **Organização:** AgroADB Demo

### 👤 Usuário 2
- **Email:** `maria.silva@agroadb.com`
- **Senha:** `demo123`
- **Organização:** Silva & Associados

### 👤 Usuário 3
- **Email:** `joao.santos@agroadb.com`
- **Senha:** `demo123`
- **Organização:** Santos Consultoria Rural

## 📊 Dados de Demonstração Incluídos

Cada usuário possui:

- ✅ **2-4 investigações** com diferentes status e prioridades
- ✅ **10-20 propriedades rurais** com CAR, áreas e localizações
- ✅ **5-15 empresas** com CNPJs e dados cadastrais
- ✅ **10-30 contratos** de arrendamento
- ✅ **5-10 notificações** (lidas e não lidas)
- ✅ **5-15 comentários** em investigações
- ✅ Dados de consultas legais simuladas

### Exemplos de Investigações:
- Fazenda Santa Helena (alta prioridade)
- Agropecuária Vale Verde Ltda (análise societária)
- José Carlos Mendes (levantamento patrimonial)
- Fazenda Esperança (regularização ambiental)

## 🎨 Funcionalidades para Testar

### 1. Dashboard
- Visualize estatísticas gerais
- Cards com investigações recentes
- Gráficos de status e prioridades

### 2. Investigações
- Lista completa de investigações
- Filtros por status e prioridade
- Detalhes de cada investigação
- Propriedades, empresas e contratos vinculados

### 3. Notificações
- Sino no navbar mostra notificações não lidas
- Clique para ver detalhes
- Marcar como lida/não lida
- Filtrar por tipo

### 4. Sistema de Busca
- Busca por nome, CPF/CNPJ
- Filtros avançados
- Resultados em tempo real

### 5. Exportação
- Export PDF profissional
- Export Excel/CSV
- Relatórios formatados

### 6. Colaboração
- Comentários em investigações
- Anotações privadas
- Compartilhamento (quando implementado)

### 7. Configurações
- Perfil do usuário
- Configuração de integrações
- Preferências de notificação

## 🛑 Parando a Aplicação

### Windows:
Feche as janelas abertas ou pressione `Ctrl+C` em cada terminal

### Mac/Linux:
```bash
./stop-demo.sh
```

Ou manualmente:
```bash
# Parar backend
pkill -f "uvicorn app.main:app"

# Parar frontend
pkill -f "vite"
```

## 🔄 Resetando os Dados

Para limpar e recriar os dados demo:

```bash
# Deletar banco de dados
rm backend/agroadb.db

# Executar novamente
./start-demo.sh  # ou start-demo.bat no Windows
```

## 📝 Estrutura de Arquivos Criados

Após a primeira execução:

```
agroadb/
├── backend/
│   ├── agroadb.db          # Banco SQLite com dados demo
│   ├── venv/               # Ambiente virtual Python
│   ├── backend.log         # Logs do backend
│   └── .env                # Configurações
└── frontend/
    ├── node_modules/       # Dependências Node.js
    └── frontend.log        # Logs do frontend
```

## ⚠️ Solução de Problemas

### Erro: "Python não encontrado"
- Instale Python 3.11+ de https://www.python.org/downloads/
- No Windows, marque "Add Python to PATH" durante instalação

### Erro: "Node.js não encontrado"
- Instale Node.js 18+ de https://nodejs.org/
- Reinicie o terminal após instalação

### Erro: "Porta 8000 já em uso"
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Erro: "Porta 5173 já em uso"
```bash
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:5173 | xargs kill -9
```

### Banco de dados corrompido
```bash
rm backend/agroadb.db
# Execute o script novamente
```

## 🎓 Próximos Passos

Após testar a demo:

1. **Explorar a documentação da API:** http://localhost:8000/docs
2. **Ler o README.md** para entender a arquitetura
3. **Ver PROXIMOS_PASSOS.md** para roadmap de features
4. **Configurar integrações** em `/settings` (com suas próprias API keys)

## 💡 Dicas

- **Múltiplos usuários:** Teste login com diferentes usuários para ver dados distintos
- **Dados realistas:** Os dados são gerados aleatoriamente mas seguem padrões realistas
- **Performance:** Primeira execução é mais lenta (instalação). Execuções seguintes são rápidas
- **Logs:** Verifique `backend.log` e `frontend.log` em caso de erros

## 📞 Suporte

Em caso de problemas:

1. Verifique os logs (`backend.log`, `frontend.log`)
2. Consulte o README.md principal
3. Verifique se todas as dependências estão instaladas
4. Tente resetar os dados (deletar `agroadb.db`)

## ✨ Características da Demo

- ✅ **Zero configuração:** Funciona out-of-the-box
- ✅ **Dados realistas:** Nomes, endereços, valores simulados
- ✅ **Múltiplos usuários:** 3 contas para testar colaboração
- ✅ **Dados completos:** Investigações com todas as entidades relacionadas
- ✅ **Rápido:** Dados criados automaticamente em segundos
- ✅ **Limpo:** Fácil de resetar e recriar

---

**Pronto para começar? Execute o script e explore o AgroADB!** 🚀
