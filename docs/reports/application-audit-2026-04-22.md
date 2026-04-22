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
- Documentacao desta auditoria para acompanhamento futuro.

## Riscos e proximos passos recomendados

- Revisar os warnings de dependencia do backend, em especial plugin global de `logfire` e migracao Pydantic v2.
- Extrair alguns modulos grandes do frontend, como `InvestigationDetailPage.tsx`, para reduzir acoplamento e facilitar cobertura de testes.
- Avaliar separar bootstrap web, workers e tarefas de infraestrutura no backend para diminuir side effects no startup do app HTTP.
- Ampliar testes automatizados para notificacoes, PWA/offline e paginas grandes ainda com cobertura muito baixa.
