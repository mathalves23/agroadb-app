# Integrações de Tribunais Estaduais e Birôs de Crédito

## 📋 Visão Geral

Este documento descreve as novas integrações implementadas no AgroADB para consulta de processos judiciais em tribunais estaduais e consultas de crédito em birôs comerciais.

## 🏛️ Tribunais Estaduais

### 1. e-SAJ (Sistema de Automação da Justiça)

**Arquivo**: `backend/app/services/integrations/esaj_service.py`

**Tribunais Suportados**:
- **TJSP** (São Paulo)
- **TJGO** (Goiás)
- **TJMS** (Mato Grosso do Sul)
- **TJSC** (Santa Catarina)
- **TJAL** (Alagoas)
- **TJCE** (Ceará)

**Funcionalidades**:
- `consultar_processos_1g(cpf_cnpj, tribunal)` - Processos de 1º Grau
- `consultar_processos_2g(cpf_cnpj, tribunal)` - Processos de 2º Grau

**Métodos de Busca**:
1. **HTTP Direto**: Tenta primeiro com requisição HTTP simples
2. **Selenium**: Se falhar, usa web scraping com Chrome headless

**Dados Retornados**:
- Número do processo
- Classe e assunto
- Área (cível, criminal, etc)
- Data de distribuição
- Status
- Comarca, foro e vara
- Juiz responsável
- Valor da ação
- Partes envolvidas
- Últimas 10 movimentações

**Endpoints da API**:
```
POST /api/v1/integrations/tribunais/esaj/1g
POST /api/v1/integrations/tribunais/esaj/2g
```

**Exemplo de Requisição**:
```json
{
  "cpf_cnpj": "12345678900",
  "tribunal": "tjsp",
  "investigation_id": 1
}
```

---

### 2. Projudi

**Arquivo**: `backend/app/services/integrations/projudi_service.py`

**Tribunais Suportados**:
- **TJMT** (Mato Grosso)
- **TJPR** (Paraná)
- **TJSC** (Santa Catarina)
- **TJAC** (Acre)
- **TJAM** (Amazonas)
- **TJAP** (Amapá)
- **TJBA** (Bahia)
- **TJGO** (Goiás)
- **TJMA** (Maranhão)
- **TJPA** (Pará)
- **TJPI** (Piauí)
- **TJRN** (Rio Grande do Norte)
- **TJRO** (Rondônia)
- **TJRR** (Roraima)
- **TJTO** (Tocantins)

**Funcionalidades**:
- `consultar_processos(cpf_cnpj, tribunal)` - Consulta processos

**Endpoint da API**:
```
POST /api/v1/integrations/tribunais/projudi
```

**Exemplo de Requisição**:
```json
{
  "cpf_cnpj": "12345678900",
  "tribunal": "tjmt",
  "investigation_id": 1
}
```

---

### 3. PJe (Justiça Federal) - Melhorado

**Arquivo**: `backend/app/services/integrations/pje.py`

**Melhorias Implementadas**:
- Adicionado suporte explícito para TRF1-TRF5
- Novo método `consultar_todos_tribunais(cpf_cnpj)` - busca em todos os TRFs

**Tribunais Regionais Federais**:
- **TRF1**: AC, AM, AP, BA, DF, GO, MA, MG, MT, PA, PI, RO, RR, TO
- **TRF2**: ES, RJ
- **TRF3**: MS, SP
- **TRF4**: PR, RS, SC
- **TRF5**: AL, CE, PB, PE, RN, SE

---

## 💳 Birôs de Crédito

### 1. Serasa Experian

**Arquivo**: `backend/app/services/integrations/serasa_service.py`

**⚠️ ATENÇÃO**: Requer contrato comercial com a Serasa Experian

**Requisitos**:
- Conta empresarial Serasa Experian
- Contrato de uso da API de crédito
- Credenciais OAuth2 (Client ID e Client Secret)

**Configuração** (`.env`):
```env
SERASA_CLIENT_ID=seu_client_id
SERASA_CLIENT_SECRET=seu_client_secret
```

**Funcionalidades**:

1. **Score de Crédito**:
   - `consultar_score(cpf_cnpj)` - Score de 0-1000
   - Faixa de risco
   - Probabilidade de inadimplência

