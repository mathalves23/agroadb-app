# Analytics & Business Intelligence - AgroADB

Sistema completo de métricas, dashboards e relatórios gerenciais para a plataforma AgroADB.

## 📊 Visão Geral

O módulo Analytics fornece:

- **Métricas em tempo real** - KPIs e indicadores de performance
- **Dashboards interativos** - Visualizações executivas, operacionais e pessoais
- **Relatórios gerenciais** - Relatórios customizados (diários, semanais, mensais, trimestrais, anuais)
- **Integrações BI** - Conectores para Metabase, Power BI, Tableau e outras ferramentas
- **API REST completa** - Endpoints documentados e autenticados

## 🏗️ Arquitetura

```
backend/app/analytics/
├── __init__.py              # MetricsCalculator, AnalyticsAggregator
├── dashboard.py             # DashboardBuilder, ReportGenerator
├── reports.py               # CustomReportBuilder, ReportTemplates
├── bi_integrations.py       # Conectores BI (Metabase, Power BI, Tableau)
└── routes.py                # API REST endpoints
```

## 🚀 Componentes Principais

### 1. **MetricsCalculator**

Calculador de métricas individuais.

**Métodos:**
- `get_overview_metrics()` - Métricas gerais (usuários, investigações)
- `get_usage_metrics()` - Atividade diária, top usuários, tempo de conclusão
- `get_scrapers_metrics()` - Performance dos scrapers
- `get_geographic_metrics()` - Distribuição geográfica
- `get_performance_metrics()` - Performance do sistema (API, DB, Cache)
- `get_financial_metrics()` - Custos, receita, ROI

**Exemplo:**
```python
from app.analytics import MetricsCalculator
from datetime import datetime, timedelta

calculator = MetricsCalculator(db)

# Métricas dos últimos 30 dias
start = datetime.utcnow() - timedelta(days=30)
end = datetime.utcnow()

overview = calculator.get_overview_metrics(start, end)
print(f"Total de usuários ativos: {overview['users']['active']}")
print(f"Taxa de conclusão: {overview['investigations']['completion_rate']}%")
```

### 2. **AnalyticsAggregator**

Agregador de múltiplas métricas para relatórios.

**Métodos:**
- `generate_executive_summary()` - Sumário executivo completo
- `generate_operational_report()` - Relatório operacional
- `get_user_analytics()` - Analytics de usuário específico
- `get_funnel_metrics()` - Funil de conversão

**Exemplo:**
```python
from app.analytics import AnalyticsAggregator

aggregator = AnalyticsAggregator(db)

# Sumário executivo
summary = aggregator.generate_executive_summary()
print(f"Health Score: {summary['health_score']}/100")
print(f"KPIs: {summary['kpis']}")
```

### 3. **DashboardBuilder**

Construtor de dashboards estruturados.

**Métodos:**
- `build_executive_dashboard()` - Dashboard para CEOs/Diretores
- `build_operations_dashboard()` - Dashboard para gerentes
- `build_user_dashboard()` - Dashboard pessoal do usuário
- `build_realtime_dashboard()` - Dashboard em tempo real (24h)

**Exemplo:**
```python
from app.analytics.dashboard import DashboardBuilder

builder = DashboardBuilder(db)

# Dashboard executivo
dashboard = builder.build_executive_dashboard()

# Acessar widgets
for widget in dashboard.widgets:
    print(f"{widget.title}: {widget.type}")
```

### 4. **CustomReportBuilder**

Gerador de relatórios personalizados.

**Tipos de Relatório:**
- `EXECUTIVE` - Visão estratégica
- `OPERATIONAL` - Detalhes operacionais
- `FINANCIAL` - Análise financeira
- `PERFORMANCE` - Performance técnica
- `USAGE` - Análise de engajamento
- `CUSTOM` - Métricas específicas

