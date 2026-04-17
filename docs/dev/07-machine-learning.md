# Machine Learning e Análise de Rede - AgroADB

## 📊 Visão Geral

Este documento descreve as funcionalidades de Machine Learning e Análise de Rede implementadas no AgroADB para detecção automática de padrões suspeitos e cálculo de score de risco.

---

## 🎯 Funcionalidades Implementadas

### 1. **Score de Risco (Risk Scoring)**

Sistema de pontuação de risco (0-100) baseado em múltiplos indicadores:

**Indicadores Analisados:**
- ✅ **Concentração de Propriedades** (peso: 15%)
  - Quantidade de propriedades
  - Área total em hectares
  - Dispersão geográfica (estados)

- ✅ **Valor de Contratos** (peso: 20%)
  - Valor total de arrendamentos
  - Quantidade de contratos
  - Detecção de valores atípicos (outliers)

- ✅ **Questões Judiciais** (peso: 25%)
  - Número de processos ativos
  - Presença de palavras-chave críticas (fraude, corrupção, grilagem)

- ✅ **Rede de Empresas** (peso: 15%)
  - Quantidade de empresas
  - Taxa de empresas inativas
  - Dispersão geográfica

- ✅ **Padrões Temporais** (peso: 10%)
  - Empresas criadas em sequência rápida
  - Propriedades registradas recentemente

- ✅ **Dispersão Geográfica** (peso: 10%)
  - Propriedades em múltiplos estados
  - Propriedades em múltiplas cidades

- ✅ **Qualidade dos Dados** (peso: 5%)
  - Completude dos campos
  - Dados faltantes

**Níveis de Risco:**
- 0-20: Muito Baixo (very_low)
- 20-40: Baixo (low)
- 40-60: Médio (medium)
- 60-80: Alto (high)
- 80-100: Crítico (critical)

**Endpoint:**
```
GET /api/v1/investigations/{investigation_id}/risk-score
```

**Exemplo de Resposta:**
```json
{
  "total_score": 67.5,
  "risk_level": "high",
  "confidence": 0.85,
  "indicators": [
    {
      "name": "property_concentration",
      "value": 75,
      "weight": 0.15,
      "description": "Concentração de propriedades rurais",
      "severity": "high"
    }
  ],
  "patterns_detected": [
    "Alta concentração: 52 propriedades",
    "Área total crítica: 150.000 hectares"
  ],
  "recommendations": [
    "⚠️ Investigação prioritária: risco elevado detectado",
    "🏞️ Investigar origem e legitimidade das propriedades"
  ],
  "timestamp": "2026-02-06T10:30:00"
}
```

---

### 2. **Detecção de Padrões (Pattern Detection)**

Identificação automática de comportamentos suspeitos usando algoritmos de ML:

**Padrões Detectados:**

#### 🚨 **Laranjas (Empresas de Fachada)**
- Múltiplas empresas no mesmo endereço (5+ empresas)
- Capital social muito baixo (< R$ 10.000)
- Empresas abertas em sequência rápida (< 30 dias)

#### 🔗 **Rede Suspeita de Empresas**
- Alta proporção de empresas inativas (> 40%)
- Muitas empresas com mesma atividade (possível cartel)

#### 🔄 **Transações Circulares**
- Ciclos de transações entre empresas (A → B → A)
- Indício de lavagem de dinheiro

#### 📍 **Concentração Anormal**
- Concentração geográfica anormal (15+ propriedades na mesma cidade)
- Propriedades com área muito acima da média (outliers estatísticos)

#### ⏰ **Anomalias Temporais**
- Empresas abertas em fins de semana
- Múltiplas empresas abertas no mesmo dia (5+)

**Endpoint:**
```
GET /api/v1/investigations/{investigation_id}/patterns
```

**Exemplo de Resposta:**
```json
{
  "patterns": [
    {
      "type": "laranja_same_address",
      "confidence": 0.85,
      "description": "7 empresas no mesmo endereço",
      "severity": "high",
      "entities": [123, 456, 789],
      "evidence": {
        "address": "Rua das Flores, 100 - São Paulo/SP",
        "num_companies": 7,
        "companies": ["Empresa A Ltda", "Empresa B Ltda"]
      }
    }
  ],
  "total_patterns": 12,
  "critical_patterns": 3
}
```

