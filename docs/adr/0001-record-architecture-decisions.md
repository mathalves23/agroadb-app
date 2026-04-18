# ADR-0001: Registar decisões de arquitectura (ADR)

## Estado

Aceite

## Contexto

O projecto AgroADB envolve API FastAPI, workers Celery, frontend React e múltiplas integrações. Sem registo explícito, decisões importantes perdem-se em PRs e chats.

## Decisão

Adoptar **Architecture Decision Records (ADR)** em `docs/adr/`, numerados sequencialmente (`0002-...`, `0003-...`), com:

- Título curto e **estado** (Proposta / Aceite / Depreciado)
- **Contexto**, **Decisão**, **Consequências** (positivas e negativas)

Novas decisões transversais (stack, segurança, ML, deploy) devem preferencialmente ter um ADR antes de alterações grandes.

## Consequências

- Curva de aprendizagem baixa para novos membros
- Manutenção leve (Markdown no repositório)
- Não substitui documentação operacional detalhada (ver `docs/deploy/`)
