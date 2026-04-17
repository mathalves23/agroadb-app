# AgroADB Postman Collection

Collection completa da API AgroADB com testes automatizados e suporte a múltiplos ambientes.

## 📦 Arquivos

- **AgroADB_API_Collection.json**: Collection principal com todos os endpoints
- **Development.postman_environment.json**: Ambiente de desenvolvimento
- **Staging.postman_environment.json**: Ambiente de staging
- **Production.postman_environment.json**: Ambiente de produção

## 🚀 Importar no Postman

### Via Interface

1. Abra o Postman
2. Clique em "Import"
3. Arraste os arquivos JSON ou selecione-os
4. Collection e environments serão importados automaticamente

### Via URL (quando publicado)

```
https://www.postman.com/agroadb/workspace/agroadb-api
```

## 📋 Collection Completa

### 🔐 Authentication (4 endpoints)

- **POST** `/api/v1/auth/login` - Login
- **POST** `/api/v1/auth/register` - Registrar usuário
- **GET** `/api/v1/auth/me` - Dados do usuário atual
- **POST** `/api/v1/auth/refresh` - Renovar token

### 📁 Investigations (6 endpoints)

- **GET** `/api/v1/investigations` - Listar investigações
- **GET** `/api/v1/investigations/{id}` - Obter investigação
- **POST** `/api/v1/investigations` - Criar investigação
- **PUT** `/api/v1/investigations/{id}` - Atualizar investigação
- **DELETE** `/api/v1/investigations/{id}` - Deletar investigação
- **GET** `/api/v1/investigations/search` - Buscar investigações

### 📄 Documents (3 endpoints)

- **GET** `/api/v1/investigations/{id}/documents` - Listar documentos
- **POST** `/api/v1/investigations/{id}/documents` - Upload documento
- **DELETE** `/api/v1/documents/{id}` - Deletar documento

### 👥 Users (4 endpoints)

- **GET** `/api/v1/users` - Listar usuários
- **GET** `/api/v1/users/{id}` - Obter usuário
- **POST** `/api/v1/users` - Criar usuário
- **PUT** `/api/v1/users/{id}` - Atualizar usuário

### 📊 Analytics (4 endpoints)

- **GET** `/api/v1/analytics/dashboard` - Dashboard consolidado
- **GET** `/api/v1/analytics/reports/performance` - Relatório de performance
- **GET** `/api/v1/analytics/user/dashboard` - Analytics de usuários
- **GET** `/api/v1/analytics/user/funnel/{funnel_key}` - Análise de funil

### 🔌 Integrations (3 endpoints)

- **GET** `/api/v1/integrations` - Listar integrações
- **POST** `/api/v1/integrations/tjsp/search` - Busca TJSP
- **POST** `/api/v1/integrations/serasa/query` - Consulta Serasa

### 📤 Export (4 endpoints)

- **POST** `/api/v1/analytics/export/file/create` - Criar job de exportação
- **GET** `/api/v1/analytics/export/file/status/{job_id}` - Status da exportação
- **GET** `/api/v1/analytics/export/file/list` - Listar exportações
- **POST** `/api/v1/analytics/export/warehouse/bigquery` - Exportar para BigQuery

### 🏥 Health Check (1 endpoint)

- **GET** `/api/health` - Health check da API

**Total: 29 endpoints**

## 🔑 Variáveis de Ambiente

### Global

| Variável | Descrição |
|----------|-----------|
| `base_url` | URL base da API |
| `access_token` | Token de acesso JWT (preenchido automaticamente) |
| `refresh_token` | Token de refresh (preenchido automaticamente) |

### Autenticação

| Variável | Descrição |
|----------|-----------|
| `user_email` | Email do usuário |
| `user_password` | Senha do usuário |

### IDs de Recursos

| Variável | Descrição |
|----------|-----------|
| `investigation_id` | ID da investigação (preenchido automaticamente) |
| `document_id` | ID do documento |
| `user_id` | ID do usuário |
| `export_job_id` | ID do job de exportação |

## 🧪 Testes Automatizados

Cada endpoint inclui testes automatizados:

```javascript
// Teste de status
pm.test("Status 200", function () {
    pm.response.to.have.status(200);
});

// Teste de resposta
pm.test("Has items array", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('items');
});

// Teste de performance
pm.test("Response time < 2000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});
```

