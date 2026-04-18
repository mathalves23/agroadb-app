# Documentação de produto

Material orientado ao **utilizador final** da aplicação AgroADB (separado de `docs/`, que cobre desenvolvimento e operações técnicas).

## Fonte única do manual

- **Canónico:** [`manual-do-utilizador.md`](./manual-do-utilizador.md) — única fonte de verdade para o texto do manual.
- **Na aplicação:** a rota `/guide` importa este ficheiro em tempo de build (alias Vite `@product/…`). **Não** duplicar o conteúdo integral noutro ficheiro do repositório.
- **Build:** `npm run build` no frontend executa `check-product-manual` — o build **falha** se o ficheiro não existir ou for demasiado curto (garantia mínima de conteúdo).
- **Raiz do repo:** `make product-manual-check` invoca o mesmo script (útil antes de commits que só alteram `product/`).
- **CI:** o job de frontend executa `npm run check-product-manual` explicitamente e o `build` também a inclui (redundância intencional para falhar cedo e documentar o requisito).
- **Revisão:** usar [`EDITORIAL_CHECKLIST.md`](./EDITORIAL_CHECKLIST.md) antes de releases relevantes.

## Recursos visuais (opcional)

Screenshots ou um vídeo curto podem residir em `frontend/public/product-guide/` e serem referenciados no manual ou mostrados na página `/guide`. Ver o `README` nessa pasta.

## Qualidade

- **Conteúdo:** checklist editorial assinado antes de releases relevantes.
- **Técnica:** `npm run lint` e `npm run build` no `frontend/` (o build inclui a verificação do manual).
- **E2E (CI):** o job Playwright em `.github/workflows/ci.yml` corre todos os specs em `frontend/e2e/`, incluindo `user-guide.spec.ts` (login com API mockada → `/guide` → título e trecho canónico do manual).
- **Métricas (CI backend):** com Redis no job, `AGROADB_CI_QUEUE_METRICS=1` activa o teste que exige `agroadb_queue_tasks` em `GET /metrics` (`backend/tests/test_observability.py`); o workflow noturno completo usa o mesmo critério.
