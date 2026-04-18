# Pacote `integrations` (API v1)

Sub-routers montados pelo `__init__.py` sob o prefixo `/integrations`:

| Módulo | Âmbito |
|--------|--------|
| `remainder.py` | Status, CAR, SIGEF parcelas, APIs abertas, transparência, TJMG, IBAMA, etc. |
| `conecta.py` | Conecta (SNCR, SIGEF, SICAR, SNCCI, CNPJ, CND, CADIN, …) |
| `tribunais.py` | Consulta processual, e-SAJ, Projudi |
| `biros_orgaos_notify.py` | Órgãos federais, birôs (Serasa/Boa Vista agregados), Slack/Teams |

Regenerar a partir do monólito (raramente necessário): `python3 backend/scripts/split_integrations_router.py` na raiz do repo (requer `integrations.py` presente).
