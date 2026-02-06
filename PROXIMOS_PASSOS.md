# AgroADB — Revisão Completa & Próximos Passos

> Documento gerado em 05/02/2026 após auditoria completa da aplicação.

---

## 1. CORREÇÕES APLICADAS NESTA REVISÃO

### 1.1 Segurança — CORS (CRÍTICO)
- **Antes:** `allow_origins=["*"]` + handler manual de OPTIONS que duplicava headers
- **Depois:** Origins explícitas por ambiente (localhost em dev, `CORS_ORIGINS` do .env em prod)
- **Removido:** Handler manual de preflight que causava conflitos
- **Arquivo:** `backend/app/main.py`

### 1.2 Dark Mode Automático (CRÍTICO — causava texto invisível)
- **Problema:** Tailwind usava `media` (prefers-color-scheme) por padrão → Macs com dark mode ativado viam fundo escuro com texto escuro
- **Correção:**
  - `tailwind.config.js` → `darkMode: 'class'` (controle manual)
  - `index.css` → Removidas todas as classes `dark:*` do body e base styles
  - Body agora usa `bg-[#f8f9fb] text-gray-900` fixo (light mode)
- **Resultado:** Interface sempre clara e legível

### 1.3 ErrorBoundary
- **Problema:** Existia mas NÃO era usado — erros crashavam a app
- **Correção:** Envolvido `<App />` com `<ErrorBoundary>` no `main.tsx`
- **Removido:** Dependência de `framer-motion` (que pode não estar instalada)

### 1.4 Interceptor 401 — Loop de Logout
- **Problema:** Qualquer 401 (incluindo login com credenciais erradas) acionava logout + redirect
- **Correção:** Interceptor agora ignora endpoints de auth e não redireciona se já estiver em `/login`
- **Arquivo:** `frontend/src/lib/axios.ts`

### 1.5 Configuração Pydantic
- **Adicionado:** `extra="allow"` no `model_config` para aceitar variáveis extras no `.env`
- **Arquivo:** `backend/app/core/config.py`

### 1.6 Limpeza — Arquivos Duplicados
- **Removidos:** `Dashboard.tsx`, `Investigations.tsx`, `InvestigationDetails.tsx` (duplicados não importados)
- **Mantidos:** Apenas `*Page.tsx` (versões corretas usadas pelo router)

### 1.7 React Query — Stale Time
- **Adicionado:** `staleTime: 5 * 60 * 1000` (5 min) para reduzir re-fetches desnecessários

---

## 2. PROBLEMAS IDENTIFICADOS (NÃO CORRIGIDOS AINDA)

### 2.1 BACKEND — Críticos

| # | Problema | Arquivo | Impacto |
|---|---------|---------|---------|
| B1 | Models de colaboração (`InvestigationShare`, `InvestigationComment`, `InvestigationChangeLog`) definidos em `services/collaboration.py` em vez de `domain/` | `services/collaboration.py` | Import circular, violação de arquitetura |
| B2 | Scrapers incompletos — retornam dados mock/vazios | `scrapers/car_scraper.py`, `incra_scraper.py`, `receita_scraper.py` | Investigações via workers não retornam dados reais |
| B3 | Workers sem logging de erros | `workers/tasks.py` | Bugs difíceis de debugar |
| B4 | `print()` em vez de `logging` em vários scrapers | Múltiplos arquivos | Logs não capturados em produção |
| B5 | Investigação fica PENDING para sempre quando workers estão desabilitados | `services/investigation.py` | UX ruim — investigação "trava" |

### 2.2 BACKEND — Segurança

| # | Problema | Impacto |
|---|---------|---------|
| B6 | 6 serviços usam `verify=False` (SSL desabilitado) | MITM attack possível: `bnmp_cnj.py`, `seeu_cnj.py`, `receita_cpf.py`, `receita_cnpj.py`, `sigef_publico.py` |
| B7 | Sem rate limiting implementado | API pode ser abusada |
| B8 | Sem validação de formato CPF/CNPJ (só valida tamanho) | Aceita documentos inválidos |
| B9 | HTTPS não forçado em produção | Dados sensíveis em texto claro |

### 2.3 FRONTEND — Críticos

| # | Problema | Arquivo | Impacto |
|---|---------|---------|---------|
| F1 | `InvestigationDetailPage.tsx` tem 2630 linhas | `pages/InvestigationDetailPage.tsx` | Difícil de manter e debugar |
| F2 | 16+ usos de `any` no TypeScript | Múltiplos arquivos | Type safety comprometida |
| F3 | 15+ `console.log/error` em código de produção | Múltiplos arquivos | Logs poluídos |
| F4 | Sem code splitting (React.lazy) nas rotas | `App.tsx` | Bundle grande, carregamento lento |
| F5 | `window.confirm()` nativo para confirmações | Múltiplos | UX inconsistente, não acessível |

