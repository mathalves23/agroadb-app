# Manual do utilizador — AgroADB

## Sobre este documento

Este manual descreve o fluxo típico na plataforma de **inteligência patrimonial** AgroADB. **Não substitui** o contrato de prestação de serviços, políticas internas da sua organização nem **aconselhamento jurídico**. Em caso de dúvida legal ou de tratamento de dados pessoais, consulte o **jurídico** ou o **encarregado de protecção de dados (DPO)** da sua entidade.

**Tratamento de dados pessoais (LGPD — referência genérica):** a plataforma pode processar identificadores e dados conexos às investigações autorizadas pela sua organização. A **base legal**, os **prazos de conservação** e os **direitos dos titulares** (acesso, rectificação, eliminação, portabilidade, oposição, etc.) devem estar definidos no **registo de actividades de tratamento (RoPA)** e nos instrumentos contratuais aplicáveis. Os contactos de privacidade/DPO indicados na sua instância ou contrato prevalecem sobre qualquer exemplo neste texto.

**Revisão editorial:** antes de distribuir este conteúdo a utilizadores finais, a equipa de **produto** e **jurídico/DPO** devem validar o alinhamento com a versão da aplicação e com a realidade contratual — ver `product/EDITORIAL_CHECKLIST.md` no repositório.

---

## Mapa de menus (interface actual)

Os nomes abaixo correspondem à navegação habitual da aplicação (menu lateral e barra superior):

| Área na interface | Rota | Descrição breve |
|-------------------|------|-----------------|
| **Dashboard** | `/dashboard` | Resumo e atalhos |
| **Investigações** | `/investigations` | Lista e filtros |
| **Nova Investigação** | `/investigations/new` | Criação de caso |
| **Notificações** | `/notifications` | Centro de alertas |
| **Perfil** | `/profile` | Conta e segurança (ex.: 2FA) |
| **Manual do utilizador** | `/guide` | Este manual na aplicação |
| **Integrações** | `/settings` | Estado das APIs e fontes (configuração no servidor) |

O **menu do utilizador** (ícone/canto superior) inclui atalhos como **Tour guiado**, **Configurações** (ligação a integrações/perfil conforme a versão) e **Manual do utilizador**.

---

## 1. Primeiro acesso

1. Abra o URL fornecido pela sua organização (ou o URL de desenvolvimento que lhe foi indicado).
2. **Registo** — crie conta com e-mail válido e uma palavra-passe forte, salvo se a sua organização usar **provisionamento** por outro meio.
3. **Início de sessão** — use as credenciais indicadas pela organização. Se existir política de **autenticação em dois passos (2FA)**, configure-a em **Perfil** quando lhe for pedido.

Após autenticar, pode aparecer um **tour guiado**. Pode interrompê-lo; no **menu do utilizador** pode **reiniciar o tour** mais tarde, se essa opção estiver disponível.

---

## 2. Dashboard (painel inicial)

Em **Dashboard** (`/dashboard`) encontra, em geral:

- **Indicadores (KPIs)** — totais ou métricas resumidas, consoante os dados e o plano.
- **Lista recente** — atalhos para investigações em curso ou concluídas recentemente.

Utilize **Nova Investigação** para iniciar um caso.

---

## 3. Investigações

### 3.1 Lista de investigações

Em **Investigações** (`/investigations`) vê as fichas. Pode:

- **Filtrar** por estado, datas ou texto (nome, documento), conforme as opções disponíveis na sua versão.
- **Alternar vista** (lista/grelha), se existir.
- Abrir o **detalhe** ao clicar numa linha ou cartão.

### 3.2 Criar investigação

1. Aceda a **Nova Investigação** (`/investigations/new`).
2. Indique o **tipo de alvo** e os **identificadores** permitidos pela **sua política interna** e pela lei (ex.: CPF, CNPJ, nome — apenas quando houver base legal e finalidade legítima).
3. Confirme e aguarde o processamento. O estado evolui (por exemplo: pendente, em progresso, concluída, erro).

### 3.3 Detalhe da investigação

Na página de detalho (`/investigations/:id`) pode encontrar:

- **Resumo** e metadados do caso.
- **Resultados por fonte** (registos públicos, cartografia, integrações judiciais ou outras, quando activas).
- **Mapa** ou visualizações geográficas, quando aplicável.
- **Exportação** — formatos disponíveis dependem do plano e da configuração (ex.: PDF, Excel).

Funcionalidades como **Comentários** ou **Partilha** dependem da configuração da sua organização.

---

## 4. Notificações

O acesso a **Notificações** (`/notifications`) pode estar também na **barra superior**. Aí vê alertas sobre conclusões, falhas relevantes ou mensagens do sistema, conforme a implementação.

---

## 5. Integrações

A página **Integrações** (`/settings`) mostra o estado das **APIs e fontes** ligadas ao backend (dados abertos, chaves opcionais, Conecta gov.br, etc.). Indica se cada integração está **ativa** ou se requer **configuração no servidor** (variáveis de ambiente geridas pela equipa técnica — não expor segredos neste manual).

---

## 6. Perfil e segurança

Em **Perfil** (`/profile`) pode, entre outras acções:

- actualizar dados profissionais;
- alterar palavra-passe;
- configurar **2FA**, se disponível;
- rever opções expostas pela sua versão.

---

## 7. Boas práticas, LGPD e limitações

1. **Finalidade e minimização** — trate apenas os dados necessários à investigação autorizada; evite duplicar dados sensíveis fora da plataforma sem controlo.
2. **Bases legais e titulares** — cumpra as bases legais aplicáveis (contrato, legítimo interesse com balanceamento, cumprimento de obrigação legal, etc.) e responda a pedidos dos titulares nos prazos legais, com os canais definidos pelo DPO.
3. **Dados de teste** — não utilize dados reais de titulares em ambiente de teste sem consentimento específico ou outra base adequada.
4. **Fontes terceiras** — a disponibilidade e o conteúdo das fontes públicas ou contratuais **não são garantidos** pela AgroADB; podem existir limites técnicos, legais ou de quota.
5. **Incidentes** — em caso de violação de dados ou pedido urgente de autoridade, siga o **plano de resposta a incidentes** da sua organização e notifique o DPO/jurídico conforme obrigações legais.

---

## 8. Ajuda na aplicação e documentação técnica

- **Manual do utilizador** — menu lateral, rota `/guide` (conteúdo importado a partir de `product/manual-do-utilizador.md` no repositório).
- **Tour guiado** — menu do utilizador, quando disponível.

Para **documentação técnica** (API, implantação, arquitectura), a equipa de TI deve usar a pasta **`docs/`** do repositório, **separada** deste manual.

---

## 9. Recursos visuais (opcional)

Se a sua organização disponibilizar **capturas de ecrã** ou um **vídeo curto**, estes podem ser colocados em `frontend/public/product-guide/` e referenciados aqui ou mostrados automaticamente na página `/guide` quando os ficheiros existirem (ver `frontend/public/product-guide/README.md`).

---

## Controle de versão editorial (preencher internamente)

| Campo | Valor |
|-------|--------|
| Versão do manual | (ex.: 1.1) |
| Data da última revisão de produto | |
| Data da última revisão jurídica / DPO | |
| Versão da app alinhada | (commit ou release) |

*Este bloco é orientador; pode ser gerido no vosso sistema de tickets ou no `EDITORIAL_CHECKLIST.md`.*