2. **Restrições Financeiras**:
   - `consultar_restricoes(cpf_cnpj)` - Negativações
   - Protestos
   - Ações judiciais
   - Cheques sem fundo
   - Dívidas vencidas

3. **Consultas Recentes**:
   - `consultar_consultas_recentes(cpf_cnpj)` - Quem consultou nos últimos 90 dias

4. **Relatório Completo**:
   - `get_full_report(cpf_cnpj)` - Todos os dados acima consolidados
   - Participação em empresas
   - Histórico completo

**Endpoints da API**:
```
POST /api/v1/integrations/credito/serasa/score
POST /api/v1/integrations/credito/serasa/relatorio
```

**Exemplo de Requisição**:
```json
{
  "cpf_cnpj": "12345678900",
  "investigation_id": 1
}
```

**Exemplo de Resposta (Score)**:
```json
{
  "success": true,
  "score": {
    "score": 650,
    "faixa": "MÉDIO",
    "probabilidade_inadimplencia": 0.25,
    "data_consulta": "2026-02-06T10:30:00"
  }
}
```

---

### 2. Boa Vista SCPC

**Arquivo**: `backend/app/services/integrations/boavista_service.py`

**⚠️ ATENÇÃO**: Requer contrato comercial com a Boa Vista

**Requisitos**:
- Credenciamento Boa Vista SCPC
- Contrato de uso da API
- Certificado digital (em alguns casos)
- Credenciais OAuth2

**Configuração** (`.env`):
```env
BOAVISTA_CLIENT_ID=seu_client_id
BOAVISTA_CLIENT_SECRET=seu_client_secret
```

**Funcionalidades**:

1. **Score de Crédito**:
   - `consultar_score(cpf_cnpj)` - Score e classificação

2. **Restrições**:
   - `consultar_restricoes(cpf_cnpj)` - Restrições financeiras

3. **Consultas Recentes**:
   - `consultar_consultas_recentes(cpf_cnpj)` - Quantidade de consultas

4. **Relatório Completo**:
   - `get_full_report(cpf_cnpj)` - Relatório consolidado
   - Protestos detalhados
   - Cheques sem fundo
   - Ações judiciais
   - Participação em sociedades

**Endpoints da API**:
```
POST /api/v1/integrations/credito/boavista/score
POST /api/v1/integrations/credito/boavista/relatorio
```

**Exemplo de Resposta (Relatório)**:
```json
{
  "success": true,
  "relatorio": {
    "cpf_cnpj": "12345678900",
    "nome": "João da Silva",
    "score": {
      "score": 720,
      "classificacao": "BOM"
    },
    "restricoes_financeiras": [...],
    "protestos": [...],
    "cheques_sem_fundo": [...],
    "acoes_judiciais": [...],
    "participacao_sociedades": [...],
    "consultas_recentes": 15,
    "data_consulta": "2026-02-06T10:30:00"
  }
}
```

---

## 🔧 Configuração

### 1. Variáveis de Ambiente

Adicione ao arquivo `.env`:

```env
# Tribunais Estaduais (Web Scraping)
ESAJ_ENABLED=true
PROJUDI_ENABLED=true

# Serasa Experian (Requer contrato comercial)
SERASA_CLIENT_ID=
SERASA_CLIENT_SECRET=

# Boa Vista SCPC (Requer contrato comercial)
BOAVISTA_CLIENT_ID=
BOAVISTA_CLIENT_SECRET=
```

### 2. Dependências Python

As seguintes dependências são necessárias para web scraping:

```bash
pip install beautifulsoup4 selenium
```

**Chrome Driver**:
- Para Selenium, é necessário ter o ChromeDriver instalado
- Em produção, usar Chrome headless em container Docker

### 3. Docker

Se usar Docker, adicionar ao `Dockerfile`:

```dockerfile
# Instalar Chrome para Selenium
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    && rm -rf /var/lib/apt/lists/*
```

---

## 📊 Uso na Investigação

### Cenário: Investigação Completa

