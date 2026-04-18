# Postman — AgroADB

Coleção e ambientes para testar a API **sem duplicar** a documentação OpenAPI (`/api/docs`).

## Ficheiros

| Ficheiro | Descrição |
|----------|-----------|
| `AgroADB_API_Collection.json` | Coleção principal |
| `Development.postman_environment.json` | Variáveis de desenvolvimento |
| `Staging.postman_environment.json` | Staging |
| `Production.postman_environment.json` | Produção |

## Importar

1. Postman → **Import** → seleccionar os JSON acima.
2. Escolher o ambiente correspondente.
3. Definir `base_url` / tokens conforme o ambiente (não versionar segredos).

Para a lista actual de rotas e schemas, prefira **`/api/openapi.json`** na instância em execução.
