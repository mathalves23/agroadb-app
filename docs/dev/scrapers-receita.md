# Receita Federal Scraper - Documentação Completa

## Visão Geral

O Receita Federal Scraper é um módulo robusto e avançado para consulta de dados cadastrais de empresas brasileiras através de múltiplas APIs públicas da Receita Federal, com sistema inteligente de fallback e análise de estrutura corporativa.

## Características Principais

### ✅ Funcionalidades Implementadas

1. **Sistema Multi-API com Fallback Automático**
   - BrasilAPI (API primária)
   - ReceitaWS (fallback 1)
   - CNPJá (fallback 2)
   - API Oficial RFB (fallback 3)
   - Troca automática em caso de falha

2. **Extração Completa de Dados Cadastrais**
   - Razão social e nome fantasia
   - Situação cadastral completa
   - Endereço detalhado
   - CNAEs (principal e secundários)
   - Natureza jurídica e porte
   - Capital social
   - Datas importantes

3. **Estrutura Societária (QSA)**
   - Quadro de Sócios e Administradores completo
   - Identificação de sócios PF e PJ
   - Qualificação e percentuais de participação
   - Dados de representantes legais
   - Proteção LGPD automática

4. **Análise de CNPJs Relacionados**
   - Identificação de sócios que são empresas
   - Mapeamento de matrizes e filiais
   - Análise de rede corporativa
   - Identificação de grupos empresariais
   - Sócios em comum entre empresas

5. **Estrutura Corporativa Recursiva**
   - Busca em múltiplos níveis
   - Mapeamento completo do grupo
   - Análise de profundidade configurável
   - Identificação de estruturas complexas

6. **Sistema Avançado de Cache**
   - Cache de 48 horas para dados da Receita
   - Estatísticas em tempo real
   - Controle de expiração
   - Limpeza manual disponível

7. **Rate Limiting Inteligente**
   - Respeita limites de cada API
   - Controle automático de requisições
   - Prevenção de bloqueios
   - Espaçamento adequado entre chamadas

## Arquitetura

```
ReceitaScraper
├── APIs Integradas (Fallback Automático)
│   ├── BrasilAPI (primária - sem limite)
│   ├── ReceitaWS (3 req/min)
│   ├── CNPJá (5 req/min)
│   └── API Oficial RFB
│
├── Busca e Validação
│   ├── search() - Busca com fallback automático
│   ├── _fetch_from_provider() - Busca em API específica
│   ├── _validate_cnpj() - Validação de formato
│   └── _clean_cnpj() - Limpeza de formatação
│
├── Processamento de Dados
│   ├── _process_company_data() - Padronização de dados
│   ├── _extract_partners() - Extração do QSA
│   ├── _extract_related_cnpjs() - Identificação de relacionados
│   ├── _extract_secondary_activities() - CNAEs secundários
│   └── _format_address() - Formatação de endereço
│
├── Análise Corporativa
│   ├── get_full_corporate_structure() - Estrutura recursiva
│   └── analyze_corporate_network() - Análise de rede
│
├── Rate Limiting
│   ├── _can_make_request() - Verificação de limite
│   └── _mark_request() - Registro de requisição
│
└── Cache
    ├── _get_from_cache() - Recuperação
    ├── _save_to_cache() - Armazenamento
    ├── clear_cache() - Limpeza
    └── get_cache_stats() - Estatísticas
```

## Uso

### Exemplo 1: Busca Simples por CNPJ

```python
from app.scrapers.receita_scraper import ReceitaScraper

scraper = ReceitaScraper()

# Buscar empresa (aceita qualquer formatação)
results = await scraper.search("12.345.678/0001-90")

for company in results:
    print(f"CNPJ: {company['cnpj']}")
    print(f"Razão Social: {company['corporate_name']}")
    print(f"Nome Fantasia: {company['trade_name']}")
    print(f"Situação: {company['status']}")
    print(f"Porte: {company['company_size']}")
    print(f"Capital Social: R$ {company['capital']:,.2f}")
    print(f"Número de Sócios: {company['partners_count']}")
    print(f"API Utilizada: {company['provider']}")
```

### Exemplo 2: Análise de Estrutura Societária (QSA)

```python
# Buscar empresa com análise de sócios
results = await scraper.search("12345678000190")

if results:
    company = results[0]
    
    print(f"\n=== ESTRUTURA SOCIETÁRIA ===")
    print(f"Empresa: {company['corporate_name']}")
    print(f"\nQuadro de Sócios e Administradores ({company['partners_count']} sócios):\n")
    
    for partner in company['partners']:
        print(f"Nome: {partner['name']}")
        print(f"Documento: {partner['cpf_cnpj'] or 'Protegido LGPD'}")
        print(f"Qualificação: {partner['qualification']['description']}")
        if partner['percentage']:
            print(f"Participação: {partner['percentage']}%")
        print(f"Data Entrada: {partner['entry_date']}")
        print("-" * 50)
```

