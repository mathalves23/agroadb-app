# Retenção de dados e backups (referência operacional)

Este documento descreve **práticas mínimas** para um cenário SaaS em produção. Os valores concretos (dias, localização, cifragem) devem ser definidos pelo **encarregado de proteção de dados (DPO)** e pela **equipa de infraestrutura**, em linha com o contrato com o cliente e a legislação aplicável (ex.: LGPD no Brasil, GDPR se houver titulares na UE).

## Retenção

1. **Dados de conta e perfil** — manter apenas enquanto a relação contratual existir; após cancelamento, aplicar política de eliminação ou anonimização (prazo definido em contrato, tipicamente 30–90 dias para recuperação, depois purge).
2. **Registos de auditoria e segurança** — período mais longo pode ser necessário para investigação de incidentes e obrigações legais; documentar base legal e prazo máximo; aplicar minimização (campos estritamente necessários).
3. **Backups** — não prolongar indefinidamente a vida dos dados: política de **retenção de cópias** (ex.: rotação diária/semanal/mensal com expiração automática).
4. **Pedidos de eliminação (LGPD)** — após conclusão do pedido, eliminar ou anonimizar nas bases primárias **e** garantir que backups expiram dentro do prazo acordado ou que exista processo controlado de purge em cópias restauradas.

## Backups

- **Frequência** — alinhar RPO/RTO ao SLA; documentar no runbook.
- **Cifragem** — em repouso e em trânsito; chaves geridas num serviço de secrets (não em repositório).
- **Testes de restauro** — exercícios periódicos (ex. trimestrais) com registo de data, âmbito e resultado.
- **Localização** — jurisdição do armazenamento e subprocessadores declarados no DPA.

## Responsabilidades

| Área | Ação |
|------|------|
| Produto | Definir quais entidades são apagadas no cancelamento vs. arquivadas por obrigação legal |
| Infra | Automatizar retenção de backups, monitorização de falhas de backup |
| Jurídico / DPO | Aprovar prazos e bases legais; responder a titulares e autoridades |

---

*Modelo genérico: adaptar antes de uso comercial ou auditoria.*