**Períodos:**
- `TODAY`, `YESTERDAY`
- `LAST_7_DAYS`, `LAST_30_DAYS`
- `THIS_MONTH`, `LAST_MONTH`
- `THIS_QUARTER`, `LAST_QUARTER`
- `THIS_YEAR`, `LAST_YEAR`
- `CUSTOM` (com datas específicas)

**Formatos de Exportação:**
- `JSON` - API REST
- `EXCEL` - Planilhas
- `CSV` - Dados tabulares
- `PDF` - Documentos formatados

**Exemplo:**
```python
from app.analytics.reports import CustomReportBuilder, ReportConfig, ReportType, ReportPeriod, ReportFormat

builder = CustomReportBuilder(db)

config = ReportConfig(
    report_id="relatorio_financeiro",
    title="Relatório Financeiro Mensal",
    report_type=ReportType.FINANCIAL,
    period=ReportPeriod.LAST_MONTH,
    format=ReportFormat.EXCEL
)

report = builder.generate_report(config)
```

### 5. **Integrações BI**

Conectores para ferramentas de Business Intelligence.

#### **Metabase**
```python
from app.analytics.bi_integrations import MetabaseConnector

connector = MetabaseConnector(db)

# Configuração de conexão
config = connector.get_connection_config()

# Queries sugeridas
questions = connector.get_suggested_questions()

# Template de dashboard
template = connector.create_dashboard_template()
```

#### **Power BI**
```python
from app.analytics.bi_integrations import PowerBIConnector

connector = PowerBIConnector(db)

# Exportar dados otimizados
export = connector.export_for_powerbi()

# Medidas DAX
measures = connector._get_powerbi_measures()
```

#### **Tableau**
```python
from app.analytics.bi_integrations import TableauConnector

connector = TableauConnector(db)

# Exportar para Tableau
export = connector.export_for_tableau()

# Campos calculados
calculated_fields = connector._get_tableau_calculated_fields()
```

#### **Universal Adapter**
```python
from app.analytics.bi_integrations import UniversalBIAdapter

adapter = UniversalBIAdapter(db)

# Catálogo de datasets
catalog = adapter.get_dataset_catalog()

# Obter dados de dataset
data = adapter.get_dataset_data("metrics_overview", limit=1000)

# Metadata OData
metadata = adapter.get_odata_metadata()
```

## 📡 API REST

### **Autenticação**

Todos os endpoints requerem autenticação via JWT:

```bash
Authorization: Bearer {seu_token}
```

### **Permissões**

Diferentes níveis de acesso:
- **Público** - Todos os usuários autenticados
- **Manager** - Gerentes e administradores
- **Admin** - Apenas administradores
- **Executive** - Executivos e administradores
- **Finance** - Financeiro e administradores

### **Endpoints**

#### **Métricas Básicas**

```bash
# Overview geral
GET /api/analytics/metrics/overview?start_date=2024-01-01&end_date=2024-01-31

# Métricas de uso
GET /api/analytics/metrics/usage

# Métricas dos scrapers (admin/manager)
GET /api/analytics/metrics/scrapers

# Distribuição geográfica
GET /api/analytics/metrics/geographic

# Performance do sistema (admin)
GET /api/analytics/metrics/performance

# Métricas financeiras (admin/finance)
GET /api/analytics/metrics/financial
```

#### **Dashboards**

```bash
# Dashboard executivo (admin/executive)
GET /api/analytics/dashboards/executive

# Dashboard operacional (admin/manager)
GET /api/analytics/dashboards/operations

# Dashboard pessoal
GET /api/analytics/dashboards/user/{user_id}

# Dashboard em tempo real (admin/manager)
GET /api/analytics/dashboards/realtime
```

#### **Relatórios**