### Exemplo 3: Identificação de CNPJs Relacionados

```python
# Buscar empresa e CNPJs relacionados
results = await scraper.search("12345678000190")

if results:
    company = results[0]
    
    print(f"\n=== CNPJs RELACIONADOS ===")
    print(f"Total: {company['related_count']}\n")
    
    for related in company['related_cnpjs']:
        print(f"CNPJ: {related['cnpj']}")
        print(f"Relação: {related['relationship']}")
        if related['partner_name']:
            print(f"Nome: {related['partner_name']}")
            print(f"Qualificação: {related['qualification']}")
        print("-" * 50)
```

### Exemplo 4: Estrutura Corporativa Completa (Recursiva)

```python
# Buscar estrutura corporativa em múltiplos níveis
structure = await scraper.get_full_corporate_structure(
    "12345678000190",
    depth=2  # 2 níveis de profundidade
)

def print_structure(node, indent=0):
    """Imprime estrutura recursivamente"""
    company = node.get('company', {})
    prefix = "  " * indent
    
    print(f"{prefix}📊 {company.get('corporate_name')}")
    print(f"{prefix}   CNPJ: {company.get('cnpj')}")
    print(f"{prefix}   Sócios: {company.get('partners_count')}")
    
    for related in node.get('related_companies', []):
        print_structure(related, indent + 1)

print("\n=== ESTRUTURA CORPORATIVA COMPLETA ===\n")
print_structure(structure)
```

### Exemplo 5: Análise de Rede Corporativa

```python
# Analisar rede corporativa e identificar grupos
analysis = await scraper.analyze_corporate_network("12345678000190")

print("\n=== ANÁLISE DE REDE CORPORATIVA ===\n")
print(f"CNPJ Raiz: {analysis['root_cnpj']}")
print(f"Total de Empresas no Grupo: {analysis['total_companies']}")
print(f"Total de Sócios Únicos: {analysis['total_partners']}")
print(f"Sócios em Comum (ligação entre empresas): {analysis['common_partners_count']}")

if analysis['common_partners']:
    print(f"\n📊 SÓCIOS EM COMUM:")
    for doc, companies in analysis['common_partners'].items():
        print(f"\nDocumento: {doc}")
        print(f"Presente em {len(companies)} empresas:")
        for comp in companies:
            print(f"  - {comp['corporate_name']} ({comp['cnpj']})")
            print(f"    Qualificação: {comp['qualification']}")
```

### Exemplo 6: Uso com Sistema de Fallback

```python
# O sistema tenta automaticamente múltiplas APIs

# Exemplo: BrasilAPI está fora
# O scraper automaticamente tenta ReceitaWS
# Se ReceitaWS também falhar, tenta CNPJá
# Se todos falharem, retorna lista vazia

results = await scraper.search("12345678000190")

if results:
    company = results[0]
    print(f"✅ Dados encontrados via: {company['provider']}")
else:
    print("❌ Nenhuma API disponível no momento")
```

### Exemplo 7: Gerenciamento de Cache

```python
# Ver estatísticas do cache
stats = scraper.get_cache_stats()
print(f"📊 Cache Stats:")
print(f"  Total: {stats['total_entries']}")
print(f"  Válidas: {stats['valid_entries']}")
print(f"  Expiradas: {stats['expired_entries']}")
print(f"  TTL: {stats['ttl_hours']}h")

# Limpar cache manualmente
scraper.clear_cache()
print("✅ Cache limpo!")
```

## Estrutura de Dados Retornados