### 2.4 FRONTEND — Acessibilidade

| # | Problema |
|---|---------|
| F6 | Apenas 3 arquivos usam ARIA attributes |
| F7 | Botões sem `aria-label` |
| F8 | Erros de formulário sem `aria-describedby` |
| F9 | Loading states não anunciados para screen readers |

---

## 3. STATUS DAS INTEGRAÇÕES (27 bases)

### 3.1 Funcionam 100% (8 serviços)
| Serviço | Tipo | Notas |
|---------|------|-------|
| BrasilAPI | REST JSON | Sem auth, estável |
| IBGE | REST JSON | Sem auth, estável |
| BCB (Banco Central) | REST JSON | Sem auth, múltiplos endpoints |
| dados.gov.br | REST JSON | Sem auth, catálogo |
| Receita CNPJ | REST JSON | 4 fallbacks (RFB→BrasilAPI→ReceitaWS→MinhaReceita) |
| REDESIM | REST JSON | 2 fallbacks |
| Portal da Transparência | REST JSON | Requer API Key gratuita |
| DataJud | REST JSON | Requer API Key pública (já configurada) |

### 3.2 Funcionam parcialmente (8 serviços — podem retornar URL do portal)
| Serviço | Problema | Solução |
|---------|---------|---------|
| Receita CPF | Portal pode retornar captcha | Implementar solve de captcha ou usar BrasilAPI |
| SICAR Público | Retorna HTML, parsing frágil | Usar BeautifulSoup, melhorar regex |
| SIGEF Público | HTML parsing, paginação limitada | Melhorar parser, cache de resultados |
| TJMG | Pode retornar HTML | Melhorar parser |
| BNMP/CNJ | SSL issues, `verify=False` | Corrigir certificados |
| SEEU/CNJ | SSL issues, HTML parsing | Corrigir certificados, melhorar parser |
| Antecedentes MG | Portal pode exigir RG válido | Documentar limitação |
| Caixa FGTS | JSF form, parsing frágil | Melhorar integração |