---

### 3. **Análise de Rede (Network Analysis)**

Mapeamento e análise de relacionamentos usando NetworkX:

**Componentes:**
- **Nós**: Empresas, propriedades, pessoas
- **Arestas**: owns (propriedade), leases (arrendamento), partner_in (sócios)

**Métricas Calculadas:**
- **Centralidade**: Identifica nós mais importantes (degree + betweenness)
- **Comunidades**: Detecta grupos fortemente conectados (Greedy Modularity)
- **Densidade**: Mede conectividade da rede (0-1)
- **Clusters**: Conta componentes desconectados
- **Jogadores-Chave**: Top 10 entidades mais influentes

**Padrões de Rede Detectados:**
- Nós isolados (sem conexões)
- Hubs (nós com muitas conexões)
- Pontes (conexões críticas entre comunidades)
- Cliques (grupos totalmente conectados)
- Densidade anormal (muito densa ou muito esparsa)

**Endpoint:**
```
GET /api/v1/investigations/{investigation_id}/network
```

**Exemplo de Resposta:**
```json
{
  "num_nodes": 45,
  "num_edges": 67,
  "density": 0.0356,
  "central_nodes": [
    {"node_id": "company_123", "centrality": 0.85}
  ],
  "communities": [
    {"size": 12, "nodes": ["company_1", "property_5"]}
  ],
  "clusters": 3,
  "key_players": [
    "Empresa ABC Ltda (company) - Score: 0.850",
    "Fazenda Santa Clara (property) - Score: 0.742"
  ],
  "suspicious_patterns": [
    "🔍 15 hubs detectados (nós com muitas conexões)",
    "🌉 23 pontes detectadas (conexões críticas)"
  ],
  "graph_data": {
    "nodes": [
      {
        "id": "company_123",
        "label": "Empresa ABC Ltda",
        "type": "company",
        "attributes": {"cnpj": "12345678000190", "status": "ATIVA"}
      }
    ],
    "edges": [
      {
        "source": "company_123",
        "target": "property_456",
        "type": "owns",
        "weight": 1.0
      }
    ],
    "metadata": {
      "num_nodes": 45,
      "num_edges": 67,
      "density": 0.0356,
      "is_connected": false
    }
  }
}
```

---

### 4. **Análise Abrangente (Comprehensive Analysis)**

Executa todas as análises em paralelo para otimização de performance:

**Endpoint:**
```
GET /api/v1/investigations/{investigation_id}/comprehensive-analysis
```

**Exemplo de Resposta:**
```json
{
  "investigation_id": 42,
  "risk": {
    "score": 67.5,
    "level": "high",
    "confidence": 0.85,
    "recommendations": ["⚠️ Investigação prioritária"]
  },
  "patterns": {
    "total": 12,
    "critical": 3,
    "types": ["laranja_same_address", "circular_transactions"]
  },
  "network": {
    "nodes": 45,
    "edges": 67,
    "density": 0.0356,
    "clusters": 3,
    "key_players_count": 10
  },
  "overall_assessment": {
    "assessment": "ALTO RISCO",
    "color": "orange",
    "critical_alerts": 4,
    "requires_manual_review": true
  }
}
```

---

## 🎨 Frontend - Visualização

### Aba "Rede de Relacionamentos"
- Grafo interativo 2D usando `react-force-graph-2d`
- Cores por tipo: 🏢 Empresas (azul), 🏞️ Propriedades (verde), 👤 Pessoas (amarelo)
- Tamanho dos nós baseado em número de conexões
- Clique em um nó para destacar suas conexões
- Zoom e pan para navegação

### Aba "Análise ML"

#### Card de Score de Risco:
- Medidor visual circular (0-100)
- Nível de risco com cores semânticas
- Barra de progresso com escala
- Lista de indicadores com peso e severidade
- Padrões detectados
- Recomendações automáticas

#### Card de Detecção de Padrões:
- Resumo de padrões por severidade (crítico, alto, médio, baixo)
- Cards agrupados por severidade
- Confiança de cada padrão (0-100%)
- Evidências detalhadas
- Entidades envolvidas

---

## 🔧 Tecnologias Utilizadas

