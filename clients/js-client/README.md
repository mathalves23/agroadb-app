# @agroadb/client

[![npm version](https://badge.fury.io/js/%40agroadb%2Fclient.svg)](https://badge.fury.io/js/%40agroadb%2Fclient)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Cliente JavaScript/TypeScript oficial para a API do **AgroADB** - Sistema de Análise de Dados Agrários.

## 🚀 Instalação

```bash
npm install @agroadb/client
```

Ou com yarn:

```bash
yarn add @agroadb/client
```

## 📋 Requisitos

- Node.js >=14.0.0
- TypeScript >=4.5 (opcional, para projetos TypeScript)

## 🔧 Uso Rápido

### TypeScript

```typescript
import { AgroADBClient } from '@agroadb/client';

// Criar cliente
const client = new AgroADBClient({
  baseUrl: 'https://api.agroadb.com'
});

// Login
await client.login('usuario@email.com', 'senha');

// Listar investigações
const investigations = await client.investigations.list({ limit: 10 });
```

### JavaScript (ES6+)

```javascript
const { AgroADBClient } = require('@agroadb/client');

const client = new AgroADBClient({
  baseUrl: 'https://api.agroadb.com'
});

// Usar com async/await
async function main() {
  await client.login('usuario@email.com', 'senha');
  const investigations = await client.investigations.list();
  console.log(investigations);
}

main();
```

### Variáveis de Ambiente

```javascript
import { createClient } from '@agroadb/client';

// Usa AGROADB_BASE_URL e AGROADB_API_KEY do environment
const client = createClient();
```

## 📚 Exemplos de Uso

### Investigações

```typescript
// Listar com filtros
const investigations = await client.investigations.list({
  limit: 20,
  offset: 0,
  status: 'active',
  priority: 'high'
});

// Obter por ID
const investigation = await client.investigations.get(123);

// Criar
const newInvestigation = await client.investigations.create({
  title: 'Nova Investigação',
  description: 'Descrição detalhada',
  priority: 'high',
  status: 'active'
});

// Atualizar
const updated = await client.investigations.update(123, {
  status: 'completed'
});

// Buscar
const results = await client.investigations.search('fraude');

// Deletar
await client.investigations.delete(123);
```

### Documentos

```typescript
// Listar documentos de uma investigação
const docs = await client.documents.list(123);

// Obter documento
const doc = await client.documents.get(456);

// Deletar documento
await client.documents.delete(456);
```

### Usuários

```typescript
// Listar usuários
const users = await client.users.list({ limit: 50 });

// Criar usuário
const newUser = await client.users.create({
  name: 'João Silva',
  email: 'joao@example.com',
  password: 'senha123',
  role: 'analyst'
});

// Atualizar
const updated = await client.users.update(789, {
  role: 'admin'
});

// Deletar
await client.users.delete(789);
```

### Analytics

```typescript
// Dashboard
const dashboard = await client.analytics.dashboard({
  start_date: '2024-01-01',
  end_date: '2024-12-31'
});

// Relatório de performance
const performance = await client.analytics.performanceReport({
  start_date: '2024-01-01'
});

// Analytics de usuários
const userAnalytics = await client.analytics.userAnalytics();

// Análise de funil
const funnel = await client.analytics.funnelAnalysis('investigation_creation');
```

### Integrações

```typescript
// Lista integrações disponíveis
const integrations = await client.integrations.list();

// Busca no TJSP
const tjspResult = await client.integrations.tjspSearch('12345678900');

// Consulta Serasa
const serasaResult = await client.integrations.serasaQuery('12345678900');

// Receita Federal
const receitaResult = await client.integrations.receitaFederal('12345678000199');
```

### Exportação

```typescript
// Criar job de exportação
const job = await client.export.createExport({
  data_source: 'investigations',
  export_format: 'csv',
  start_date: '2024-01-01'
});

// Verificar status
const status = await client.export.getStatus(job.job_id);

// Listar exportações
const exports = await client.export.list(10);

// Exportar para BigQuery
const bqResult = await client.export.exportToBigQuery({
  project_id: 'meu-projeto',
  dataset: 'agroadb',
  table_name: 'investigations',
  data_source: 'investigations'
});

// Exportar para Redshift
const rsResult = await client.export.exportToRedshift({
  cluster: 'agroadb-cluster',
  database: 'analytics',
  table_name: 'investigations',
  data_source: 'investigations'
});
```

## 🔑 Autenticação

### Login com Email e Senha

```typescript
const response = await client.login('usuario@email.com', 'senha');
console.log(response.access_token);
```

### API Key

```typescript
const client = new AgroADBClient({
  baseUrl: 'https://api.agroadb.com',
  apiKey: 'sua_api_key'
});
```

### Token Manual

```typescript
client.setAccessToken('seu_token_aqui');
```

### Logout

```typescript
client.logout(); // Limpa tokens
```

## ⚙️ Configuração Avançada

### Timeout e Retries

```typescript
const client = new AgroADBClient({
  baseUrl: 'https://api.agroadb.com',
  timeout: 60000, // 60 segundos
  maxRetries: 5 // Máximo de tentativas
});
```

## 🧪 Tratamento de Erros

```typescript
import { AgroADBError } from '@agroadb/client';

try {
  await client.login('email@invalido.com', 'senha_errada');
} catch (error) {
  if (error instanceof AgroADBError) {
    console.log('Status:', error.statusCode);
    console.log('Response:', error.response);
  }
}

// Tratamento específico
try {
  const inv = await client.investigations.get(99999);
} catch (error) {
  if (error instanceof AgroADBError && error.statusCode === 404) {
    console.log('Investigação não encontrada');
  }
}
```

## 📖 TypeScript Support

O cliente é escrito em TypeScript e inclui definições de tipos completas:

```typescript
import {
  AgroADBClient,
  Investigation,
  User,
  Document,
  ExportJob
} from '@agroadb/client';

// Tipos são inferidos automaticamente
const investigations: Investigation[] = await client.investigations.list();
const user: User = await client.users.get(123);
```

## 🧪 Testes

```bash
# Executar testes
npm test

# Com watch
npm run test:watch

# Com cobertura
npm run test:coverage
```

## 🏗️ Build

```bash
# Build para produção
npm run build

# O output estará em ./dist
```

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## 📞 Suporte

- **Documentação**: https://docs.agroadb.com
- **Issues**: https://github.com/agroadb/js-client/issues
- **Email**: dev@agroadb.com

## 🔗 Links Úteis

- [Documentação da API](https://docs.agroadb.com/api)
- [Exemplos](https://github.com/agroadb/js-client/tree/main/examples)
- [Changelog](https://github.com/agroadb/js-client/blob/main/CHANGELOG.md)

---

**Desenvolvido com ❤️ pela equipe AgroADB**
