# DPA e registo de tratamentos (RoPA) — referência SaaS

Quando a aplicação processa **dados pessoais** em nome de clientes (B2B típico), o enquadramento LGPD/GDPR costuma distinguir:

- **Controlador** — quem decide as finalidades e meios (muitas vezes o cliente empresarial).
- **Operador / subprocessador** — quem trata dados por conta do controlador (o fornecedor da plataforma).

## Acordo de tratamento de dados (DPA)

Um **DPA** (Data Processing Agreement / contrato de tratamento de dados) deve, no mínimo, cobrir:

1. **Objeto e duração** do tratamento e natureza dos dados.
2. **Instruções** do controlador e obrigação de tratamento apenas conforme instruído (salvo obrigação legal).
3. **Confidencialidade** das pessoas autorizadas a tratar dados.
4. **Medidas de segurança** técnicas e organizativas (TOMs), com referência a normas ou boas práticas adotadas.
5. **Subprocessadores** — lista ou mecanismo de notificação/autorização prévia; mesmas obrigações em cadeia.
6. **Assistência** ao controlador para direitos dos titulares, DPIA quando aplicável, e notificação de violações.
7. **Eliminação ou devolução** dos dados ao fim do serviço.
8. **Auditoria** — disponibilidade de informações necessárias para demonstrar conformidade.

*Este repositório não substitui aconselhamento jurídico: o DPA final deve ser revisto por advogados qualificados.*

## Registo de atividades de tratamento (RoPA)

O RoPA (registo previsto no art. 37 da LGPD / art. 30 do GDPR) deve listar, por atividade:

| Campo sugerido | Exemplo |
|----------------|---------|
| Nome da atividade | Autenticação de utilizadores |
| Finalidade | Execução do contrato, segurança |
| Categorias de titulares | Utilizadores finais, contactos administrativos |
| Categorias de dados | Identificação, contacto, registos de auditoria |
| Destinatários / subprocessadores | Hospedagem cloud, e-mail transacional |
| Transferências internacionais | País/região e salvaguardas (SCCs, adequação) |
| Prazos de conservação | Conforme política de retenção aprovada |
| Medidas de segurança | MFA, cifragem, RBAC, logs |

Manter o RoPA **atualizado** quando novas funcionalidades ou integrações processarem dados pessoais.

## Ligação ao código

- Rotas administrativas sensíveis devem exigir **superutilizador** ou papel explícito de administração (ver `app/api/v1/deps.py`).
- Auditoria e pedidos LGPD devem estar alinhados às finalidades declaradas no RoPA.

---

*Documento orientador; não constitui parecer jurídico.*
