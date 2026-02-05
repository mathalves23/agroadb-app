# API Reference - AgroADB

## 📚 Documentação da API REST

Base URL: `https://api.agroadb.com/api/v1`

---

## 🔐 Autenticação

### Registro de Usuário

```http
POST /auth/register
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "SenhaForte123!",
  "full_name": "João Silva"
}
```

**Resposta 201**:
```json
{
  "id": 1,
  "email": "usuario@example.com",
  "full_name": "João Silva",
  "is_active": true,
  "created_at": "2026-02-05T10:00:00Z"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "SenhaForte123!"
}
```

**Resposta 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Usando o Token

Todas as requisições autenticadas devem incluir o header:

```http
Authorization: Bearer {access_token}
```

---

## 🔍 Investigações

### Listar Investigações

```http
GET /investigations?skip=0&limit=20&status=active
Authorization: Bearer {token}
```

**Resposta 200**:
```json
{
  "total": 45,
  "items": [
    {
      "id": 1,
      "name": "Fazenda São João",
      "type": "property",
      "status": "active",
      "progress": 75,
      "created_at": "2026-02-01T10:00:00Z",
      "updated_at": "2026-02-05T14:30:00Z"
    }
  ]
}
```

### Criar Investigação

```http
POST /investigations
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Empresa XYZ Ltda",
  "type": "company",
  "description": "Due diligence para aquisição",
  "target_document": "12.345.678/0001-90",
  "priority": "high"
}
```

**Resposta 201**:
```json
{
  "id": 46,
  "name": "Empresa XYZ Ltda",
  "type": "company",
  "status": "draft",
  "progress": 0,
  "created_at": "2026-02-05T15:00:00Z"
}
```

### Obter Investigação

```http
GET /investigations/{id}
Authorization: Bearer {token}
```

### Atualizar Investigação

```http
PUT /investigations/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "completed",
  "priority": "medium"
}
```

### Deletar Investigação

```http
DELETE /investigations/{id}
Authorization: Bearer {token}
```

---

## 📊 Relatórios

### Gerar Relatório

```http
POST /investigations/{id}/report
Authorization: Bearer {token}
Content-Type: application/json

{
  "format": "pdf",
  "type": "executive"
}
```

**Resposta 200**:
```json
{
  "report_id": "abc123",
  "status": "processing",
  "download_url": null
}
```

### Verificar Status do Relatório

```http
GET /reports/{report_id}
Authorization: Bearer {token}
```

**Resposta 200**:
```json
{
  "report_id": "abc123",
  "status": "completed",
  "download_url": "https://api.agroadb.com/reports/abc123/download"
}
```

---

## ⚖️ Integrações Jurídicas

### Consultar Processo PJe

```http
POST /legal/pje/consultar-processo
Authorization: Bearer {token}
Content-Type: application/json

{
  "numero_processo": "0000000-00.0000.0.00.0000",
  "tribunal": "TRT2"
}
```

**Resposta 200**:
```json
{
  "numero_processo": "0000000-00.0000.0.00.0000",
  "tribunal": "TRT2",
  "classe": "Reclamação Trabalhista",
  "assunto": "Adicional de Periculosidade",
  "partes": [
    {
      "nome": "João Silva",
      "tipo": "autor"
    }
  ],
  "movimentacoes": [
    {
      "data": "2026-02-01",
      "tipo": "Distribuição",
      "descricao": "Processo distribuído"
    }
  ]
}
```

### Gerar Due Diligence

```http
POST /legal/due-diligence/gerar?investigation_id=1
Authorization: Bearer {token}
```

---

## 💬 Colaboração

### Listar Comentários

```http
GET /collaboration/comments?investigation_id=1
Authorization: Bearer {token}
```

### Adicionar Comentário

```http
POST /collaboration/comments
Authorization: Bearer {token}
Content-Type: application/json

{
  "investigation_id": 1,
  "content": "Revisão concluída. @joao favor verificar.",
  "mentions": [2]
}
```

---

## 🔔 Notificações

### Listar Notificações

```http
GET /notifications?unread_only=true
Authorization: Bearer {token}
```

### Marcar como Lida

```http
POST /notifications/{id}/read
Authorization: Bearer {token}
```

---

## 📈 Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Sucesso |
| 201 | Created - Recurso criado |
| 204 | No Content - Sucesso sem retorno |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Não autenticado |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Validação falhou |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Erro do servidor |

---

## 🚨 Tratamento de Erros

Formato padrão de erro:

```json
{
  "detail": "Mensagem de erro legível",
  "error_code": "ERROR_CODE",
  "status_code": 400
}
```

Exemplos:

```json
{
  "detail": "Email já está registrado",
  "error_code": "EMAIL_ALREADY_REGISTERED",
  "status_code": 400
}
```

---

## 📊 Paginação

Todas as listagens suportam paginação:

```http
GET /investigations?skip=20&limit=20
```

Resposta inclui total:

```json
{
  "total": 150,
  "skip": 20,
  "limit": 20,
  "items": [...]
}
```

---

## 🔍 Filtros e Ordenação

```http
GET /investigations?
  status=active&
  priority=high&
  type=property&
  order_by=created_at&
  order_direction=desc
```

---

## 📄 Documentação Interativa

Acesse a documentação completa e interativa:

- **Swagger UI**: https://api.agroadb.com/docs
- **ReDoc**: https://api.agroadb.com/redoc

---

## 💡 Exemplos de Código

### Python

```python
import requests

BASE_URL = "https://api.agroadb.com/api/v1"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "usuario@example.com",
    "password": "senha"
})
token = response.json()["access_token"]

# Listar investigações
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/investigations", headers=headers)
investigations = response.json()["items"]
```

### JavaScript

```javascript
const BASE_URL = 'https://api.agroadb.com/api/v1';

// Login
const loginResponse = await fetch(`${BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'usuario@example.com',
    password: 'senha'
  })
});
const { access_token } = await loginResponse.json();

// Listar investigações
const response = await fetch(`${BASE_URL}/investigations`, {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const { items } = await response.json();
```

---

## 🔒 Rate Limiting

- **Limite**: 60 requisições por minuto por IP
- **Headers de resposta**:
  - `X-RateLimit-Limit`: 60
  - `X-RateLimit-Remaining`: 45
  - `X-RateLimit-Reset`: timestamp

Quando exceder:
```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "status_code": 429
}
```

---

## 📞 Suporte

Dúvidas sobre a API?

- 📧 Email: api@agroadb.com
- 📚 Documentação: https://docs.agroadb.com
- 💬 GitHub Issues: Reporte bugs

---

**Versão da API**: v1.0.0  
**Última atualização**: 05/02/2026
