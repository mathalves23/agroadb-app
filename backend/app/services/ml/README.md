# Machine Learning Services - AgroADB

Serviços de Machine Learning para análise inteligente de investigações no AgroADB.

## 📁 Estrutura

```
backend/app/services/ml/
├── risk_scoring.py       # Score de Risco (0-100)
├── pattern_detection.py  # Detecção de Padrões Suspeitos
└── network_analysis.py   # Análise de Rede (NetworkX)
```

## 🎯 Funcionalidades

### 1. Risk Scoring (`risk_scoring.py`)

**Classe**: `RiskScoringEngine`

Calcula score de risco baseado em 7 indicadores ponderados:

| Indicador | Peso | Descrição |
|-----------|------|-----------|
| Concentração de Propriedades | 15% | Quantidade e área total |
| Valor de Contratos | 20% | Valor total e outliers |
| Questões Judiciais | 25% | Processos ativos e críticos |
| Rede de Empresas | 15% | Quantidade e status |
| Padrões Temporais | 10% | Sequências rápidas |
| Dispersão Geográfica | 10% | Estados e cidades |
| Qualidade dos Dados | 5% | Completude |

**Uso:**
```python
from app.services.ml.risk_scoring import RiskScoringEngine

risk_score = await RiskScoringEngine.calculate_risk_score(db, investigation_id)

print(f"Score: {risk_score.total_score}/100")
print(f"Nível: {risk_score.risk_level}")
print(f"Confiança: {risk_score.confidence}")
```

### 2. Pattern Detection (`pattern_detection.py`)

**Classe**: `PatternDetectionEngine`

Detecta 10+ tipos de padrões suspeitos:

- 🚨 **Laranjas**: Empresas de fachada
  - Mesmo endereço (5+ empresas)
  - Capital social baixo (< R$ 10k)
  - Criação rápida (< 30 dias)

- 🔗 **Redes Suspeitas**
  - Alta taxa de inativas (> 40%)
  - Mesma atividade (possível cartel)

- 🔄 **Transações Circulares**
  - Ciclos de transações (A → B → A)

- 📍 **Concentração Anormal**
  - Geográfica (15+ na mesma cidade)
  - Por tamanho (outliers estatísticos)

- ⏰ **Anomalias Temporais**
  - Fins de semana
  - Mesmo dia (5+ empresas)

**Uso:**
```python
from app.services.ml.pattern_detection import PatternDetectionEngine

patterns = await PatternDetectionEngine.detect_patterns(db, investigation_id)

for pattern in patterns:
    print(f"{pattern.type}: {pattern.description}")
    print(f"Confiança: {pattern.confidence * 100}%")
    print(f"Severidade: {pattern.severity}")
```

### 3. Network Analysis (`network_analysis.py`)

**Classe**: `NetworkAnalysisEngine`

Analisa redes de relacionamentos usando NetworkX:

**Componentes:**
- **Nós**: Empresas (🏢), Propriedades (🏞️), Pessoas (👤)
- **Arestas**: owns, leases, partner_in

**Métricas:**
- Centralidade (degree + betweenness)
- Comunidades (Greedy Modularity)
- Densidade da rede
- Clusters desconectados
- Jogadores-chave (Top 10)

**Uso:**
```python
from app.services.ml.network_analysis import NetworkAnalysisEngine

analysis = await NetworkAnalysisEngine.analyze_network(db, investigation_id)

print(f"Nós: {analysis.num_nodes}")
print(f"Arestas: {analysis.num_edges}")
print(f"Densidade: {analysis.density}")
print(f"Jogadores-Chave: {analysis.key_players}")
```

## 🔧 Tecnologias

| Biblioteca | Versão | Uso |
|------------|--------|-----|
| scikit-learn | 1.4.0 | Clustering, outlier detection |
| NetworkX | 3.2.1 | Análise de grafos |
| NumPy | 1.26.3 | Operações numéricas |
| SciPy | 1.11.4 | Análises estatísticas |

## 📊 Estruturas de Dados

