# Referência da API REST

A documentação **canónica** e sempre alinhada ao código é a exposta pela própria API:

| Recurso | URL típica (desenvolvimento) |
|---------|------------------------------|
| **Swagger UI** | `http://localhost:8000/api/docs` |
| **ReDoc** | `http://localhost:8000/api/redoc` |
| **OpenAPI JSON** | `http://localhost:8000/api/openapi.json` |

## Testes e contratos

- Contratos mínimos de rotas públicas: `backend/tests/contract/test_public_api_contract.py`.
- Coleção Postman (importação e ambientes): pasta [`../../postman/`](../../postman/) e [`postman/README.md`](../../postman/README.md).

## Nota

Este ficheiro substitui listagens manuais de endpoints que duplicavam o OpenAPI. Para exemplos de payloads, use o Swagger ou exporte o `openapi.json`.