### Backend:
- **scikit-learn**: Machine Learning (clustering, detecção de outliers)
- **NetworkX**: Análise de grafos e redes sociais
- **NumPy**: Operações numéricas
- **SciPy**: Análises estatísticas

### Frontend:
- **React + TypeScript**: Framework principal
- **react-force-graph-2d**: Visualização de grafos
- **TanStack Query**: Gerenciamento de estado assíncrono
- **Tailwind CSS**: Estilização

---

## 📦 Instalação

### Backend:

```bash
cd backend
pip install -r requirements.txt
```

As dependências ML já estão no `requirements.txt`:
```
scikit-learn==1.4.0
networkx==3.2.1
scipy==1.11.4
numpy==1.26.3
```

### Frontend:

```bash
cd frontend
npm install
```

A biblioteca de visualização já está no `package.json`:
```json
{
  "dependencies": {
    "react-force-graph-2d": "^1.25.4"
  }
}
```

### Migrations:

Adicionar campo `capital` à tabela `companies`:

```bash
cd backend
alembic upgrade head
```

---

## 🚀 Uso

### 1. Acessar a investigação:
```
/investigations/{id}
```

### 2. Navegar pelas abas:
- **Resumo**: Dados gerais
- **Consultas Legais**: Histórico de consultas
- **Rede**: Visualização de relacionamentos ← NOVO
- **Análise ML**: Score de risco e padrões ← NOVO

### 3. A análise é executada automaticamente ao acessar as abas

---

## 📊 Exemplos de Casos de Uso

### Caso 1: Detecção de Grilagem
- Score de risco: **85/100** (Crítico)
- Padrões detectados:
  - 150 propriedades concentradas
  - Área total: 500.000 hectares
  - Empresas inativas: 60%
- Rede: 3 hubs principais controlando 80% das propriedades

### Caso 2: Esquema de Laranjas
- Score de risco: **72/100** (Alto)
- Padrões detectados:
  - 12 empresas no mesmo endereço
  - Capital social médio: R$ 1.000
  - Todas abertas em 30 dias
- Rede: Transações circulares detectadas

### Caso 3: Rede de Fachadas
- Score de risco: **68/100** (Alto)
- Padrões detectados:
  - 25 empresas com mesma atividade
  - Propriedades em 8 estados diferentes
- Rede: 1 pessoa física conectada a 25 empresas

---

## 🔒 Considerações de Performance

- Análises são executadas **apenas quando as abas são acessadas** (lazy loading)
- Queries são cacheadas com TanStack Query
- Análise abrangente executa em paralelo usando `asyncio.gather()`
- Tempo médio: 5-15 segundos para investigações grandes (1000+ entidades)

---

## 🛣️ Roadmap Futuro

- [ ] Exportar visualização de rede como imagem
- [ ] Filtros avançados no grafo (tipo de nó, tipo de relação)
- [ ] Machine Learning supervisionado (treinamento com casos conhecidos)
- [ ] Análise temporal (evolução da rede ao longo do tempo)
- [ ] Comparação entre investigações
- [ ] Alertas automáticos quando padrões críticos são detectados
- [ ] API pública para integração com sistemas externos

---

## 📝 Notas Técnicas

### Algoritmos de Detecção de Padrões:
1. **Outlier Detection**: Z-score (3 desvios padrão)
2. **Clustering**: K-means e DBSCAN para agrupamento
3. **Community Detection**: Greedy Modularity (NetworkX)
4. **Cycle Detection**: DFS para transações circulares

### Métricas de Centralidade:
- **Degree Centrality**: Quantidade de conexões diretas
- **Betweenness Centrality**: Quantos caminhos passam pelo nó
- **Score Combinado**: 60% degree + 40% betweenness

---

## ✅ Conclusão

As funcionalidades de Machine Learning e Análise de Rede foram implementadas com sucesso, permitindo:

✅ Cálculo automático de score de risco (0-100)  
✅ Detecção de 10+ tipos de padrões suspeitos  
✅ Visualização interativa de redes de relacionamentos  
✅ Análise de centralidade e comunidades  
✅ Recomendações automáticas baseadas em IA  
✅ Interface amigável e intuitiva  

O sistema está pronto para uso em investigações reais de agronegócio! 🎉
