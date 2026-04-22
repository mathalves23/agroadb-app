# Relatorio de auditoria do AgroADB

Data: 2026-04-22

## Achados principais

- Frontend com base funcional e testes verdes, mas com ruido relevante em build e testes.
- Dropdown e pagina de notificacoes consumiam a API com `fetch` manual e token incorreto, o que podia quebrar notificacoes em sessoes autenticadas.
- Faltavam recursos modernos reaproveitaveis de UX/app shell presentes em outros projetos do workspace, como instalacao PWA e feedback de conectividade.
- O backend tem superficie ampla e varios conectores experimentais; o smoke principal passou, mas ha warnings de dependencias e plugins globais no ambiente local.

## Melhorias aplicadas

- Centralizacao do consumo de notificacoes em `frontend/src/services/notificationService.ts`.
- Correcao do fluxo de autenticacao das notificacoes ao usar o cliente `api` compartilhado com refresh de token.
- Inclusao de `ConnectionStatus` para feedback online/offline dentro do layout principal.
- Inclusao de banner de instalacao PWA e registro de service worker para melhorar uso em desktop e mobile.
- Adicao de `sw.js` e aproveitamento dos assets PWA ja existentes em `public/`.
- Reducao de warnings do frontend com future flags do React Router e ajuste do `postcss` para formato de modulo compativel com Vite.
- Migracao dos principais schemas/responses do backend para `ConfigDict(from_attributes=True)`, reduzindo warnings de compatibilidade com Pydantic v2.
- Isolamento do bootstrap da aplicacao em `backend/app/bootstrap.py`, separando preparacao de persistencia, workers e metricas do entrypoint HTTP.
- Inclusao de flags de startup (`AUTO_CREATE_SCHEMA`, `AUTO_CREATE_INDEXES`, `CONNECT_QUEUE_ON_STARTUP`) para reduzir side effects acoplados ao `FastAPI`.
- Blindagem da execucao de testes locais contra o plugin global `logfire` e contra autoload de plugins externos via `Makefile` e `sitecustomize.py`.
- Extracao da navegacao e das regras de resumo da investigacao para `frontend/src/pages/investigationDetail/`.
- Ampliacao da cobertura automatizada com testes para notificacoes, PWA/offline, utilitarios da pagina de investigacao e bootstrap do backend.
- Documentacao desta auditoria para acompanhamento futuro.

## Riscos e proximos passos recomendados

- Remover warnings residuais de runtime/dependencias no backend: `passlib` usa `crypt` deprecated no Python 3.13 e `pandas` avisa sobre futura dependencia de `pyarrow`.
- Continuar a fatiar `InvestigationDetailPage.tsx`, principalmente o bloco extenso de mutacoes e formularios da aba legal.
- Aumentar cobertura de componentes ainda grandes e criticos, como `LegalQueriesTab`, `NotificationsPage` e blocos de ML/rede da investigacao.
