# GitHub: remoto, branches e CI

Guia para configurar o repositório no GitHub e alinhar o **GitHub Actions** com segredos opcionais.

## 1. Remoto Git

Na raiz do clone:

```bash
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
# ou SSH:
# git remote add origin git@github.com:SEU_USUARIO/SEU_REPO.git

git fetch origin
git branch -u origin/develop develop   # ou a branch que usar
```

Se já existir `origin` com URL errada:

```bash
git remote set-url origin https://github.com/SEU_USUARIO/SEU_REPO.git
```

**Nota (Mercado Livre / `github.com-emu`):** se o teu `~/.gitconfig` global reescrever `https://github.com/` para outro host SSH, adiciona no **repositório** (apenas este projeto):

```bash
git config --local url."git@github.com:SEU_USUARIO/SEU_REPO.git".insteadOf "https://github.com/SEU_USUARIO/SEU_REPO.git"
```

Ou usa o script `scripts/setup-git-remote.sh`.

## 2. Política de branches (recomendado)

No GitHub: **Settings → Branches → Branch protection rules**.

| Branch   | Sugestão |
|----------|-----------|
| `main`   | Exigir PR antes de merge; exigir revisão (1); exigir que os **checks** do CI passem; impedir push directo. |
| `develop`| Igual ou ligeiramente mais permissiva (ex.: sem revisão obrigatória em equipas pequenas). |

**Rules → Add rule:** pattern `main`, activar *Require a pull request before merging*, *Require status checks to pass* (seleccionar jobs `Backend`, `Frontend`, e opcionalmente `E2E`).

## 3. Segredos do CI (Settings → Secrets and variables → Actions)

Segredos **opcionais**. Se não estiverem definidos, o workflow usa os valores por omissão embutidos (adequados ao Postgres/Redis dos `services` do job).

| Nome do secret | Utilidade |
|----------------|-----------|
| `CI_DATABASE_URL` | URL async do Postgres para pytest (substitui o default `postgresql+asyncpg://agroadb:test_password@localhost:5432/agroadb_test`). |
| `CI_REDIS_URL` | URL do Redis para testes (default `redis://localhost:6379/0`). |
| `CI_SECRET_KEY` | `SECRET_KEY` nos testes (mín. 32 caracteres). |
| `CI_ENCRYPTION_KEY` | `ENCRYPTION_KEY` em base64, se os testes precisarem de criptografia. |
| `CODECOV_TOKEN` | Upload de cobertura para [Codecov](https://codecov.io) (o passo já tem `continue-on-error: true`). |

**Forks / PRs de contribuidores:** os secrets não são passados a workflows de PRs vindos de forks, por defeito — o CI continua a funcionar com os defaults do ficheiro `ci.yml`.

### Comportamento embutido do CI (sem segredos)

- **Manual de produto:** o job de frontend corre `npm run check-product-manual`; o `npm run build` também o inclui. Falha se `product/manual-do-utilizador.md` não existir ou for demasiado curto (ver `product/README.md`).
- **Métricas Prometheus:** no job backend (e no workflow noturno completo), com o serviço Redis dos `services`, define-se `AGROADB_CI_QUEUE_METRICS=1` para o pytest exigir a presença de `agroadb_queue_tasks` na resposta de `GET /metrics`.
- **E2E Playwright:** inclui o fluxo até `/guide` (`frontend/e2e/user-guide.spec.ts`), além dos fluxos críticos com API mockada.

## 4. Variáveis (opcional)

Em **Variables** podes guardar valores não sensíveis (ex.: `PIP_INDEX_URL` já é passado no job como env).

## 5. Alinhar `main` e `develop`

Ver notas em `README.md` (testes) e, em caso de históricos divergentes, merge com `--allow-unrelated-histories` ou alinhar `main` a `develop` com cuidado (`git reset --hard` + `--force` só se não houver perda de histórico importante).

## 6. Onde está o workflow

Ficheiro: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) (na raiz do repositório).
