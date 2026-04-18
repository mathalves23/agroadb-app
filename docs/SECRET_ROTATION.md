# Rotação de segredos (AgroADB)

Este documento descreve **o que** deve ser rotacionado periodicamente e **como** fazê-lo sem downtime desnecessário.

## Inventário de segredos

| Segredo | Onde está | Frequência sugerida |
|--------|-----------|------------------------|
| `SECRET_KEY` | Backend (JWT) | A cada incidente ou 90 dias |
| `ENCRYPTION_KEY` | Backend (dados em repouso) | Só com migração planeadada (alto impacto) |
| `REFRESH_TOKEN` / passwords de integração | Variáveis de ambiente / secret manager | Conforme política do fornecedor |
| `STRIPE_*`, `PAGARME_*`, webhooks HMAC | Env / marketplace | Quando exposto ou anual |
| `SMTP_PASSWORD`, API keys externas | Env | Quando exposto ou rotação do fornecedor |
| `INTEGRATION_WEBHOOK_SECRET` | Env | A cada rotação de integração |

## Procedimento genérico

1. Gerar novo valor (comprimento e entropia adequados; usar gerador criptográfico).
2. Inserir o novo segredo no ambiente (staging primeiro), mantendo o antigo aceite durante a janela de transição se a aplicação suportar lista de chaves.
3. Reiniciar ou fazer *rolling deploy* dos serviços que leem a variável.
4. Forçar re-login de clientes se `SECRET_KEY` mudar (tokens JWT antigos deixam de ser válidos).
5. Revogar o segredo antigo no secret manager e auditar acessos.

## JWT (`SECRET_KEY`)

Ao alterar `SECRET_KEY`, todos os `access_token` e `refresh_token` emitidos com a chave antiga deixam de ser verificáveis. Comunique a janela de manutenção ou faça deploy em horário de baixo tráfego.

## Chave de encriptação (`ENCRYPTION_KEY`)

Alterar exige **re-encriptar** dados já persistidos com a chave antiga. Não rode em produção sem script de migração e backup testado.

## CI

O pipeline usa valores fictícios apenas para testes. Nunca commite ficheiros `.env` reais.