```python
# 1. Consultar processos em tribunais estaduais
processos_sp_1g = await esaj_service.consultar_processos_1g("12345678900", "tjsp")
processos_sp_2g = await esaj_service.consultar_processos_2g("12345678900", "tjsp")
processos_mt = await projudi_service.consultar_processos("12345678900", "tjmt")

# 2. Consultar crédito
serasa_report = await serasa_service.get_full_report("12345678900")
boavista_report = await boavista_service.get_full_report("12345678900")

# 3. Análise consolidada
total_processos = len(processos_sp_1g) + len(processos_sp_2g) + len(processos_mt)
score_medio = (serasa_report.score.score + boavista_report.score.score) / 2

risk_score = calcular_risco(
    processos=total_processos,
    score_credito=score_medio,
    restricoes=len(serasa_report.restricoes) + len(boavista_report.restricoes_financeiras)
)
```

---

## 🚨 Limitações e Considerações

### Tribunais Estaduais

1. **Web Scraping**:
   - Sujeito a mudanças nos sites dos tribunais
   - Pode ser bloqueado por captchas
   - Taxa de sucesso variável

2. **Selenium**:
   - Mais lento que HTTP direto
   - Requer mais recursos (CPU/memória)
   - Necessita ChromeDriver instalado

3. **Rate Limiting**:
   - Respeitar limites de requisições
   - Implementar delays entre consultas
   - Evitar consultas massivas

### Birôs de Crédito

1. **Custos**:
   - Cada consulta tem custo financeiro
   - Contratos com valores mínimos mensais
   - Necessário gestão de orçamento

2. **Compliance**:
   - LGPD: Necessário consentimento para consulta
   - Finalidade legítima (análise de crédito)
   - Manter logs de consultas

3. **Credenciais**:
   - Proteger credenciais (nunca commitar)
   - Usar variáveis de ambiente
   - Rotacionar periodicamente

---

## 📝 Logs e Auditoria

Todas as consultas são registradas:

```python
# Log de auditoria automático
await audit_logger.log_action(
    db=db,
    user_id=current_user.id,
    action="consulta_serasa_score",
    resource_type="credito",
    resource_id=cpf_cnpj,
    details={"score": 650},
    success=True
)
```

Registros salvos em `legal_queries`:
- Provider (esaj_tjsp_1g, serasa, boavista, etc)
- Query type
- Parâmetros
- Contagem de resultados
- Resposta completa

---

## 🧪 Testes

### Testar e-SAJ:
```bash
curl -X POST http://localhost:8000/api/v1/integrations/tribunais/esaj/1g \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpf_cnpj": "12345678900",
    "tribunal": "tjsp"
  }'
```

### Testar Serasa:
```bash
curl -X POST http://localhost:8000/api/v1/integrations/credito/serasa/score \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpf_cnpj": "12345678900"
  }'
```

---

## 📞 Contatos Comerciais

### Serasa Experian
- Site: https://desenvolvedores.serasaexperian.com.br/
- Vendas: (11) 3003-0880
- Email: desenvolvedores@serasaexperian.com.br

### Boa Vista SCPC
- Site: https://developers.boavistaservicos.com.br/
- Vendas: (11) 3003-0999
- Email: comercial@boavistascpc.com.br

---

## ✅ Checklist de Implementação

- [x] Criar `esaj_service.py` com suporte a TJSP, TJGO, TJMS, TJSC, TJAL, TJCE
- [x] Criar `projudi_service.py` com suporte a 15 tribunais
- [x] Melhorar `pje.py` com método `consultar_todos_tribunais()`
- [x] Criar `serasa_service.py` com score, restrições e relatório completo
- [x] Criar `boavista_service.py` com mesma estrutura
- [x] Adicionar configurações no `config.py`
- [x] Criar endpoints REST em `integrations.py`
- [x] Documentar integrações

---

## 📚 Documentação Adicional

- [Documentação Serasa Experian](https://desenvolvedores.serasaexperian.com.br/)
- [Documentação Boa Vista](https://developers.boavistaservicos.com.br/)
- [CNJ - Consulta Processual](https://www.cnj.jus.br/sistemas/consulta-processual/)

---

**Status**: ✅ Integrações tribunais estaduais e birôs de crédito implementadas com sucesso