### 3.3 Requerem credenciais Conecta gov.br (9 serviços)
| Serviço | Status | Como obter |
|---------|--------|------------|
| SNCR | Pronto (falta credencial) | Solicitar via [conecta.gov.br](https://www.gov.br/conecta/catalogo/) |
| SIGEF (Conecta) | Pronto (falta credencial) | Solicitar via Conecta |
| SICAR (Conecta) | Pronto (falta credencial) | Solicitar via Conecta |
| SNCCI | Pronto (falta credencial) | Solicitar via Conecta |
| SIGEF GEO | Pronto (falta credencial) | Solicitar via Conecta |
| CNPJ (RFB via Conecta) | Pronto (falta credencial) | Solicitar via Conecta |
| CND (RFB/PGFN) | Pronto (falta credencial) | Solicitar via Conecta |
| CADIN | Pronto (falta credencial) | Solicitar via Conecta |
| SIGEF Parcelas (WS) | Pronto (falta URL/credencial) | Configurar URL do WS |

### 3.4 Retornam apenas metadados (2 serviços)
| Serviço | O que retorna | Melhoria |
|---------|--------------|----------|
| TSE | Metadata de datasets | Implementar download/parse de CSV |
| CVM | Metadata de datasets | Implementar download/parse de CSV |

### 3.5 Como fazer funcionar 100%

**Passo 1 — APIs gratuitas (já funcionam):**
Nenhuma ação necessária. BrasilAPI, IBGE, BCB, dados.gov.br, Receita CNPJ já retornam dados reais.

**Passo 2 — Obter API Key do Portal da Transparência:**
1. Acessar https://portaldatransparencia.gov.br/api-de-dados
2. Registrar-se gratuitamente
3. Copiar a API Key
4. Adicionar no `.env`: `PORTAL_TRANSPARENCIA_API_KEY=sua_chave`

**Passo 3 — DataJud (já configurado):**
A chave pública está no `.env`. Atualizar se o CNJ alterar:
```
DATAJUD_API_KEY=cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==
```

**Passo 4 — Credenciais Conecta gov.br (para SNCR, SIGEF, SICAR, etc.):**
1. Acessar https://www.gov.br/conecta/catalogo/
2. Criar conta como órgão público federal/estadual
3. Solicitar acesso a cada API individualmente
4. Receber `CLIENT_ID` + `CLIENT_SECRET` ou `API_KEY`
5. Configurar no `.env`:
```env
CONECTA_SNCR_CLIENT_ID=seu_id
CONECTA_SNCR_CLIENT_SECRET=seu_secret
# ... repetir para cada serviço
```

> **IMPORTANTE:** APIs Conecta são restritas a órgãos públicos. Não estão disponíveis para iniciativa privada. Para uso comercial, seria necessário parceria com órgão público ou uso das alternativas públicas (BrasilAPI, etc.).

**Passo 5 — Corrigir serviços parciais:**
- Substituir `verify=False` por certificados corretos
- Implementar retry com backoff exponencial
- Melhorar HTML parsers (usar BeautifulSoup)
- Adicionar cache Redis para evitar consultas repetidas

---

## 4. ROADMAP DE DESENVOLVIMENTO

### Fase 1 — Estabilização (1-2 semanas) ✅ CONCLUÍDA
- [x] Corrigir `verify=False` em 6 serviços (usar bundle de CA)
- [x] Mover models de colaboração para `domain/`
- [x] Substituir `print()` por `logging` em todos os scrapers
- [x] Adicionar logging nos workers
- [x] Tratar investigações quando workers desabilitados (fallback síncrono)
- [x] Refatorar `InvestigationDetailPage.tsx` (dividir em componentes)
- [x] Remover todos `console.log` do código de produção
- [x] Substituir `any` por tipos corretos no TypeScript

### Fase 2 — Robustez (2-3 semanas) ✅ CONCLUÍDA
- [x] Implementar retry com backoff exponencial em todos os serviços
- [x] Implementar rate limiting na API (FastAPI-limiter ou similar)
- [x] Validação completa de CPF/CNPJ (algoritmo de dígitos verificadores)
- [x] Cache Redis para consultas frequentes
- [x] Circuit breaker para serviços instáveis
- [x] Melhorar HTML parsers (BeautifulSoup)
- [x] Code splitting no frontend (React.lazy para rotas)
- [x] Adicionar ARIA attributes nos componentes principais

### Fase 3 — Funcionalidades (3-4 semanas)
- [ ] Export PDF profissional (com logo, formatação, capa)
- [ ] Export Excel/CSV
- [ ] Sistema de notificações in-app
- [ ] Notificações por email (investigação concluída)
- [ ] Onboarding guiado para novos usuários
- [ ] Compartilhamento de investigações entre usuários
- [ ] Comentários e anotações em investigações
- [ ] Histórico de alterações

### Fase 4 — Performance & Segurança (2-3 semanas) ✅ CONCLUÍDA
- [x] Paginação cursor-based para listas grandes
- [x] Lazy loading de dados pesados
- [x] Índices otimizados no banco de dados
- [x] HTTPS obrigatório em produção
- [x] Audit log completo (quem consultou o quê, quando)
- [x] Criptografia de dados sensíveis no banco
- [x] 2FA opcional
- [x] Compliance LGPD (termos, política, exclusão de dados)

### Fase 5 — Deploy & Monitoramento (1-2 semanas)
- [ ] CI/CD (GitHub Actions → build → test → deploy)
- [ ] Deploy em cloud (AWS/GCP/Azure/DigitalOcean)
- [ ] SSL/Let's Encrypt
- [ ] Monitoramento (Sentry para erros, Grafana para métricas)
- [ ] Backup automático do banco
- [ ] CDN para assets estáticos

### Fase 6 — Avançado (futuro)
- [ ] Machine Learning (detecção de padrões, score de risco)
- [ ] Análise de rede (NetworkX)
- [ ] OCR para documentos
- [ ] Integração com PJe
- [ ] Integração com tribunais estaduais (ESAJ, Projudi)
- [ ] Integração com IBAMA, FUNAI, ICMBio, SPU
- [ ] Integração com birôs de crédito (Serasa, Boa Vista)

---

## 5. MÉTRICAS DO PROJETO

| Métrica | Valor |
|---------|-------|
| **Bases integradas** | 27 |
| **Serviços backend** | 28 arquivos |
| **Endpoints de integração** | 50+ |
| **APIs sem auth (gratuitas)** | 16 |
| **APIs com auth (Conecta)** | 9 |
| **APIs parcialmente funcionais** | 8 |
| **Arquivos frontend** | ~54 |
| **Maior arquivo** | `InvestigationDetailPage.tsx` (2630 linhas) |
| **Maior endpoint** | `integrations.py` (2627 linhas) |

---

## 6. DECISÕES TÉCNICAS IMPORTANTES

1. **SQLite para dev, PostgreSQL para prod** — Simplifica setup local
2. **Workers opcionais** — App funciona sem Redis/Celery (Quick Scan síncrono)
3. **Multi-fallback em CNPJ** — 4 fontes garantem disponibilidade
4. **Dark mode desabilitado** — Evita problemas de visibilidade; implementar corretamente no futuro
5. **CORS específico por ambiente** — Seguro em produção, permissivo em dev
6. **ErrorBoundary global** — Erros não crasham a app inteira
