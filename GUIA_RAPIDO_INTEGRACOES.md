# 🚀 Guia Rápido - Integrações Tribunais e Birôs de Crédito

## ⚡ Início Rápido (5 minutos)

### 1. Instalar Dependências
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar Variáveis (.env)
```env
# Tribunais (não precisa configurar nada)
ESAJ_ENABLED=true
PROJUDI_ENABLED=true

# Birôs de Crédito (opcional - só se tiver contrato)
# SERASA_CLIENT_ID=seu_id
# SERASA_CLIENT_SECRET=seu_secret
# BOAVISTA_CLIENT_ID=seu_id
# BOAVISTA_CLIENT_SECRET=seu_secret
```

### 3. Instalar ChromeDriver
```bash
# macOS
brew install chromedriver

# Ubuntu/Debian
sudo apt-get install chromium-driver

# Ou automático
pip install webdriver-manager
```

---

## 📞 Como Usar - Tribunais Estaduais

### e-SAJ (TJSP, TJGO, TJMS, etc)

#### 1º Grau
```bash
curl -X POST http://localhost:8000/api/v1/integrations/tribunais/esaj/1g \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpf_cnpj": "12345678900",
    "tribunal": "tjsp"
  }'
```

#### 2º Grau
```bash
curl -X POST http://localhost:8000/api/v1/integrations/tribunais/esaj/2g \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpf_cnpj": "12345678900",
    "tribunal": "tjsp"
  }'
```

**Tribunais Disponíveis**: tjsp, tjgo, tjms, tjsc, tjal, tjce

---

### Projudi (TJMT, TJPR, etc)

```bash
curl -X POST http://localhost:8000/api/v1/integrations/tribunais/projudi \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpf_cnpj": "12345678900",
    "tribunal": "tjmt"
  }'
```

**Tribunais Disponíveis**: tjmt, tjpr, tjsc, tjac, tjam, tjap, tjba, tjgo, tjma, tjpa, tjpi, tjrn, tjro, tjrr, tjto

---

## 💳 Como Usar - Birôs de Crédito

### Serasa - Score

```bash
curl -X POST http://localhost:8000/api/v1/integrations/credito/serasa/score \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpf_cnpj": "12345678900"
  }'
```

**Resposta**:
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

### Serasa - Relatório Completo

```bash
curl -X POST http://localhost:8000/api/v1/integrations/credito/serasa/relatorio \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpf_cnpj": "12345678900"
  }'
```

### Boa Vista - Score

```bash
curl -X POST http://localhost:8000/api/v1/integrations/credito/boavista/score \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpf_cnpj": "12345678900"
  }'
```

### Boa Vista - Relatório Completo

```bash
curl -X POST http://localhost:8000/api/v1/integrations/credito/boavista/relatorio \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpf_cnpj": "12345678900"
  }'
```

---

## 🐍 Uso em Python

### Tribunais

```python
from backend.app.services.integrations.esaj_service import ESAJService

async def consultar_tjsp():
    async with ESAJService() as service:
        # 1º Grau
        processos_1g = await service.consultar_processos_1g(
            "12345678900",
            "tjsp"
        )
        
        # 2º Grau
        processos_2g = await service.consultar_processos_2g(
            "12345678900",
            "tjsp"
        )
        
        print(f"Total: {len(processos_1g) + len(processos_2g)} processos")
```

### Birôs

```python
from backend.app.services.integrations.serasa_service import SerasaService

async def consultar_serasa():
    async with SerasaService() as service:
        # Score
        score = await service.consultar_score("12345678900")
        print(f"Score: {score.score}")
        
        # Relatório completo
        report = await service.get_full_report("12345678900")
        print(f"Restrições: {len(report.restricoes)}")
```

---

## 🔍 Exemplo Completo - Investigação

```python
async def investigacao_completa(cpf_cnpj: str):
    """Busca completa: tribunais + crédito"""
    
    # 1. Tribunais Estaduais
    async with ESAJService() as esaj:
        tjsp_1g = await esaj.consultar_processos_1g(cpf_cnpj, "tjsp")
        tjsp_2g = await esaj.consultar_processos_2g(cpf_cnpj, "tjsp")
    
    async with ProjudiService() as projudi:
        tjmt = await projudi.consultar_processos(cpf_cnpj, "tjmt")
    
    # 2. Justiça Federal
    async with PJeIntegration() as pje:
        federais = await pje.consultar_todos_tribunais(cpf_cnpj)
    
    # 3. Birôs de Crédito
    async with SerasaService() as serasa:
        serasa_report = await serasa.get_full_report(cpf_cnpj)
    
    async with BoaVistaService() as boavista:
        boavista_report = await boavista.get_full_report(cpf_cnpj)
    
    # 4. Consolidar
    resultado = {
        "processos": {
            "estaduais_1g": len(tjsp_1g),
            "estaduais_2g": len(tjsp_2g),
            "projudi": len(tjmt),
            "federais": sum(len(p) for p in federais.values())
        },
        "credito": {
            "serasa_score": serasa_report.score.score if serasa_report else None,
            "serasa_restricoes": len(serasa_report.restricoes) if serasa_report else 0,
            "boavista_score": boavista_report.score.score if boavista_report else None,
            "boavista_restricoes": len(boavista_report.restricoes_financeiras) if boavista_report else 0
        }
    }
    
    return resultado
```

---

## 🧪 Testar Instalação

```bash
# 1. Verificar dependências
python check_dependencies.py

# 2. Executar testes
python test_integrations.py

# 3. Testar endpoint específico
curl http://localhost:8000/api/v1/integrations/status
```

---

## ⚠️ Avisos Importantes

### Tribunais (Web Scraping)
- ⚡ **Pode ser lento** (5-30 segundos por consulta)
- 🚫 **Captchas podem bloquear** consultas
- ⏱️ **Rate limiting**: Evite consultas massivas
- 🔄 **Selenium como fallback** quando HTTP falha

### Birôs de Crédito
- 💰 **Custos por consulta** - cada consulta é cobrada
- 🔑 **Credenciais obrigatórias** - contrato comercial
- 📜 **LGPD**: Necessário consentimento do titular
- 🎯 **Finalidade legítima** - análise de crédito

---

## 🐛 Troubleshooting Rápido

### "ChromeDriver not found"
```bash
pip install webdriver-manager
```

### "Credenciais não configuradas"
- Configure no `.env`
- Ou ignore se não tiver contrato

### "Timeout" nas consultas
- Tribunais podem estar lentos
- Aumentar timeout no código
- Tentar novamente mais tarde

### "Captcha detectado"
- Normal em alguns tribunais
- Selenium tentará resolver
- Pode falhar em alguns casos

---

## 📊 Documentação Completa

- 📖 **Guia Detalhado**: `docs/dev/integracoes-tribunais-credito.md`
- 🔧 **Instalação**: `docs/dev/instalacao-dependencias-scraping.md`
- ✅ **Resumo**: `INTEGRAÇÕES_IMPLEMENTADAS.md`

---

## 💬 Suporte

### Problemas Técnicos
- Verificar logs do backend
- Consultar documentação
- Testar com `test_integrations.py`

### Contratar Birôs
- **Serasa**: (11) 3003-0880
- **Boa Vista**: (11) 3003-0999

---

## ✅ Checklist de Uso

- [ ] Dependências instaladas
- [ ] ChromeDriver configurado
- [ ] .env configurado
- [ ] Backend rodando
- [ ] Token de autenticação obtido
- [ ] Primeiro teste executado com sucesso

---

**Pronto!** 🎉

Você está pronto para usar as integrações de tribunais estaduais e birôs de crédito no AgroADB.
