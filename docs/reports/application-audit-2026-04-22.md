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
- Fase 1 iniciada e aplicada no backend: remocao do acoplamento com `passlib`, hashes novos em PBKDF2 com compatibilidade para hashes legados `bcrypt` e `sha256_crypt`.
- Remocao do warning de `pandas`/`pyarrow` no export CSV ao substituir o caminho simples por `csv.DictWriter`.
- Refinamento adicional do bootstrap web com conexao e shutdown explicitos da fila Redis, reduzindo side effects residuais no ciclo de vida HTTP.
- Criacao de `create_application()` no backend para concentrar middlewares, rotas e observabilidade em uma factory mais previsivel para testes e runtime.
- Alinhamento entre ambiente local e CI via targets `backend-lint`, `backend-test-ci` e `backend-check` no `Makefile`, reutilizados pelo workflow do GitHub Actions.
- Blindagem do warning do plugin global `logfire` tambem na raiz do repositorio, evitando diferencas entre execucao em `backend/` e na raiz.
- Evolucao do app shell frontend com disponibilidade real do backend, distinguindo offline, backend indisponivel, waking up e reconexao com retry explicito.
- Implementacao de fila offline para mutacoes leves no frontend, com reenvio automatico ao reconectar e integracao inicial em notificacoes e comentarios.
- Enriquecimento do banner de conectividade para mostrar acoes pendentes, estado de sincronizacao e recuperacao do backend.
- Inclusao de prompt de atualizacao PWA e reforco do service worker com estrategias de cache mais seguras para navegacao, assets e leituras criticas da API.
- Inclusao de aviso de expiracao de sessao com renovacao manual para reduzir perda de trabalho em fluxos longos autenticados.
- Adicao de fallback por snapshots locais para respostas GET elegiveis, melhorando resiliência da UI quando a API fica indisponivel depois de uma carga bem-sucedida.
- Ampliacao de testes com cobertura de banners novos, fila offline indireta via shell e cenarios E2E de persistencia de sessao e fallback offline.
- Inclusao de command palette global com atalho `Ctrl/Cmd + K`, navegacao rapida para dashboard, investigacoes, notificacoes, perfil, integracoes, manual e investigacoes recentes.
- Modularizacao adicional da Fase 2 no frontend: `SettingsPage` agora usa catalogo, hook e componentes de secao dedicados em `frontend/src/pages/settings/`.
- Extracao de blocos estruturais da aba legal da investigacao para componentes dedicados (`LegalConfigWarning`, `LegalSummaryOverview`, `LegalHistoryPanel`), reduzindo acoplamento dentro de `InvestigationDetailPage.tsx`.
- Inclusao de testes puros para utilitarios de configuracao de integracoes em `frontend/src/tests/pages/settings/utils.test.ts`.
- Padronizacao de side effects no frontend com `connectivityService`, `useNotifications`, `useChangeLog` e `useInvestigationSharing` como camadas unicas para health check, cache React Query, notificacoes e colaboracao.
- Refatoracao de `NotificationDropdown`, `NotificationsPage`, `ShareModal` e `ChangeLog` para consumir hooks/services dedicados, removendo `fetch` solto, leitura manual de token e recarga local duplicada.
- Revisao da camada de componentes compartilhados com novos agrupamentos `components/layout/` e `components/feedback/`, incluindo `AppShellFrame`, `AppShellFeedback`, `NoticeBanner` e `ErrorState`.
- Padronizacao visual e estrutural de conectividade, retry de integracoes, PWA e expiracao de sessao em cima do mesmo `NoticeBanner`, reduzindo duplicacao de markup e estilos.
- Reaproveitamento do novo `ErrorState` no `ErrorBoundary` e consolidacao do shell principal em torno de um `AppShell` mais claro para navbar, sidebar, feedback e conteudo principal.
- Fase 3 iniciada com ampliacao de testes para notificacoes, reconexao e resiliência offline: `NotificationsPage`, `ConnectionStatus`, `useBackendAvailability`, `connectivityService` e `offlineSnapshot` agora têm cobertura dedicada.
- Reforco da confianca nos fluxos de erro e reconexao com testes de health check, timeout, recuperacao de backend, estados indisponivel/offline e listas de notificacoes com filtros e acoes.
- Expansao dos testes das jornadas principais para formularios grandes e semântica acessível, incluindo `LoginPage`, `NewInvestigationPage` e `GlobalCommandPalette`.
- Ampliação dos testes E2E de resiliência PWA/offline com cobertura explícita para reload em modo offline, retorno da conexão, persistência de sessão, fallback para snapshots locais e prompt de atualização do service worker.
- Expansão dos testes de backend para `startup_application`, CORS por ambiente, criação da aplicação sem integrações externas e inicialização condicional de workers, fila e refresh de métricas.
- Melhoria prática da experiência offline no app shell com estado de fila mais rico, agrupamento das pendências por tipo, feedback de sincronização concluída/parcial/falha e ação manual de `Sincronizar agora` quando a reconexão não basta sozinha.
- Evolução da command palette global com agrupamento por áreas principais/investigações recentes, busca mais inteligente por relevância e atalhos reforçados para dashboard, investigações, notificações, guia, integrações e perfil.
- Ajuste do aviso de expiração de sessão para funcionar com soneca curta em vez de sumir até o logout, reduzindo risco de perda de trabalho em jornadas longas.
- Fase 5 iniciada com documentação explícita de padrões de arquitetura, convenções de páginas/hooks/services/schemas/testes/bootstrap e criação de um guia de governança contínua em `docs/dev/09-governanca-e-qualidade.md`.
- Checklist de PR fortalecido em `.github/pull_request_template.md` com validações de lint, testes, acessibilidade básica, impacto offline/PWA e impacto em telemetria/observabilidade.
- Medição contínua de qualidade ligada ao CI com cobertura crítica por arquivo no frontend e backend, além de alvos `make frontend-check` e verificação automática extra em `make backend-test-ci`.