### RiskScore
```python
@dataclass
class RiskScore:
    total_score: float       # 0-100
    risk_level: str          # very_low, low, medium, high, critical
    confidence: float        # 0-1
    indicators: List[RiskIndicator]
    patterns_detected: List[str]
    recommendations: List[str]
    timestamp: datetime
```

### Pattern
```python
@dataclass
class Pattern:
    type: str
    confidence: float        # 0-1
    description: str
    severity: str            # low, medium, high, critical
    entities: List[int]
    evidence: Dict
```

### NetworkAnalysis
```python
@dataclass
class NetworkAnalysis:
    num_nodes: int
    num_edges: int
    density: float
    central_nodes: List[Tuple[str, float]]
    communities: List[List[str]]
    clusters: int
    key_players: List[str]
    suspicious_patterns: List[str]
    graph_data: Dict
```

## 🚀 Exemplos

### Exemplo 1: Análise Completa
```python
from app.services.ml import (
    RiskScoringEngine,
    PatternDetectionEngine,
    NetworkAnalysisEngine
)
import asyncio

async def analyze_investigation(db, investigation_id: int):
    # Executar em paralelo
    risk_task = RiskScoringEngine.calculate_risk_score(db, investigation_id)
    pattern_task = PatternDetectionEngine.detect_patterns(db, investigation_id)
    network_task = NetworkAnalysisEngine.analyze_network(db, investigation_id)
    
    risk, patterns, network = await asyncio.gather(
        risk_task, pattern_task, network_task
    )
    
    return {
        'risk': risk,
        'patterns': patterns,
        'network': network
    }
```

### Exemplo 2: Filtrar Padrões Críticos
```python
patterns = await PatternDetectionEngine.detect_patterns(db, investigation_id)

critical = [p for p in patterns if p.severity == 'critical']
high = [p for p in patterns if p.severity == 'high']

print(f"Críticos: {len(critical)}")
print(f"Alta Severidade: {len(high)}")
```

### Exemplo 3: Encontrar Caminho entre Entidades
```python
path = await NetworkAnalysisEngine.find_shortest_path(
    db, 
    investigation_id,
    source='company_123',
    target='property_456'
)

if path:
    print(f"Caminho encontrado: {' -> '.join(path)}")
else:
    print("Sem conexão direta")
```

## 🧪 Testes

### Teste Unitário
```python
import pytest
from app.services.ml.risk_scoring import RiskScoringEngine

@pytest.mark.asyncio
async def test_risk_score(db, investigation):
    score = await RiskScoringEngine.calculate_risk_score(db, investigation.id)
    
    assert 0 <= score.total_score <= 100
    assert score.risk_level in ['very_low', 'low', 'medium', 'high', 'critical']
    assert 0 <= score.confidence <= 1
```

### Teste de Integração
```bash
python test_ml_setup.py
```

## 📈 Performance

| Operação | Tempo Médio | Complexidade |
|----------|-------------|--------------|
| Risk Score | 3-5s | O(n) |
| Pattern Detection | 2-4s | O(n²) |
| Network Analysis | 4-8s | O(n + e) |
| Comprehensive | 5-15s | Paralelo |

*n = número de entidades, e = número de arestas*

## 🔒 Segurança

- ✅ Validação de entrada com Pydantic
- ✅ Queries seguras com SQLAlchemy ORM
- ✅ Logs de todas as operações
- ✅ Timeout configurável

## 📚 Documentação

- [Guia Completo](../../docs/dev/07-machine-learning.md)
- [API Endpoints](../../api/v1/endpoints/ml.py)

## 🛣️ Roadmap

- [ ] Cache Redis para análises pesadas
- [ ] Treinamento supervisionado
- [ ] Análise temporal (evolução)
- [ ] Comparação entre investigações
- [ ] Exportação de relatórios ML

## 🤝 Contribuir

1. Adicionar novos indicadores em `risk_scoring.py`
2. Criar novos padrões em `pattern_detection.py`
3. Implementar novas métricas em `network_analysis.py`
4. Adicionar testes unitários
5. Atualizar documentação

## 📄 Licença

Mantém licença do projeto principal AgroADB

---

**Versão**: 1.0.0  
**Status**: ✅ Stable  
**Última Atualização**: 06/02/2026
