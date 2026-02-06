# Tutorial 4: Colaboração em Equipe

**Duração estimada:** 3-5 minutos  
**Nível:** Intermediário  
**Objetivo:** Trabalhar eficientemente em equipe usando recursos colaborativos

---

## 👥 Recursos de Colaboração

### 1. **Atribuição de Membros**

**Como Adicionar Colaboradores:**
1. Abra a investigação
2. Clique em **"Equipe"** → **"+ Adicionar Membro"**
3. Digite nome ou email
4. Selecione permissão

**Níveis de Permissão:**
```
👁️ Visualizador
   • Ver investigação
   • Ver documentos
   • Ver comentários
   ✗ Não pode editar

✏️ Editor
   • Tudo do Visualizador
   • Editar informações
   • Upload documentos
   • Adicionar comentários
   ✗ Não pode deletar

🔧 Gestor
   • Tudo do Editor
   • Gerenciar equipe
   • Deletar conteúdo
   • Configurações avançadas
```

### 2. **Comentários e Discussões**

**Adicionar Comentário:**
```
┌────────────────────────────────────┐
│ 💬 Novo Comentário                 │
├────────────────────────────────────┤
│                                    │
│ @maria verificou a matrícula?     │
│ Precisamos confirmar antes da     │
│ vistoria de sexta-feira.          │
│                                    │
│ [📎 Anexar]  [😊 Emoji]           │
│                                    │
│ [Comentar]  [Cancelar]            │
└────────────────────────────────────┘
```

**Recursos:**
- **@menções**: Notifica usuário específico
- **#tags**: Organiza discussões
- **Anexos**: Até 5MB por comentário
- **Markdown**: Formatação rica

**Exemplo com Formatação:**
```markdown
@joao encontrei **3 irregularidades**:

1. Matrícula sem averbação
2. Contrato sem reconhecimento de firma
3. Área divergente (500ha vs 480ha cadastrados)

Anexo: análise_completa.pdf

#urgente #documentacao
```

### 3. **Tarefas e Atribuições**

**Criar Tarefa:**
```
┌────────────────────────────────────────────┐
│ ✅ Nova Tarefa                             │
├────────────────────────────────────────────┤
│                                            │
│ Título: Vistoria in loco                  │
│ Responsável: @maria                       │
│ Prazo: 28/02/2024                         │
│ Prioridade: Alta                          │
│                                            │
│ Descrição:                                │
│ Realizar vistoria na Fazenda São José    │
│ Verificar:                                │
│ • Cercas e limites                        │
│ • Ocupação atual                          │
│ • Benfeitorias                            │
│                                            │
│ [Criar Tarefa]                            │
└────────────────────────────────────────────┘
```

**Quadro Kanban:**
```
┌─────────┬──────────────┬───────────┬──────────┐
│ A Fazer │ Em Progresso │ Em Revisão│ Concluído│
├─────────┼──────────────┼───────────┼──────────┤
│         │              │           │          │
│ [Tarefa]│   [Tarefa]   │  [Tarefa] │ [Tarefa] │
│ Análise │   Vistoria   │  Relatório│ Matrícula│
│ jurídica│              │           │          │
│         │              │           │          │
│ [Tarefa]│              │           │ [Tarefa] │
│ Fotos   │              │           │ Contratos│
│         │              │           │          │
└─────────┴──────────────┴───────────┴──────────┘

Arraste entre colunas para atualizar status
```

### 4. **Notificações Inteligentes**

**Configurar Notificações:**
```yaml
Eventos para Notificar:
  ✅ Menção do meu nome (@você)
  ✅ Nova tarefa atribuída
  ✅ Comentário em investigação que sigo
  ✅ Documento adicionado
  ✅ Status alterado
  ☐ Qualquer atualização
  ☐ Relatórios semanais

Canais:
  ✅ Email (imediato)
  ✅ Push (navegador)
  ✅ App mobile
  ☐ SMS
  ☐ Slack
  ☐ Teams
```

### 5. **Histórico de Atividades**

```
┌──────────────────────────────────────────────┐
│ 📜 Timeline de Atividades                    │
├──────────────────────────────────────────────┤
│                                              │
│ Hoje, 14:30                                  │
│ 👤 @maria adicionou comentário              │
│    "Vistoria concluída. Anexo relatório."   │
│    [Ver Comentário]                          │
│                                              │
│ Hoje, 11:20                                  │
│ 📄 @joao fez upload de 3 documentos         │
│    • contrato_arrendamento.pdf              │
│    • foto_fachada.jpg                       │
│    • coordenadas.kml                        │
│    [Ver Documentos]                          │
│                                              │
│ Ontem, 16:45                                 │
│ ✅ @pedro concluiu tarefa                   │
│    "Análise jurídica completa"              │
│    Status: ✅ Concluído                     │
│                                              │
│ 22/01, 10:00                                 │
│ 🔄 @ana alterou status                      │
│    Ativa → Em Revisão                       │
│                                              │
│ [Carregar Mais]                              │
└──────────────────────────────────────────────┘
```

---

## 🔔 Comunicação Efetiva

### Boas Práticas de @Menções

**✅ Use @menções para:**
- Solicitar ação específica
- Pedir opinião/aprovação
- Alertar sobre urgência
- Responder diretamente

**Exemplo Bom:**
```
@maria você pode revisar o contrato antes da reunião
de quinta? Tem algumas cláusulas que precisam de
análise jurídica. #urgente
```

