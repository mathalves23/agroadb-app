# 6. Testes - AgroADB

## 🧪 Visão Geral

O AgroADB possui uma suíte de testes completa com **156 testes** e **60%+ de cobertura** garantida.

---

## 📊 Estatísticas

- **Total**: 156 testes
- **Backend**: 66 testes (60%+ cobertura)
- **Frontend**: 90 testes (60%+ cobertura)
- **Tempo de Execução**: ~2 minutos
- **CI/CD**: Integrado

---

## 🐍 Backend Tests

### Configuração (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "-v",
    "--cov=app",
    "--cov-fail-under=60",
]
```

### Fixtures (conftest.py)

```python
@pytest.fixture
def db() -> Session:
    """Database de teste"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db: Session) -> User:
    """Usuário de teste"""
    user = User(email="test@example.com", ...)
    db.add(user)
    db.commit()
    return user
```

### Executar

```bash
cd backend

# Todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=app --cov-report=html

# Teste específico
pytest tests/test_auth.py::TestAuthEndpoints::test_login_success -v

# Watch mode
ptw tests/
```

### Categorias

**test_auth.py** (25 testes):
- Registro de usuário
- Login/Logout
- JWT tokens
- Refresh tokens
- Mudança de senha
- Segurança

**test_investigation_service.py** (18 testes):
- CRUD completo
- Validações
- Filtros
- Paginação
- Busca

**test_cache.py** (13 testes):
- Set/Get
- TTL
- Delete patterns
- Performance

**test_legal_integration.py** (10 testes):
- PJe integration
- Due diligence
- Mocks de API externa

---

## ⚛️ Frontend Tests

### Configuração (package.json)

```json
{
  "jest": {
    "preset": "ts-jest",
    "testEnvironment": "jsdom",
    "coverageThreshold": {
      "global": {
        "branches": 60,
        "functions": 60,
        "lines": 60,
        "statements": 60
      }
    }
  }
}
```

### Setup (setupTests.ts)

```typescript
import '@testing-library/jest-dom';

// Mocks globais
global.IntersectionObserver = class {...};
global.ResizeObserver = class {...};
window.matchMedia = jest.fn();
```

### Executar

```bash
cd frontend

# Todos os testes
npm test

# Com cobertura
npm run test:ci

# Watch mode
npm run test:watch

# Teste específico
npm test -- Controls.test.tsx
```

### Exemplo de Teste

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '../Controls';

describe('Button Component', () => {
  it('handles click events', async () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    
    await userEvent.click(screen.getByText('Click'));
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Categorias

**Controls.test.tsx** (35 testes):
- Button (7)
- Input (6)
- Badge (4)
- Avatar (4)
- Progress (5)

**Cards.test.tsx** (16 testes):
- Card (4)
- StatsCard (5)
- AlertCard (4)
- EmptyState (3)

**Overlays.test.tsx** (22 testes):
- Modal (6)
- Tabs (5)
- Accordion (5)
- Dropdown (6)

**DataTable.test.tsx** (17 testes):
- Rendering
- Sorting
- Filtering
- Pagination
- Selection

---

## 🎯 Boas Práticas

### AAA Pattern

```python
def test_example():
    # Arrange
    user = create_test_user()
    
    # Act
    result = login_user(user.email, "password")
    
    # Assert
    assert result.success is True
```

### Mock de APIs

```python
@patch('httpx.AsyncClient.get')
async def test_external_api(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response
    
    result = await fetch_external_data()
    
    assert result["data"] == "test"
```

### Test Isolation

```python
@pytest.fixture(scope="function")
def db():
    # Setup
    Base.metadata.create_all()
    yield session
    # Teardown
    Base.metadata.drop_all()
```

---

## 📊 Coverage Reports

### Backend

```bash
cd backend
pytest tests/ --cov=app --cov-report=html

# Abrir report
open htmlcov/index.html
```

### Frontend

```bash
cd frontend
npm run test:ci

# Abrir report
open coverage/index.html
```

---

## 🔄 CI/CD Integration

Os testes são executados automaticamente no GitHub Actions:

```yaml
jobs:
  backend-tests:
    steps:
      - name: Run tests
        run: pytest tests/ --cov=app --cov-fail-under=60
  
  frontend-tests:
    steps:
      - name: Run tests
        run: npm run test:ci
```

---

## ✅ Checklist de Testes

Antes de fazer commit:

- [ ] Todos os testes passam localmente
- [ ] Cobertura >= 60%
- [ ] Nenhum teste skipped sem justificativa
- [ ] Novos recursos têm testes
- [ ] Edge cases cobertos
- [ ] Mocks apropriados
- [ ] Assertions claras

---

## 📞 Suporte

Problemas com testes?

- 📧 Email: dev@agroadb.com
- 💬 Slack: #dev-tests

---

**Atualizado**: 05/02/2026
