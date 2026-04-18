# Revisão OWASP ASVS (foco API REST — AgroADB)

Checklist derivada de [OWASP ASVS 4.x](https://owasp.org/www-project-application-security-verification-standard/) aplicável a uma API FastAPI + JWT + PostgreSQL. Use em auditorias internas ou pedidos de homologação.

## V1 — Arquitetura, design e modelação de ameaças

- [ ] Modelo de ameaças documentado (autenticação, filas Celery, uploads, webhooks).
- [ ] Limites de confiança entre serviços (API, worker, Redis, Postgres) claros.

## V2 — Autenticação

- [ ] Passwords armazenados com algoritmo moderno (ex.: bcrypt) e política de complexidade.
- [ ] Proteção a brute-force / rate limiting em `/auth/login` e rotas sensíveis.
- [ ] Tokens JWT com expiração curta; refresh com rotação ou revogação definida.
- [ ] MFA disponível ou planeado para contas privilegiadas (ASVS 2.7+).

## V3 — Gestão de sessão

- [ ] Cookies, se usados, com flags `Secure`, `HttpOnly`, `SameSite` adequados.
- [ ] Logout invalida refresh tokens no servidor (quando aplicável).

## V4 — Controlos de acesso

- [ ] Autorização por recurso (utilizador só acede às suas investigações / roles).
- [ ] IDs sequenciais não expõem dados sem verificação de ownership.

## V5 — Validação, sanitização e codificação

- [ ] Pydantic valida entrada; rejeição de tipos inesperados e limites de tamanho.
- [ ] Sem SQL concatenado; uso de ORM / parâmetros bind.

## V6 — Criptografia em repouso e em trânsito

- [ ] TLS em produção (`FORCE_HTTPS` / proxy terminando TLS).
- [ ] Dados sensíveis encriptados com chave gerida (`ENCRYPTION_KEY`).

## V7 — Tratamento de erros e logging

- [ ] Erros 500 não vazam stack traces ao cliente.
- [ ] Logs sem passwords, tokens completos ou PII desnecessária.

## V8 — Proteção de dados

- [ ] Retenção e eliminação de dados alinhadas à LGPD / política interna.
- [ ] Exportações (PDF/Excel) com controlo de acesso.

## V9 — Comunicações

- [ ] CORS restrito a origens conhecidas em produção.
- [ ] Cabeçalhos de segurança (CSP, `X-Frame-Options`, etc.) configurados.

## V10 — APIs maliciosas / abuso

- [ ] Rate limiting global e por rota onde fizer sentido.
- [ ] Webhooks com assinatura HMAC e *replay* mitigado (timestamp / nonce).

## V11 — Configuração

- [ ] Segredos apenas em variáveis de ambiente ou secret manager.
- [ ] `DEBUG` / documentação OpenAPI desactivados ou protegidos em produção.

## V12 — Dependências

- [ ] `pip-audit` e `npm audit` no CI com política de severidade acordada.
- [ ] Atualização periódica de dependências críticas (auth, TLS, framework).

## V13 — Integridade e *pipeline*

- [ ] CI com testes de segurança smoke; branches protegidas.
- [ ] Imagens Docker escaneadas antes do deploy.

---

**Nota:** Marcar um item implica evidência (teste automatizado, configuração ou ticket). Este ficheiro não substitui um pentest formal.