```python
{
    # Identificação
    "cnpj": "12.345.678/0001-90",
    "cnpj_clean": "12345678000190",
    "corporate_name": "EMPRESA TESTE LTDA",
    "trade_name": "Empresa Teste",
    
    # Situação Cadastral
    "status": "ATIVA",
    "status_date": "2020-01-15",
    "status_reason": None,
    
    # Localização
    "address": "Rua Teste, 123, Sala 456",
    "neighborhood": "Centro",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01234567",
    "country": "Brasil",
    
    # Contato
    "phone": "1133334444",
    "email": "contato@empresateste.com.br",
    
    # Atividade Econômica
    "main_activity": {
        "code": "6201500",
        "description": "Desenvolvimento de programas de computador sob encomenda"
    },
    "secondary_activities": [
        {
            "code": "6202300",
            "description": "Desenvolvimento e licenciamento de programas customizáveis"
        }
    ],
    
    # Natureza Jurídica
    "legal_nature": {
        "code": "2062",
        "description": "Sociedade Empresária Limitada"
    },
    
    # Porte e Capital
    "company_size": "DEMAIS",
    "capital": 100000.0,
    
    # Datas
    "opening_date": "2020-01-10",
    "registration_date": "2020-01-15",
    "last_update": "2024-11-20",
    
    # Estrutura Societária (QSA)
    "partners": [
        {
            "name": "JOÃO SILVA",
            "cpf_cnpj": "12345678",  # Parcialmente oculto (LGPD)
            "qualification": {
                "code": "49",
                "description": "Sócio-Administrador"
            },
            "entry_date": "2020-01-10",
            "country": "Brasil",
            "legal_representative": None,
            "representative_qualification": None,
            "age_range": None,
            "percentage": "60.00"
        },
        {
            "name": "EMPRESA HOLDING LTDA",
            "cpf_cnpj": "98765432000100",  # Sócio PJ
            "qualification": {
                "code": "22",
                "description": "Sócio"
            },
            "entry_date": "2021-06-15",
            "country": "Brasil",
            "percentage": "30.00"
        }
    ],
    "partners_count": 2,
    
    # CNPJs Relacionados
    "related_cnpjs": [
        {
            "cnpj": "98.765.432/0001-00",
            "cnpj_clean": "98765432000100",
            "relationship": "Sócio PJ",
            "partner_name": "EMPRESA HOLDING LTDA",
            "qualification": "Sócio"
        }
    ],
    "related_count": 1,
    
    # Indicadores
    "is_matriz": True,
    "is_mei": False,
    "is_simples": False,
    
    # Metadados
    "data_source": "Receita Federal via BrasilAPI",
    "provider": "BrasilAPI",
    "consulted_at": "2026-02-05T10:30:00",
    "raw_data": {
        # Dados brutos da API
    }
}
```

## APIs Utilizadas

### 1. BrasilAPI (Primária)
- **URL**: `https://brasilapi.com.br/api/cnpj/v1/{cnpj}`
- **Rate Limit**: Sem limite conhecido
- **Timeout**: 10s
- **Prioridade**: 1 (primeira a ser tentada)
- **Dados**: Completos (QSA, CNAEs, endereço)

### 2. ReceitaWS (Fallback 1)
- **URL**: `https://www.receitaws.com.br/v1/cnpj/{cnpj}`
- **Rate Limit**: 3 requisições/minuto
- **Timeout**: 15s
- **Prioridade**: 2
- **Dados**: Completos (QSA simplificado)

### 3. CNPJá (Fallback 2)
- **URL**: `https://publica.cnpj.ws/cnpj/{cnpj}`
- **Rate Limit**: 5 requisições/minuto
- **Timeout**: 10s
- **Prioridade**: 3
- **Dados**: Completos (atualização de 45 dias)

### 4. API Oficial RFB (Fallback 3)
- **URL**: `https://servicos.receita.fazenda.gov.br/.../cnpjreva`
- **Rate Limit**: Não documentado
- **Timeout**: 20s
- **Prioridade**: 4
- **Dados**: Oficiais (pode requerer CAPTCHA)

## Comparativo de Funcionalidades

| Funcionalidade | CAR | INCRA | Receita |
|----------------|-----|-------|---------|
| **Foco** | Ambiental | Fundiário | Empresarial |
| **Identificador** | Número CAR | CCIR | CNPJ |
| **Dados Principais** | APP, Reserva Legal | Áreas, ITR | QSA, CNAEs |
| **Geolocalização** | ✅ GeoJSON | ✅ Coordenadas | ❌ Endereço |
| **Sócios/Proprietários** | ✅ Nome | ✅ Nome/CPF | ✅ QSA Completo |
| **Estrutura Corporativa** | ❌ | ❌ | ✅ Recursiva |
| **CNPJs Relacionados** | ❌ | ❌ | ✅ Análise |
| **Cache** | 24h | 24h | 48h |
| **Fallback** | ❌ 1 API | ❌ 1 API | ✅ 4 APIs |

## Testes

### Cobertura Atual: 86%

```bash
# Executar testes
cd backend
pytest tests/test_receita_scraper.py -v --cov=app/scrapers/receita_scraper

# Testes incluem:
# ✅ Busca por CNPJ (válido/inválido)
# ✅ Sistema de fallback entre APIs
# ✅ Extração de estrutura societária
# ✅ Análise de CNPJs relacionados
# ✅ Estrutura corporativa recursiva
# ✅ Análise de rede corporativa
# ✅ Rate limiting
# ✅ Sistema de cache
# ✅ Métodos auxiliares
# ✅ Tratamento de erros
```