```bash
# Gerar relatório customizado (admin/manager)
POST /api/analytics/reports/generate
Content-Type: application/json
{
  "report_id": "meu_relatorio",
  "title": "Relatório Customizado",
  "report_type": "financial",
  "period": "last_month",
  "format": "excel"
}

# Sumário executivo (admin/executive)
GET /api/analytics/reports/executive-summary

# Relatório operacional (admin/manager)
GET /api/analytics/reports/operational

# Relatório mensal (admin/executive)
GET /api/analytics/reports/monthly/2024/1

# Relatório trimestral (admin/executive)
GET /api/analytics/reports/quarterly/2024/1

# Relatório anual (admin/executive)
GET /api/analytics/reports/annual/2024

# Templates disponíveis (admin/manager)
GET /api/analytics/reports/templates

# Agendar relatório (admin)
POST /api/analytics/reports/schedule

# Métricas de funil (admin/manager)
GET /api/analytics/reports/funnel
```

#### **Integrações BI**

```bash
# Metabase (admin)
GET /api/analytics/bi/metabase/connection

# Power BI (admin)
GET /api/analytics/bi/powerbi/connection
GET /api/analytics/bi/powerbi/export

# Tableau (admin)
GET /api/analytics/bi/tableau/connection
GET /api/analytics/bi/tableau/export

# Datasets (admin)
GET /api/analytics/bi/datasets
GET /api/analytics/bi/datasets/{dataset_name}?limit=1000&offset=0

# OData (admin)
GET /api/analytics/bi/odata/$metadata
```

#### **Analytics de Usuário**

```bash
# Analytics detalhado de usuário
GET /api/analytics/users/{user_id}/analytics
```

#### **Health Check**

```bash
# Status do sistema de analytics
GET /api/analytics/health
```

## 🔧 Configuração

### **Variáveis de Ambiente**

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agroadb

# Auth
JWT_SECRET_KEY=your_secret_key

# Analytics (opcional)
ANALYTICS_CACHE_TTL=300  # Cache em segundos (5 min)
ANALYTICS_MAX_RESULTS=10000  # Limite de resultados
```

### **Inicialização**

```python
# main.py
from app.analytics.routes import router as analytics_router

app = FastAPI()
app.include_router(analytics_router)
```

## 📊 Métricas Coletadas

### **Usuários**
- Total de usuários
- Usuários ativos/inativos
- Novos usuários no período
- Taxa de crescimento

### **Investigações**
- Total de investigações
- Investigações por status (pending, in_progress, completed)
- Taxa de conclusão
- Tempo médio de conclusão
- Atividade diária

### **Scrapers**
- Execuções totais
- Taxa de sucesso/falha
- Duração média
- Performance por scraper

### **Dados Coletados**
- Propriedades encontradas
- Empresas encontradas
- Distribuição geográfica (por estado)
- Área total (hectares)

### **Performance**
- Tempo de resposta da API
- Taxa de erro da API
- Queries lentas do banco
- Taxa de acerto do cache

### **Financeiro**
- Custo por investigação
- MRR (Monthly Recurring Revenue)
- ARR (Annual Recurring Revenue)
- Margem de lucro
- ROI (Return on Investment)

## 📈 KPIs Principais

### **Health Score (0-100)**

Calculado com base em:
- **Taxa de Conclusão** (30 pontos) - % de investigações concluídas
- **Performance da API** (30 pontos) - Baixa taxa de erro
- **Margem de Lucro** (40 pontos) - Lucratividade

### **Interpretação:**
- **90-100**: Excelente (verde)
- **75-89**: Bom (verde claro)
- **50-74**: Razoável (amarelo)
- **0-49**: Ruim (vermelho)

## 🎯 Casos de Uso

### **CEO / Diretor Executivo**

```bash
# Dashboard executivo com KPIs principais
GET /api/analytics/dashboards/executive

# Relatório trimestral
GET /api/analytics/reports/quarterly/2024/1
```

### **Gerente de Operações**

```bash
# Dashboard operacional
GET /api/analytics/dashboards/operations

# Relatório diário
GET /api/analytics/reports/operational
```

### **Gerente Financeiro**

```bash
# Métricas financeiras
GET /api/analytics/metrics/financial

# Relatório financeiro mensal
GET /api/analytics/reports/monthly/2024/1
```

### **Product Manager**

```bash
# Métricas de uso
GET /api/analytics/metrics/usage

