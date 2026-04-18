# Segredos locais (Grafana / observabilidade)

- **`grafana_admin_password.dev`** — palavra-passe por omissão para desenvolvimento (versionada, **não** usar em produção).
- **`grafana_admin_password`** — ficheiro de uma linha com a palavra-passe real; **não** versionar (ver `.gitignore` na raiz).

## Produção

1. Gere uma palavra-passe forte e guarde-a num gestor de segredos.
2. No servidor, crie `monitoring/secrets/grafana_admin_password` (ou outro caminho) com permissões restritas.
3. Defina `GRAFANA_ADMIN_PASSWORD_FILE` no ambiente do Compose apontando para esse ficheiro.
4. Defina `GRAFANA_ADMIN_USER` (ex.: e-mail corporativo do administrador inicial).
5. Para **SSO**, use variáveis `GF_AUTH_*` (OAuth/OIDC) ou LDAP — ver `monitoring/grafana/SSO.example.env` e a [documentação oficial](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/).

O `docker-compose` monta o ficheiro em `/run/secrets/grafana_admin_password` e define `GF_SECURITY_ADMIN_PASSWORD__FILE`.