### Executar Todos os Testes

1. Abra o Postman
2. Selecione a collection "AgroADB API"
3. Clique em "Run"
4. Selecione environment (Dev, Staging, ou Prod)
5. Clique em "Run AgroADB API"

### Via CLI (Newman)

```bash
# Instalar Newman
npm install -g newman

# Executar collection
newman run AgroADB_API_Collection.json \
  -e Development.postman_environment.json \
  --reporters cli,html \
  --reporter-html-export report.html

# Com detalhes
newman run AgroADB_API_Collection.json \
  -e Development.postman_environment.json \
  --verbose
```

## 📊 Fluxo de Trabalho Recomendado

### 1. Autenticação

```
1. POST /api/v1/auth/login
   → Obtém access_token e refresh_token
   → Tokens são salvos automaticamente em variáveis
```

### 2. CRUD de Investigações

```
2. POST /api/v1/investigations
   → Cria nova investigação
   → investigation_id é salvo automaticamente

3. GET /api/v1/investigations/{investigation_id}
   → Obtém detalhes da investigação

4. PUT /api/v1/investigations/{investigation_id}
   → Atualiza investigação

5. DELETE /api/v1/investigations/{investigation_id}
   → Deleta investigação
```

### 3. Upload de Documentos

```
6. POST /api/v1/investigations/{investigation_id}/documents
   → Upload de arquivo
   → Usar body tipo "form-data"
```

### 4. Analytics

```
7. GET /api/v1/analytics/dashboard
   → Dashboard consolidado

8. GET /api/v1/analytics/user/funnel/investigation_creation
   → Análise de funil
```

### 5. Exportação

```
9. POST /api/v1/analytics/export/file/create
   → Cria job de exportação
   → export_job_id é salvo automaticamente

10. GET /api/v1/analytics/export/file/status/{export_job_id}
    → Verifica status da exportação
```

## 🌍 Ambientes

### Development

```json
{
  "base_url": "http://localhost:8000",
  "user_email": "admin@agroadb.dev",
  "user_password": "dev_password_123"
}
```

### Staging

```json
{
  "base_url": "https://staging.agroadb.com",
  "user_email": "test@agroadb.com"
}
```

### Production

```json
{
  "base_url": "https://api.agroadb.com"
}
```

## 📝 Scripts Úteis

### Pre-request Script (Global)

```javascript
// Log da requisição
console.log('Request:', {
    method: pm.request.method,
    url: pm.request.url.toString()
});
```

### Test Script (Global)

```javascript
// Testes globais de performance
pm.test("Response time reasonable", function () {
    pm.expect(pm.response.responseTime).to.be.below(5000);
});

// Log da resposta
console.log('Response:', {
    status: pm.response.code,
    time: pm.response.responseTime + 'ms'
});
```

## 🔐 Autenticação Automática

A collection está configurada para autenticação automática via Bearer Token:

```
Authorization: Bearer {{access_token}}
```

O token é automaticamente:
- Obtido no login
- Salvo em variável de ambiente
- Usado em todas as requisições subsequentes
- Renovado quando necessário

## 📄 Documentação Online

Quando publicado no Postman:

```
https://documenter.getpostman.com/view/agroadb-api
```

## 🤝 Compartilhamento

### Workspace Público

```
https://www.postman.com/agroadb/workspace/agroadb-api
```

### Fork da Collection

1. Acesse o workspace público
2. Clique em "Fork"
3. A collection será copiada para seu workspace

## 🐛 Troubleshooting

### Token Expirado

Se receber erro 401:
1. Execute novamente o endpoint de Login
2. O token será renovado automaticamente

### Variáveis Não Definidas

Se alguma variável estiver undefined:
1. Verifique o environment ativo
2. Execute os endpoints na ordem recomendada
3. Variáveis são preenchidas automaticamente pelos testes

### Timeout

Se timeout exceder:
1. Verifique conexão com a API
2. Aumente timeout nas configurações do Postman
3. Collection Settings → Timeout → 30000ms

## 📞 Suporte

- **Documentação API**: https://docs.agroadb.com
- **Issues**: https://github.com/agroadb/api/issues
- **Email**: dev@agroadb.com

---

**Desenvolvido com ❤️ pela equipe AgroADB**
