# 5. Banco de Dados - AgroADB

## 🗄️ Schema do Banco de Dados

O AgroADB utiliza **PostgreSQL 15** com **SQLAlchemy ORM**.

---

## 📊 Principais Tabelas

### users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
```

### investigations
```sql
CREATE TABLE investigations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    type VARCHAR(50) NOT NULL, -- property, company, person, due_diligence
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, pending, completed, cancelled
    priority VARCHAR(50) DEFAULT 'medium', -- low, medium, high, urgent
    progress FLOAT DEFAULT 0.0,
    description TEXT,
    target_document VARCHAR(50),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_investigations_user ON investigations(user_id);
CREATE INDEX idx_investigations_status ON investigations(status);
CREATE INDEX idx_investigations_type ON investigations(type);
CREATE INDEX idx_investigations_created ON investigations(created_at DESC);
```

### properties
```sql
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    matricula VARCHAR(50) UNIQUE,
    area DECIMAL(15,2),
    estado VARCHAR(2),
    municipio VARCHAR(100),
    endereco TEXT,
    valor_estimado DECIMAL(15,2),
    investigation_id INTEGER REFERENCES investigations(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_properties_matricula ON properties(matricula);
CREATE INDEX idx_properties_estado ON properties(estado);
```

### audit_logs
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(50),
    details JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
```

---

## 🔄 Migrações

### Criar Nova Migração

```bash
cd backend
alembic revision --autogenerate -m "Adicionar tabela xyz"
```

### Aplicar Migrações

```bash
alembic upgrade head
```

### Reverter Migração

```bash
alembic downgrade -1
```

---

## ⚡ Índices para Performance

```sql
-- Investigações por usuário e status (query mais frequente)
CREATE INDEX idx_inv_user_status ON investigations(user_id, status);

-- Busca full-text em investigações
CREATE INDEX idx_inv_search ON investigations USING gin(to_tsvector('portuguese', name || ' ' || COALESCE(description, '')));

-- Propriedades por estado e município
CREATE INDEX idx_prop_location ON properties(estado, municipio);
```

---

## 🔍 Queries Comuns

### Investigações Ativas do Usuário

```python
investigations = db.query(Investigation).filter(
    Investigation.user_id == user_id,
    Investigation.status == "active"
).order_by(Investigation.created_at.desc()).all()
```

### Busca com Full-Text

```python
from sqlalchemy import func

results = db.query(Investigation).filter(
    func.to_tsvector('portuguese', Investigation.name + ' ' + Investigation.description)
    .match(query)
).all()
```

---

## 💾 Backup

Backups automáticos diários via `scripts/backup.sh`:

```bash
pg_dump -h localhost -U agroadb agroadb | gzip > backup.sql.gz
```

---

**Atualizado**: 05/02/2026
