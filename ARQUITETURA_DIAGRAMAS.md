# 🏗️ Arquitetura das Integrações - Diagramas

## 📊 Visão Geral do Sistema

```mermaid
graph TB
    subgraph Frontend
        UI[Interface React]
        Hooks[Custom Hooks]
    end
    
    subgraph "API REST"
        API[FastAPI Endpoints]
        Auth[Autenticação JWT]
    end
    
    subgraph "Serviços de Integração"
        ESAJ[e-SAJ Service]
        PROJ[Projudi Service]
        PJE[PJe Service]
        SER[Serasa Service]
        BOA[Boa Vista Service]
    end
    
    subgraph "Tribunais Estaduais"
        TJSP[TJSP]
        TJGO[TJGO]
        TJMS[TJMS]
        TJMT[TJMT]
        TJPR[TJPR]
        Others[... outros 21]
    end
    
    subgraph "Tribunais Federais"
        TRF1[TRF1]
        TRF2[TRF2]
        TRF3[TRF3]
        TRF4[TRF4]
        TRF5[TRF5]
    end
    
    subgraph "Birôs de Crédito"
        SERAPI[API Serasa]
        BOAAPI[API Boa Vista]
    end
    
    subgraph "Armazenamento"
        DB[(PostgreSQL)]
        AUDIT[Auditoria]
    end
    
    UI --> Hooks
    Hooks --> API
    API --> Auth
    Auth --> API
    
    API --> ESAJ
    API --> PROJ
    API --> PJE
    API --> SER
    API --> BOA
    
    ESAJ --> TJSP
    ESAJ --> TJGO
    ESAJ --> TJMS
    
    PROJ --> TJMT
    PROJ --> TJPR
    PROJ --> Others
    
    PJE --> TRF1
    PJE --> TRF2
    PJE --> TRF3
    PJE --> TRF4
    PJE --> TRF5
    
    SER --> SERAPI
    BOA --> BOAAPI
    
    API --> DB
    API --> AUDIT
    
    style ESAJ fill:#4CAF50
    style PROJ fill:#4CAF50
    style PJE fill:#4CAF50
    style SER fill:#2196F3
    style BOA fill:#2196F3
    style API fill:#FF9800
    style DB fill:#9C27B0
```

---

## 🔄 Fluxo de Consulta - Tribunais (Web Scraping)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant A as API
    participant S as Service (e-SAJ/Projudi)
    participant H as HTTP Client
    participant SE as Selenium
    participant T as Tribunal
    
    U->>A: POST /tribunais/esaj/1g
    A->>A: Validar autenticação
    A->>S: consultar_processos_1g()
    
    S->>H: Tentar HTTP direto
    H->>T: GET com params
    
    alt HTTP Sucesso
        T-->>H: HTML
        H-->>S: HTML
        S->>S: Parse com BeautifulSoup
    else HTTP Falha ou Captcha
        S->>SE: Iniciar Selenium
        SE->>T: Abrir Chrome headless
        SE->>T: Preencher formulário
        SE->>T: Clicar buscar
        T-->>SE: HTML
        SE-->>S: HTML
        S->>S: Parse com BeautifulSoup
        SE->>SE: Fechar browser
    end
    
    S->>S: Converter para dataclass
    S-->>A: Lista de processos
    A->>A: Salvar em legal_queries
    A->>A: Log de auditoria
    A-->>U: JSON response
```

---

## 🔐 Fluxo de Consulta - Birôs de Crédito (OAuth2)

```mermaid
sequenceDiagram
    participant U as Usuário
    participant A as API
    participant S as Serasa/Boa Vista Service
    participant O as OAuth2 Server
    participant B as Birô API
    participant D as Database
    
    U->>A: POST /credito/serasa/score
    A->>A: Validar JWT
    A->>S: consultar_score()
    
    alt Token não existe ou expirado
        S->>O: POST /oauth2/token
        O-->>S: access_token
        S->>S: Armazenar token
    end
    
    S->>B: POST /score (com Bearer token)
    B->>B: Validar credenciais
    B->>B: Consultar score
    B-->>S: Score + dados
    
    S->>S: Parse para dataclass
    S-->>A: Score object
    
    A->>D: Salvar em legal_queries
    A->>D: Log de auditoria
    
    A-->>U: {success: true, score: {...}}
    
    Note over U,D: Custo por consulta cobrado pelo birô
