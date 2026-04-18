# Diagrama C4 — AgroADB

Visão em camadas conforme [C4 model](https://c4model.com/). Texto em Mermaid (renderiza em GitHub, GitLab, VS Code).

## Nível 1 — Contexto do sistema

```mermaid
flowchart LR
    analyst["Analista / Advogado"]
    admin["Administrador"]
    agroadb["AgroADB"]
    gov["APIs governamentais"]
    email["SMTP"]
    analyst -->|HTTPS| agroadb
    admin -->|HTTPS| agroadb
    agroadb -->|HTTPS / OAuth| gov
    agroadb -->|TLS| email
```

## Nível 2 — Contentores

```mermaid
flowchart TB
    user["Utilizador / browser"]
    web["Frontend\nReact + Vite"]
    api["API\nFastAPI"]
    db[("PostgreSQL")]
    redis[("Redis")]
    worker["Workers\nCelery"]
    user -->|HTTPS| web
    web -->|REST /api/v1| api
    api --> db
    api --> redis
    worker --> redis
    worker --> db
```

## Nível 3 — Componentes (API)

```mermaid
flowchart TB
    subgraph API["FastAPI"]
        Auth["auth / JWT / 2FA"]
        Inv["investigations"]
        ML["ML: risco, padrões, rede"]
        Legal["legal + integrações"]
        WS["WebSockets / notificações"]
    end
    Client["Cliente HTTP"]
    Client --> Auth
    Client --> Inv
    Client --> ML
    Client --> Legal
    Client --> WS
```

Para detalhe de classes Python, consulte o código em `backend/app/` e os ADRs em `docs/adr/`.