## Riscos e proximos passos recomendados

- Revisar futuramente a remocao de compatibilidade com hashes legados `sha256_crypt` quando nao houver mais usuarios dependentes desse formato.
- Tratar warnings de dependencias transversais ainda externos ao codigo alterado nesta fase: `pytesseract` puxa `pandas` com aviso de `pyarrow` futuro e `PyPDF2` segue deprecado em favor de `pypdf`.
- Continuar a fatiar `InvestigationDetailPage.tsx`, principalmente o bloco extenso de mutacoes e formularios da aba legal.
- Seguir extraindo os formularios restantes da aba legal da investigacao para componentes menores por integracao (`SNCR`, `CND`, `CADIN`, `SNCCI`, `SIGEF GEO`, `Portal de Servicos`, `Servicos Estaduais`).
- Aumentar cobertura de componentes ainda grandes e criticos, como `LegalQueriesTab`, `NotificationsPage` e blocos de ML/rede da investigacao.
- Cobrir com testes os novos componentes de `settings/` e os blocos extraidos da aba legal, hoje ainda exercitados mais pela integracao da pagina do que por testes focados.
- Evoluir a fila offline de mutacoes para outras areas ainda nao adaptadas, como compartilhamento, perfil e alguns fluxos da aba legal.
- Expandir a mesma padronizacao de servicos e side effects para outros pontos com estado de browser ainda distribuido, como onboarding, preferencias locais e alguns listeners do app shell.
- Evoluir a camada `feedback/` com um ou dois wrappers adicionais para estados inline de erro/carregamento em cards e tabelas, hoje ainda misturados em componentes de dominio.
- Continuar a Fase 3 cobrindo componentes ainda grandes e com baixa cobertura, especialmente `ShareModal`, `ChangeLog`, `CommentThread`, `SettingsPage`, `ProfilePage` e os blocos restantes da aba legal de `InvestigationDetailPage`.
- Adicionar um teste E2E futuro para atualização completa do service worker com troca real de controller, se decidirmos endurecer ainda mais essa parte no ambiente de preview.