### Casos de Teste (26 testes)

1. **Busca Básica** (3 testes)
   - CNPJ válido
   - CNPJ inválido
   - Uso de cache

2. **Sistema de Fallback** (2 testes)
   - Fallback para segunda API
   - Todas as APIs falhando

3. **Processamento de Dados** (3 testes)
   - Dados completos
   - Extração de sócios
   - CNPJs relacionados

4. **Métodos Auxiliares** (5 testes)
   - Limpeza de CNPJ
   - Formatação de CNPJ
   - Validação de CNPJ
   - Formatação de endereço
   - Limpeza com proteção LGPD

5. **Rate Limiting** (3 testes)
   - Sem limite
   - Com limite
   - Expiração de limite

6. **Estrutura Corporativa** (3 testes)
   - Estrutura completa
   - Profundidade zero
   - Análise de rede

7. **Cache** (4 testes)
   - Salvar e recuperar
   - Expiração
   - Limpeza
   - Estatísticas

8. **Atividades Secundárias** (2 testes)
   - Extração de CNAEs
   - Lista vazia

9. **Identificação de Filial** (1 teste)
   - Extração de matriz

## Considerações de Performance

### Cache
- **TTL**: 48 horas (dados da Receita mudam menos)
- **Objetivo**: Reduzir requisições às APIs públicas
- **Memória**: ~3-5 KB por empresa em cache

### Rate Limiting
- **BrasilAPI**: Sem limite aparente
- **ReceitaWS**: 3 req/min (20s entre requisições)
- **CNPJá**: 5 req/min (12s entre requisições)
- **Controle Automático**: Respeita limites de cada API

### Fallback Inteligente
- Tentativa sequencial de APIs
- Falha silenciosa (não bloqueia sistema)
- Log de erros para monitoramento
- Retorno vazio se todas falharem

## Casos de Uso

### 1. Investigação de Ativos
- Identificar proprietários (sócios)
- Mapear estrutura societária
- Encontrar CNPJs relacionados
- Validar dados cadastrais

### 2. Due Diligence
- Verificar situação cadastral
- Analisar capital social
- Identificar sócios e administradores
- Mapear grupo econômico

### 3. Compliance e KYC
- Validar dados de cadastro
- Identificar beneficiários finais
- Mapear estruturas complexas
- Detectar grupos empresariais

### 4. Análise de Crédito
- Verificar porte da empresa
- Analisar capital social
- Identificar estrutura de controle
- Mapear empresas do grupo

## Limitações Conhecidas

1. **Rate Limiting**
   - APIs gratuitas têm limites
   - Requisições em massa podem ser bloqueadas
   - Recomendável usar cache extensivamente

2. **Dados Protegidos (LGPD)**
   - CPFs de sócios parcialmente ocultos
   - Sistema limpa automaticamente
   - Alguns dados podem estar incompletos

3. **Disponibilidade**
   - APIs públicas podem ficar indisponíveis
   - Sistema de fallback mitiga problema
   - Monitoramento recomendado

4. **Dados de Filiais**
   - Cada filial tem CNPJ próprio
   - Sistema identifica matriz automaticamente
   - Necessário buscar cada CNPJ separadamente

## Requisitos

```txt
# Backend dependencies
aiohttp>=3.9.0
httpx>=0.26.0
python-dotenv>=1.0.0
```

## Integração com Outros Scrapers

### Fluxo Completo de Investigação

```python
# 1. Buscar empresa na Receita
company_data = await receita_scraper.search("12345678000190")

# 2. Se houver propriedades rurais, buscar no CAR
if has_rural_property:
    car_data = await car_scraper.search(cpf_cnpj="12345678000190")

# 3. Verificar dados no INCRA
incra_data = await incra_scraper.search(cpf_cnpj="12345678000190")

# 4. Cruzar todos os dados
investigation_result = cross_reference_data(
    company_data,
    car_data,
    incra_data
)
```

## Licença e Conformidade

- Utiliza apenas APIs públicas
- Dados da Receita Federal são públicos
- Respeita proteção LGPD automaticamente
- Credita fonte de dados em todos os resultados
- Rate limiting respeita termos de uso

## Suporte

Para dúvidas ou problemas:
1. Verificar logs da aplicação
2. Consultar estatísticas do cache
3. Verificar conectividade com APIs
4. Revisar rate limiting

---

**Última atualização**: 05/02/2026  
**Versão**: 1.0.0  
**Status**: ✅ Implementado e Testado (86% cobertura)