# Funil de conversão
GET /api/analytics/reports/funnel
```

### **Usuário Final**

```bash
# Dashboard pessoal
GET /api/analytics/dashboards/user/{meu_id}

# Minhas analytics
GET /api/analytics/users/{meu_id}/analytics
```

## 🔌 Integração com Ferramentas BI

### **Metabase**

1. Acesse o endpoint de configuração:
```bash
GET /api/analytics/bi/metabase/connection
```

2. No Metabase:
   - Admin > Databases > Add Database
   - Tipo: PostgreSQL
   - Preencha host, port, database, user, password
   - Save

3. Use as queries sugeridas fornecidas pela API

### **Power BI**

1. Obtenha a configuração:
```bash
GET /api/analytics/bi/powerbi/connection
```

2. No Power BI Desktop:
   - Get Data > Database > PostgreSQL
   - Preencha server e database
   - Escolha DirectQuery ou Import

3. Ou use a API REST:
   - Get Data > Web
   - URL: `https://api.agroadb.com/api/analytics/bi/powerbi/export`
   - Autenticação: Bearer token

### **Tableau**

1. Obtenha a configuração:
```bash
GET /api/analytics/bi/tableau/connection
```

2. No Tableau Desktop:
   - Connect > To a Server > PostgreSQL
   - Preencha server, database, user, password

3. Ou use Web Data Connector:
   - Connect > To a Server > Web Data Connector
   - URL: `https://api.agroadb.com/api/analytics/bi/datasets`

### **Qualquer Ferramenta (via API REST)**

```bash
# Listar datasets disponíveis
GET /api/analytics/bi/datasets

# Obter dados
GET /api/analytics/bi/datasets/metrics_overview
GET /api/analytics/bi/datasets/daily_activity?limit=1000
```

## 🧪 Testes

### **Executar Testes**

```bash
# Todos os testes
pytest backend/tests/test_analytics.py -v

# Testes específicos
pytest backend/tests/test_analytics.py::TestMetricsCalculator -v

# Com cobertura
pytest backend/tests/test_analytics.py --cov=app.analytics --cov-report=html
```

### **Testes de Integração**

```bash
pytest backend/tests/test_analytics.py -v -m integration
```

### **Testes de Performance**

```bash
pytest backend/tests/test_analytics.py -v -m performance
```

## 📋 Checklist de Implementação

- [x] Sistema de métricas (MetricsCalculator)
- [x] Agregador de analytics (AnalyticsAggregator)
- [x] Dashboard builder (DashboardBuilder)
- [x] Gerador de relatórios (ReportGenerator)
- [x] Relatórios customizados (CustomReportBuilder)
- [x] Templates de relatórios (ReportTemplates)
- [x] Agendamento de relatórios (ScheduledReports)
- [x] Integração Metabase (MetabaseConnector)
- [x] Integração Power BI (PowerBIConnector)
- [x] Integração Tableau (TableauConnector)
- [x] Adaptador universal (UniversalBIAdapter)
- [x] API REST completa (routes.py)
- [x] Testes automatizados
- [x] Documentação

## 🚧 Melhorias Futuras

### **Curto Prazo**
- [ ] Cache Redis para métricas frequentes
- [ ] Exportação real para PDF (com templates)
- [ ] Envio automático de relatórios por email
- [ ] Alertas baseados em thresholds

### **Médio Prazo**
- [ ] Machine Learning para previsões
- [ ] Análise de tendências
- [ ] Comparação com períodos anteriores
- [ ] Cohort analysis

### **Longo Prazo**
- [ ] Data warehouse dedicado
- [ ] Real-time streaming analytics
- [ ] Análise preditiva avançada
- [ ] Integração com Google Analytics

## 📞 Suporte

Para questões ou problemas:
- Email: suporte@agroadb.com
- Documentação: https://docs.agroadb.com/analytics
- Issues: https://github.com/agroadb/agroadb/issues

## 📄 Licença

Copyright © 2024 AgroADB. Todos os direitos reservados.
