# 3. Arquitetura Backend - AgroADB

## 🏗️ Visão Geral

O backend do AgroADB é construído com **FastAPI**, seguindo princípios de **Clean Architecture** e **Domain-Driven Design (DDD)**.

---

## 📁 Estrutura de Pastas

```
backend/
├── app/
│   ├── api/                    # Camada de API
│   │   └── v1/
│   │       ├── endpoints/      # Rotas por domínio
│   │       │   ├── auth.py
│   │       │   ├── investigations.py
│   │       │   ├── users.py
│   │       │   ├── queue.py
│   │       │   ├── security.py
│   │       │   ├── notifications.py
│   │       │   ├── collaboration.py
│   │       │   └── legal_integration.py
│   │       └── router.py       # Agregador de rotas
│   │
│   ├── core/                   # Núcleo da aplicação
│   │   ├── config.py          # Configurações (Pydantic Settings)
│   │   ├── security.py        # JWT, hashing, auth
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── cache.py           # Redis cache service
│   │   └── middleware.py      # Middlewares customizados
│   │
│   ├── models/                 # Modelos SQLAlchemy (ORM)
│   │   ├── user.py
│   │   ├── investigation.py
│   │   ├── property.py
│   │   ├── company.py
│   │   └── ...
│   │
│   ├── services/               # Lógica de Negócio
│   │   ├── investigation.py   # CRUD + Business Logic
│   │   ├── notifications.py   # Sistema de notificações
│   │   ├── reports.py         # Geração de relatórios
│   │   ├── queue.py           # Sistema de filas
│   │   ├── lgpd.py            # Compliance LGPD
│   │   ├── collaboration.py   # Comentários, activity
│   │   └── legal_integration.py # PJe, Due Diligence
│   │
│   ├── scrapers/              # Web Scrapers
│   │   ├── base.py           # Base scraper abstrato
│   │   ├── incra.py          # Scraper INCRA
│   │   ├── car.py            # Scraper CAR
│   │   └── receita.py        # Scraper Receita Federal
│   │
│   └── main.py                # Aplicação FastAPI
│
├── tests/                      # Testes (66 testes)
├── alembic/                    # Migrações de banco
├── requirements.txt            # Dependências
└── Dockerfile                  # Container Docker
```

---

## 🔄 Fluxo de uma Requisição

```
Cliente HTTP
    │
    ├─> Middleware (CORS, Rate Limit, HTTPS)
    │
    ├─> Roteador FastAPI (/api/v1/*)
    │
    ├─> Endpoint (Validação Pydantic)
    │
    ├─> Dependency Injection (get_db, get_current_user)
    │
    ├─> Service Layer (Business Logic)
    │
    ├─> Model Layer (SQLAlchemy ORM)
    │
    └─> Database (PostgreSQL)
```

---

## 🗄️ Modelos de Dados

### User

```python
class User(Base):
    __tablename__ = "users"
    
    id: int (PK)
    email: str (unique)
    full_name: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    # Relacionamentos
    investigations: List[Investigation]
    comments: List[Comment]
```

### Investigation

```python
class Investigation(Base):
    __tablename__ = "investigations"
    
    id: int (PK)
    name: str
    type: enum (property, company, person, due_diligence)
    status: enum (draft, active, pending, completed, cancelled)
    priority: enum (low, medium, high, urgent)
    progress: float
    description: text
    target_document: str
    user_id: int (FK -> users.id)
    created_at: datetime
    updated_at: datetime
    
    # Relacionamentos
    user: User
    properties: List[Property]
    companies: List[Company]
    comments: List[Comment]
```

---

## 🔐 Autenticação e Segurança

### JWT Authentication

```python
# Login
token = create_access_token(user_id)
refresh_token = create_refresh_token(user_id)

# Verificação
user = get_current_user(token)  # Dependency

# Refresh
new_token = refresh_access_token(refresh_token)
```

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash
hashed = pwd_context.hash("senha_plaintext")

# Verify
is_valid = pwd_context.verify("senha_plaintext", hashed)
```

### Permissions

```python
@router.get("/admin-only")
def admin_route(current_user: User = Depends(get_current_superuser)):
    # Apenas superusers
    pass
```

---

## 📊 Cache Redis

### Uso Básico

```python
from app.core.cache import cache_service

# Set
await cache_service.set("key", {"data": "value"}, ttl=3600)

# Get
data = await cache_service.get("key")

# Delete
await cache_service.delete("key")

# Delete pattern
await cache_service.delete_pattern("user:*")
```

### Decorator

```python
@cache_service.cached(ttl=300)
async def expensive_query(param: str):
    # Esta função será cacheada por 5 minutos
    return await db.query(...)
```

---

## 🔄 Sistema de Filas

### Enfileirar Job

```python
from app.services.queue import queue_service

await queue_service.enqueue(
    "scrape_incra",
    investigation_id=1,
    matricula="12345"
)
```

### Worker

```python
# Executar worker
python -m app.services.queue worker
```

---

## 🌐 Scrapers

### Base Scraper

```python
class BaseScraper:
    async def scrape(self, **params):
        # 1. Validate params
        # 2. Make requests
        # 3. Parse data
        # 4. Save to DB
        # 5. Return results
        pass
```

### Exemplo: INCRA

```python
from app.scrapers.incra import INCRAScraper

scraper = INCRAScraper()
data = await scraper.scrape(matricula="12345", estado="SP")
```

---

## 📊 Database Queries

### Query Simples

```python
investigation = db.query(Investigation).filter(
    Investigation.id == investigation_id
).first()
```

### Query com Joins

```python
investigations = db.query(Investigation).join(User).filter(
    User.id == user_id,
    Investigation.status == "active"
).all()
```

### Query Otimizada

```python
from sqlalchemy.orm import joinedload

investigations = db.query(Investigation).options(
    joinedload(Investigation.user),
    joinedload(Investigation.properties)
).filter(...).all()
```

---

## 📝 Validação com Pydantic

```python
from pydantic import BaseModel, EmailStr, Field

class InvestigationCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    type: str = Field(..., regex="^(property|company|person)$")
    target_document: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Fazenda São João",
                "type": "property",
                "target_document": "12.345.678/0001-90"
            }
        }
```

---

## 🔌 Dependency Injection

```python
from app.api.deps import get_db, get_current_user

@router.get("/investigations")
def list_investigations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    return investigation_service.list(db, current_user.id, skip, limit)
```

---

## 📈 Métricas e Logging

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    REQUEST_COUNT.inc()
    with REQUEST_DURATION.time():
        response = await call_next(request)
    return response
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Investigation {id} created")
logger.error(f"Scraper failed: {error}")
```

---

## 🧪 Testes

Ver [docs/dev/06-testes.md](./06-testes.md)

---

**Próximo**: [Arquitetura Frontend](./04-arquitetura-frontend.md)
