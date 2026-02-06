# AgroADB Python Client

[![PyPI version](https://badge.fury.io/py/agroadb.svg)](https://badge.fury.io/py/agroadb)
[![Python Support](https://img.shields.io/pypi/pyversions/agroadb.svg)](https://pypi.org/project/agroadb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Cliente Python oficial para a API do **AgroADB** - Sistema de Análise de Dados Agrários.

## 🚀 Instalação

```bash
pip install agroadb
```

## 📋 Requisitos

- Python 3.8+
- requests >= 2.28.0

## 🔧 Uso Rápido

### Inicialização

```python
from agroadb import AgroADBClient

# Criar cliente
client = AgroADBClient(base_url="https://api.agroadb.com")

# Login
client.login("usuario@email.com", "senha")
```

### Ou usar variáveis de ambiente

```python
from agroadb import create_client
import os

os.environ["AGROADB_BASE_URL"] = "https://api.agroadb.com"
os.environ["AGROADB_API_KEY"] = "sua_api_key"

client = create_client()
```

## 📚 Exemplos de Uso

### Investigações

```python
# Listar investigações
investigations = client.investigations.list(limit=10, status="active")

# Obter investigação específica
inv = client.investigations.get(123)

# Criar investigação
new_inv = client.investigations.create({
    "title": "Nova Investigação",
    "description": "Descrição detalhada",
    "priority": "high",
    "status": "active"
})

# Atualizar investigação
updated = client.investigations.update(123, {
    "status": "completed"
})

# Buscar investigações
results = client.investigations.search("fraude")

# Deletar investigação
client.investigations.delete(123)
```

### Documentos

```python
# Listar documentos de uma investigação
docs = client.documents.list(investigation_id=123)

# Upload de documento
doc = client.documents.upload(
    investigation_id=123,
    file_path="/path/to/file.pdf",
    metadata={"category": "evidence"}
)

# Download de documento
client.documents.download(
    document_id=456,
    output_path="/path/to/output.pdf"
)

# Deletar documento
client.documents.delete(456)
```

### Usuários

```python
# Listar usuários
users = client.users.list(limit=50)

# Obter usuário
user = client.users.get(789)

# Criar usuário
new_user = client.users.create({
    "name": "João Silva",
    "email": "joao@example.com",
    "role": "analyst"
})

# Atualizar usuário
updated_user = client.users.update(789, {
    "role": "admin"
})

# Deletar usuário
client.users.delete(789)
```

### Analytics

```python
# Dashboard consolidado
dashboard = client.analytics.dashboard(
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Relatório de performance
performance = client.analytics.performance_report(
    start_date="2024-01-01"
)

# Analytics de usuários
user_analytics = client.analytics.user_analytics()

# Análise de funil
funnel = client.analytics.funnel_analysis("investigation_creation")
```

### Integrações

```python
# Busca no TJSP
tjsp_result = client.integrations.tjsp_search(cpf="12345678900")

# Consulta Serasa
serasa_result = client.integrations.serasa_query(cpf="12345678900")

# Receita Federal
receita_result = client.integrations.receita_federal(cnpj="12345678000199")

# Listar integrações
integrations = client.integrations.list()
```

### Exportação

```python
# Criar job de exportação
job = client.export.create_export(
    data_source="investigations",
    export_format="csv",
    start_date="2024-01-01"
)

# Verificar status
status = client.export.get_export_status(job["job_id"])

# Listar exportações
exports = client.export.list_exports(limit=10)

# Download
client.export.download_export(
    job_id=job["job_id"],
    output_path="/path/to/export.csv"
)

# Exportar para BigQuery
bq_result = client.export.export_to_bigquery(
    project_id="meu-projeto",
    dataset="agroadb",
    table_name="investigations",
    data_source="investigations"
)

# Exportar para Redshift
rs_result = client.export.export_to_redshift(
    cluster="agroadb-cluster",
    database="analytics",
    table_name="investigations",
    data_source="investigations"
)
```

## 🔑 Autenticação

### Login com usuário e senha

```python
client = AgroADBClient(base_url="https://api.agroadb.com")
response = client.login("usuario@email.com", "senha")

# Tokens são armazenados automaticamente
print(client.access_token)
```

### API Key

```python
client = AgroADBClient(
    base_url="https://api.agroadb.com",
    api_key="sua_api_key_aqui"
)
```

### Refresh Token

```python
# Renovar token automaticamente
new_tokens = client.auth.refresh(client.refresh_token)
client.access_token = new_tokens["access_token"]
```

### Logout

```python
client.logout()  # Limpa tokens armazenados
```

## ⚙️ Configuração Avançada

### Timeout e Retry

```python
client = AgroADBClient(
    base_url="https://api.agroadb.com",
    timeout=60,  # 60 segundos
    max_retries=5  # Máximo de tentativas
)
```

### Desabilitar verificação SSL (não recomendado para produção)

```python
client = AgroADBClient(
    base_url="https://api.agroadb.com",
    verify_ssl=False
)
```

### Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agroadb")
```

## 🧪 Tratamento de Erros

```python
from agroadb import (
    AgroADBException,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError
)

try:
    client.login("email@invalido.com", "senha_errada")
except AuthenticationError as e:
    print(f"Erro de autenticação: {e.message}")
    print(f"Status: {e.status_code}")

try:
    inv = client.investigations.get(99999)
except NotFoundError:
    print("Investigação não encontrada")

try:
    result = client.investigations.create({})  # Dados inválidos
except ValidationError as e:
    print(f"Erro de validação: {e.response}")

try:
    # Muitas requisições
    for i in range(1000):
        client.investigations.list()
except RateLimitError:
    print("Limite de requisições excedido")
```

## 📖 Type Hints

O cliente inclui type hints completos para melhor experiência de desenvolvimento:

```python
from agroadb import AgroADBClient
from typing import List, Dict, Any

client: AgroADBClient = AgroADBClient(base_url="https://api.agroadb.com")

investigations: List[Dict[str, Any]] = client.investigations.list()
investigation: Dict[str, Any] = client.investigations.get(123)
```

## 🧪 Testes

```bash
# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Executar testes
pytest

# Com cobertura
pytest --cov=agroadb

# Gerar relatório HTML
pytest --cov=agroadb --cov-report=html
```

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## 📞 Suporte

- **Documentação**: https://docs.agroadb.com
- **Issues**: https://github.com/agroadb/python-client/issues
- **Email**: dev@agroadb.com

## 🔗 Links Úteis

- [Documentação da API](https://docs.agroadb.com/api)
- [Exemplos](https://github.com/agroadb/python-client/tree/main/examples)
- [Changelog](https://github.com/agroadb/python-client/blob/main/CHANGELOG.md)

---

**Desenvolvido com ❤️ pela equipe AgroADB**
