# Manual do utilizador — AgroADB

Bem-vindo. Este manual descreve o fluxo típico na plataforma de **inteligência patrimonial** AgroADB: painel, investigações, exportações, notificações e integrações.

---

## 1. Primeiro acesso

1. Abra o URL fornecido pela sua organização (ou `http://localhost:5173` em desenvolvimento).
2. **Registo** — crie conta com e-mail válido e uma palavra-passe forte.
3. **Início de sessão** — use o e-mail e a palavra-passe. Se a organização exigir **2FA**, siga o fluxo de configuração no primeiro acesso ao perfil.

Após autenticar, pode aparecer um **tour guiado** (passos sobre o ecrã). Pode saltá-lo a qualquer momento; no menu do utilizador pode **reiniciar o tour** mais tarde.

---

## 2. Dashboard (painel inicial)

O **Dashboard** resume a sua actividade:

- **Indicadores (KPIs)** — totais de investigações, propriedades ou empresas encontradas, consoante os dados disponíveis.
- **Lista recente** — atalhos para investigações em curso ou concluídas recentemente.

Utilize o botão **Nova investigação** para iniciar um caso.

---

## 3. Investigações

### 3.1 Lista de investigações

Em **Investigações** vê todas as fichas. Pode:

- **Filtrar** por estado, datas ou texto (nome, documento).
- **Alternar vista** lista/grelha, se disponível na sua versão.
- Abrir o **detalhe** clicando numa linha ou cartão.

### 3.2 Criar investigação

1. **Nova investigação**.
2. Indique o **tipo de alvo** (ex.: pessoa física, empresa) e os **identificadores** (CPF, CNPJ, nome conforme permitido pela sua política interna).
3. Confirme e aguarde o processamento. O estado evolui (pendente, em progresso, concluída, erro).

### 3.3 Detalhe da investigação

Na página de detalhe pode encontrar:

- **Resumo** e metadados do caso.
- **Resultados por fonte** (ex.: registos públicos, cartografia, dados judiciais quando integrados).
- **Mapa** ou visualizações geográficas, quando aplicável.
- **Exportação** — relatórios em PDF, Excel ou formatos técnicos suportados (depende do plano e da configuração).

Utilize **Comentários** ou **Partilha** (se activos) para colaboração interna.

---

## 4. Notificações

O ícone de **notificações** na barra superior mostra alertas sobre:

- conclusão de tarefas ou investigações;
- falhas que requerem atenção;
- mensagens do sistema.

Na página de notificações pode marcar como lidas ou rever o histórico.

---

## 5. Integrações (definições)

Em **Integrações** (ou **Definições → Integrações**) consulta o estado das **APIs e fontes** ligadas ao backend (dados abertos, chaves opcionais, Conecta gov.br, etc.). O painel indica se cada integração está **ativa** ou requer configuração no servidor (variáveis de ambiente geridas pela equipa técnica).

---

## 6. Perfil e segurança

Em **Perfil** pode:

- actualizar nome e dados profissionais;
- alterar palavra-passe;
- configurar **autenticação em dois passos (2FA)**;
- rever sessões ou preferências expostas pela sua versão.

---

## 7. Boas práticas e conformidade

- Trate **dados pessoais** apenas para finalidades autorizadas pela sua organização e pela lei aplicável (ex.: LGPD).
- **Minimize** a criação de investigações de teste com dados reais de titulares sem consentimento ou base legal.
- Em caso de **incidente** ou pedido de titular, contacte o **encarregado de protecção de dados (DPO)** ou o canal interno indicado no contrato.

---

## 8. Ajuda dentro da aplicação

- Menu lateral: **Manual do utilizador** — esta documentação formatada na app.
- **Tour guiado** — no menu do utilizador, opção para repetir o tour de boas-vindas.

Para documentação técnica (API, implantação, arquitectura), a equipa de TI deve consultar a pasta **`docs/`** do repositório, separada deste manual.

---

*Última actualização editorial: documento vivo; solicite à sua organização versões aprovadas internamente.*