```

---

## 🏗️ Arquitetura de Serviços

```mermaid
graph LR
    subgraph "Web Scraping Services"
        ESAJ[e-SAJ Service]
        PROJ[Projudi Service]
        
        subgraph "Estratégias"
            HTTP[HTTP Direto]
            SEL[Selenium Fallback]
        end
        
        subgraph "Parse"
            BS[BeautifulSoup]
            REGEX[Regex]
        end
    end
    
    subgraph "API Services"
        SER[Serasa Service]
        BOA[Boa Vista Service]
        
        subgraph "Auth"
            OAUTH[OAuth2]
            TOKEN[Token Manager]
        end
        
        subgraph "Client"
            AIOHTTP[aiohttp]
        end
    end
    
    ESAJ --> HTTP
    ESAJ --> SEL
    SEL --> BS
    HTTP --> BS
    BS --> REGEX
    
    PROJ --> HTTP
    PROJ --> SEL
    
    SER --> OAUTH
    BOA --> OAUTH
    OAUTH --> TOKEN
    TOKEN --> AIOHTTP
    
    style ESAJ fill:#4CAF50
    style PROJ fill:#4CAF50
    style SER fill:#2196F3
    style BOA fill:#2196F3
```

---

## 📊 Modelo de Dados

```mermaid
erDiagram
    INVESTIGATION ||--o{ LEGAL_QUERY : has
    LEGAL_QUERY ||--o{ PROCESSO : contains
    LEGAL_QUERY ||--o{ CREDIT_REPORT : contains
    
    LEGAL_QUERY {
        int id PK
        int investigation_id FK
        string provider
        string query_type
        json query_params
        int result_count
        json response
        timestamp created_at
    }
    
    PROCESSO {
        string numero_processo
        string tribunal
        string grau
        string classe
        string assunto
        string status
        json partes
        json movimentacoes
    }
    
    CREDIT_REPORT {
        string cpf_cnpj
        string nome
        int score
        string faixa
        json restricoes
        json consultas
        float valor_total_restricoes
    }
    
    AUDIT_LOG {
        int id PK
        int user_id FK
        string action
        string resource_type
        timestamp created_at
        json details
    }
    
    LEGAL_QUERY ||--o{ AUDIT_LOG : generates
```

---

## 🔄 Fluxo de Investigação Completa

```mermaid
flowchart TD
    START([Iniciar Investigação])
    INPUT[Entrada: CPF/CNPJ]
    
    TRIB{Consultar<br/>Tribunais?}
    CRED{Consultar<br/>Crédito?}
    
    ESAJ[e-SAJ TJSP 1º+2º]
    PROJ[Projudi TJMT]
    PJE[PJe TRFs]
    
    SER[Serasa Score]
    BOA[Boa Vista Score]
    SERREL[Serasa Relatório]
    BOAREL[Boa Vista Relatório]
    
    CONSOL[Consolidar Dados]
    RISK[Calcular Risk Score]
    REPORT[Gerar Relatório]
    END([Fim])
    
    START --> INPUT
    INPUT --> TRIB
    
    TRIB -->|Sim| ESAJ
    TRIB -->|Sim| PROJ
    TRIB -->|Sim| PJE
    
    ESAJ --> CRED
    PROJ --> CRED
    PJE --> CRED
    TRIB -->|Não| CRED
    
    CRED -->|Sim| SER
    CRED -->|Sim| BOA
    SER --> SERREL
    BOA --> BOAREL
    
    SERREL --> CONSOL
    BOAREL --> CONSOL
    CRED -->|Não| CONSOL
    
    CONSOL --> RISK
    RISK --> REPORT
    REPORT --> END
    
    style ESAJ fill:#4CAF50
    style PROJ fill:#4CAF50
    style PJE fill:#4CAF50
    style SER fill:#2196F3
    style BOA fill:#2196F3
    style RISK fill:#FF9800
```

---

## 🚀 Deploy e Infraestrutura

```mermaid
graph TB
    subgraph "Desenvolvimento"
        DEV[Ambiente Dev]
        PYTEST[Testes Unitários]
        LINT[Linters]
    end
    
    subgraph "Staging"
        STAGE[Ambiente Staging]
        INTTEST[Testes Integração]
        PERF[Testes Performance]
    end
    
    subgraph "Produção"
        LB[Load Balancer]
        
        subgraph "Backend Cluster"
            B1[Backend 1]
            B2[Backend 2]
            B3[Backend 3]
        end
        
        subgraph "Workers"
            W1[Worker Selenium 1]
            W2[Worker Selenium 2]
        end
        
        DB[(PostgreSQL)]
        REDIS[(Redis Cache)]
        
        subgraph "Monitoring"
            PROM[Prometheus]
            GRAF[Grafana]
            LOG[Logs]
        end
    end
    
    DEV --> PYTEST
    PYTEST --> LINT
    LINT --> STAGE
    
    STAGE --> INTTEST
    INTTEST --> PERF
    PERF --> LB
    
    LB --> B1
    LB --> B2
    LB --> B3
    
    B1 --> DB
    B2 --> DB
    B3 --> DB
    
    B1 --> REDIS
    B2 --> REDIS
    B3 --> REDIS
    
    B1 -.-> W1
    B2 -.-> W2
    
    B1 --> PROM
    B2 --> PROM
    B3 --> PROM
    
    PROM --> GRAF
    B1 --> LOG
    B2 --> LOG
    B3 --> LOG
    
    style LB fill:#FF9800
    style DB fill:#9C27B0
    style REDIS fill:#F44336
```

---

## 💰 Fluxo de Custos

```mermaid
graph LR
    subgraph "Gratuito"
        T[Tribunais<br/>Web Scraping]
        T --> T1[TJSP]
        T --> T2[TJMT]
        T --> T3[Outros 24]
    end
    
    subgraph "Infraestrutura"
        I[Custos Fixos]
        I --> I1[Servidores]
        I --> I2[Chrome/Selenium]
        I --> I3[Bandwidth]
    end
    
    subgraph "Por Consulta"
        C[Birôs de Crédito]
        C --> C1[Serasa<br/>R$ 2-5]
        C --> C2[Boa Vista<br/>R$ 2-5]
    end
    
    TOTAL[Custo Total<br/>por Investigação]
    
    T --> TOTAL
    I --> TOTAL
    C --> TOTAL
    
    TOTAL --> EST[R$ 5-15<br/>estimado]
    
    style T fill:#4CAF50
    style C fill:#F44336
    style I fill:#FF9800
    style TOTAL fill:#9C27B0
```

---

## 📈 Métricas e KPIs

```mermaid
graph TD
    subgraph "Métricas Técnicas"
        T1[Taxa de Sucesso<br/>Target: >85%]
        T2[Tempo Médio<br/>Target: <30s]
        T3[Disponibilidade<br/>Target: >99%]
    end
    
    subgraph "Métricas de Negócio"
        B1[Uso em Investigações<br/>Target: 70%]
        B2[ROI<br/>Target: Positivo 6m]
        B3[Custo/Investigação<br/>Target: <R$50]
    end
    
    subgraph "Métricas de Qualidade"
        Q1[Precisão de Dados<br/>Target: >95%]
        Q2[NPS<br/>Target: >8]
        Q3[Tempo de Resposta<br/>Target: <2s API]
    end
    
    DASH[Dashboard<br/>Grafana]
    
    T1 --> DASH
    T2 --> DASH
    T3 --> DASH
    B1 --> DASH
    B2 --> DASH
    B3 --> DASH
    Q1 --> DASH
    Q2 --> DASH
    Q3 --> DASH
    
    DASH --> ALERT[Alertas]
    DASH --> REPORT[Relatórios]
    
    style DASH fill:#2196F3
    style ALERT fill:#F44336
```

---

## 🔐 Segurança e Compliance

```mermaid
flowchart TD
    START[Requisição API]
    
    AUTH{Autenticado?}
    PERM{Permissão?}
    
    LOG[Log de Auditoria]
    LGPD[Verificar LGPD]
    CONSENT{Consentimento?}
    
    EXEC[Executar Consulta]
    STORE[Armazenar Resultado]
    ENCRYPT[Criptografar Dados<br/>Sensíveis]
    
    RESP[Retornar Response]
    END[Fim]
    
    START --> AUTH
    AUTH -->|Não| DENY[403 Forbidden]
    AUTH -->|Sim| PERM
    
    PERM -->|Não| DENY
    PERM -->|Sim| LOG
    
    LOG --> LGPD
    LGPD --> CONSENT
    
    CONSENT -->|Não| WARN[Warning: Necessário<br/>Consentimento]
    CONSENT -->|Sim| EXEC
    
    EXEC --> STORE
    STORE --> ENCRYPT
    ENCRYPT --> RESP
    RESP --> END
    
    WARN --> END
    DENY --> END
    
    style AUTH fill:#F44336
    style LGPD fill:#FF9800
    style ENCRYPT fill:#9C27B0
```

---

**Diagramas criados com Mermaid** - Visualize no GitHub ou em qualquer visualizador Mermaid