**❌ Evite:**
```
@todos olhem isso (muito genérico)
@maria @joao @pedro @ana (spam)
```

### Estrutura de Comentários

**Template Sugerido:**
```markdown
**[TIPO]**: Pergunta / Info / Alerta / Decisão

**Contexto**: Breve explicação

**Detalhes**: 
- Ponto 1
- Ponto 2

**Ação Necessária**: O que precisa ser feito

**Prazo**: Quando precisa

**Responsável**: @quem

#tag-relevante
```

---

## 📋 Gestão de Tarefas

### Ciclo de Vida da Tarefa

```
[Nova] → [Atribuída] → [Em Progresso] → [Em Revisão] → [Concluída]
          ↓               ↓                ↓
       [Pausada]      [Bloqueada]     [Rejeitada]
```

### Template de Tarefa Completa

```yaml
Título: [Verbo de Ação] + [Objeto]
Exemplo: "Revisar contratos de arrendamento"

Descrição:
  O quê: Revisar 12 contratos
  Por quê: Verificar cláusulas irregulares
  Como: Checklist de conformidade anexo
  
Responsável: @usuario
Prazo: DD/MM/AAAA
Prioridade: Alta/Média/Baixa

Subtarefas:
  □ Coletar todos contratos
  □ Aplicar checklist
  □ Documentar irregularidades
  □ Elaborar parecer

Dependências:
  → Aguarda: Tarefa #45 (Coleta de documentos)

Documentos Anexos:
  • checklist_conformidade.pdf
  • modelo_parecer.docx
```

---

## 🎯 Fluxos de Trabalho

### Fluxo: Nova Investigação

```
1. PLANEJAMENTO (Líder)
   └─> Criar investigação
   └─> Definir objetivos
   └─> Atribuir equipe
   └─> Criar tarefas iniciais

2. COLETA DE DADOS (Equipe)
   └─> Upload de documentos
   └─> Comentários com findings
   └─> Atualizar status das tarefas

3. ANÁLISE (Analistas)
   └─> Revisar evidências
   └─> Discussão em comentários
   └─> Solicitar informações adicionais

4. REVISÃO (Supervisor)
   └─> Validar análises
   └─> Aprovar ou solicitar correções
   └─> Mover para conclusão

5. CONCLUSÃO (Líder)
   └─> Gerar relatório
   └─> Obter aprovação final
   └─> Arquivar investigação
```

### Fluxo: Revisão de Documentos

```
📄 Documento Novo
    ↓
[Upload] → Notifica @revisor
    ↓
@revisor comenta: "Aprovado" ou "Correções necessárias"
    ↓
Se correções:
    └─> @autor corrige
    └─> @revisor revisa novamente
    ↓
[Documento Aprovado] → Marca como ✅
```

---

## 💡 Dicas de Produtividade

### Daily Standup Virtual

Use comentários para standup diário:
```markdown
## Daily - 05/02/2024

@joao
✅ Ontem: Análise de 5 contratos
🔄 Hoje: Finalizar análise jurídica
🚧 Bloqueio: Aguardando certidões

@maria
✅ Ontem: Vistoria in loco
🔄 Hoje: Upload fotos e relatório
🚧 Bloqueio: Nenhum

@pedro
✅ Ontem: Revisão de documentos
🔄 Hoje: Iniciar relatório final
🚧 Bloqueio: Nenhum
```

### Reuniões Assíncronas

Em vez de reunião, use **Threads de Discussão**:

```
📌 Tópico: Decisão sobre ação legal

@joao (14:30):
Proposta: Entrar com ação de reintegração de posse.
Prazo para manifestações: até 17h de hoje.

@maria (14:45):
👍 Concordo. Evidências são sólidas.

@pedro (15:20):
⚠️ Sugestão: Aguardar mais 5 dias para coletar
certidão pendente. Fortalece caso.

@joao (15:40):
✅ Aceito. Nova data: 10/02. @maria por favor
solicitar certidão urgente.

[Decisão]: Aguardar até 10/02 | Responsável: @maria
```

---

## 🔐 Privacidade e Segurança

### Investigações Confidenciais

```
Nível: CONFIDENCIAL

Acesso Restrito:
  ✅ João Silva (Líder)
  ✅ Maria Santos (Analista)
  ✅ Pedro Costa (Jurídico)
  ❌ Outros usuários

Proteções Ativas:
  • Comentários visíveis apenas para equipe
  • Documentos com watermark
  • Log de todos os acessos
  • Proibida exportação não autorizada
  • Notificação de tentativas de acesso
```

---

## 📱 Colaboração Mobile

### App Mobile - Funcionalidades

```
✅ Ver investigações atribuídas
✅ Ler e responder comentários
✅ Atualizar status de tarefas
✅ Upload de fotos (câmera)
✅ Notificações push
✅ Modo offline (sync depois)

⚠️ Limitado:
- Edição de investigação
- Configurações avançadas
- Relatórios complexos
```

---

## 📚 Recursos Adicionais

- [Tutorial 5: Integrações Jurídicas](./05-integracoes.md)
- [Guia de Permissões](../guias/permissoes.md)
- [Casos de Uso: Equipe Distribuída](../casos-uso/equipe-distribuida.md)

---

**Última atualização:** 05/02/2026  
**Versão:** 1.0
