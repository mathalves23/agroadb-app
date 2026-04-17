# Tutorial 2: Entendendo o Dashboard

**Duração estimada:** 3-5 minutos  
**Nível:** Iniciante  
**Objetivo:** Dominar o dashboard do AgroADB e interpretar métricas-chave

---

## 📊 Visão Geral do Dashboard

O Dashboard é o centro de controle do AgroADB, oferecendo uma visão consolidada de todas as suas investigações, métricas de performance e alertas importantes.

---

## 🎯 Componentes Principais

### 1. **Cabeçalho Superior**

```
┌─────────────────────────────────────────────────────────────┐
│  🏠 AgroADB          Investigações  Analytics  Configurações │
│                                                        👤 João│
└─────────────────────────────────────────────────────────────┘
```

**Elementos:**
- Logo e nome do sistema
- Menu de navegação principal
- Barra de pesquisa global (`Ctrl + K`)
- Notificações (🔔)
- Perfil do usuário

---

### 2. **Widgets de Métricas (Cards Superiores)**

#### Card 1: Investigações Ativas
```
┌──────────────────────┐
│ 📁 Investigações     │
│    Ativas            │
│                      │
│    42               │
│    ↑ 5 esta semana  │
└──────────────────────┘
```

**O que significa:**
- Número total de investigações em andamento
- Crescimento/declínio em relação à semana anterior
- Clique para ver lista completa

**Interpretação:**
- ↑ Verde: Aumento de casos (pode indicar sobrecarga)
- ↓ Vermelho: Redução (pode indicar conclusões)

#### Card 2: Pendências
```
┌──────────────────────┐
│ ⏰ Pendências        │
│                      │
│    8                │
│    3 urgentes       │
└──────────────────────┘
```

**O que inclui:**
- Documentos para revisar
- Aprovações pendentes
- Prazos próximos (< 3 dias)
- Comentários não lidos

**Ação:** Clique para ver detalhes e priorizar

#### Card 3: Conclusões
```
┌──────────────────────┐
│ ✅ Concluídas        │
│    este mês          │
│                      │
│    15               │
│    Taxa: 78%        │
└──────────────────────┘
```

**Métricas:**
- Investigações finalizadas no mês
- Taxa de conclusão (meta: > 70%)
- Comparação com mês anterior

#### Card 4: Tempo Médio
```
┌──────────────────────┐
│ ⏱️  Tempo Médio      │
│    de Conclusão      │
│                      │
│    45 dias          │
│    ↓ -5 dias        │
└──────────────────────┘
```

**Análise:**
- Tempo médio para fechar casos
- Tendência de melhoria/piora
- Benchmark interno

---

### 3. **Gráfico de Investigações ao Longo do Tempo**

```
Investigações por Mês (Últimos 6 meses)

50 │                            ●
40 │                  ●         │  ●
30 │        ●         │         │  │  ●
20 │  ●     │         │         │  │  │
10 │  │     │         │         │  │  │
 0 └──┴─────┴─────────┴─────────┴──┴──┴───
   Jan   Fev   Mar   Abr   Mai  Jun  Jul

   ● Iniciadas    ● Concluídas
```

**Insights:**
- Sazonalidade de casos
- Capacidade da equipe
- Planejamento de recursos

**Interatividade:**
- Hover: Ver valores exatos
- Clique: Filtrar por mês

---

### 4. **Minhas Investigações Recentes**

```
┌─────────────────────────────────────────────────────────────┐
│ 📋 Minhas Investigações (5 mais recentes)                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ 🔴 #1234  Arrendamento - Fazenda São José        Status: Ativa│
│           Prioridade: Alta  |  Prazo: 3 dias restantes      │
│           ▓▓▓▓▓▓▓░░░ 65% completo                          │
│                                                               │
│ 🟡 #1235  Due Diligence - Vale do Rio           Status: Ativa│
│           Prioridade: Média  |  Prazo: 15 dias              │
│           ▓▓▓▓░░░░░░ 40% completo                          │
│                                                               │
│ 🟢 #1232  Auditoria - Grupo ABC            Status: Concluída│
│           Prioridade: Baixa  |  Concluída há 2 dias         │
│           ▓▓▓▓▓▓▓▓▓▓ 100% completo                          │
│                                                               │
│                             [Ver Todas] →                     │
└─────────────────────────────────────────────────────────────┘
```

**Elementos:**
- Indicador de prioridade (🔴🟡🟢)
- Número e título da investigação
- Status atual
- Prazo e tempo restante
- Barra de progresso

**Ações Rápidas:**
- Clique: Abrir investigação
- Hover: Preview rápido
- Menu ⋮: Editar, Arquivar, Compartilhar

---

### 5. **Distribuição por Status**

```
┌────────────────────────────┐
│ Status das Investigações   │
├────────────────────────────┤
│                            │
│     🟡 Ativas: 42 (58%)   │
│     🔵 Rascunho: 8 (11%)  │
│     🟢 Concluídas: 15(21%)│
│     ⚫ Arquivadas: 7 (10%)│
│                            │
│   [Gráfico de Pizza]       │
└────────────────────────────┘
```

**Análise:**
- Distribuição saudável: Ativas 50-60%
- Rascunhos < 15% (evitar acúmulo)
- Taxa de conclusão > 20%

---

### 6. **Distribuição por Prioridade**

```
┌────────────────────────────┐
│ Prioridade                 │
├────────────────────────────┤
│                            │
│  🔴 Alta:   12 casos (29%) │
│     ▓▓▓▓▓▓▓▓░░            │
│                            │
│  🟡 Média:  22 casos (52%) │
│     ▓▓▓▓▓▓▓▓▓▓▓▓▓░░       │
│                            │
│  🟢 Baixa:   8 casos (19%) │
│     ▓▓▓▓▓░░                │
└────────────────────────────┘
```

**Balanceamento Ideal:**
- Alta: 20-30% (casos urgentes)
- Média: 50-60% (fluxo normal)
- Baixa: 15-25% (planejamento)

**Alerta:** Se Alta > 40%, revisar alocação de recursos

---

### 7. **Alertas e Notificações**

```
┌────────────────────────────────────────────────┐
│ 🔔 Alertas Importantes                         │
├────────────────────────────────────────────────┤
│                                                 │
│ ⚠️  3 investigações com prazo em 2 dias       │
│     #1234, #1240, #1245                        │
│     [Ver Detalhes]                             │
│                                                 │
│ 📄 5 novos documentos aguardando revisão      │
│     [Revisar Agora]                            │
│                                                 │
│ 💬 8 comentários não lidos                     │
│     [Ver Comentários]                          │
│                                                 │
│ ✅ 2 investigações prontas para conclusão     │
│     #1230, #1231                               │
│     [Finalizar]                                │
└────────────────────────────────────────────────┘
```

**Tipos de Alertas:**
- 🔴 Crítico: Prazo vencido
- 🟡 Atenção: Prazo próximo (< 3 dias)
- 🟢 Info: Atualizações gerais

---

### 8. **Timeline de Atividades**

```
┌────────────────────────────────────────────────────┐
│ 📅 Atividades Recentes                            │
├────────────────────────────────────────────────────┤
│                                                     │
│ Hoje, 14:30                                        │
│ 👤 João Silva comentou em #1234                   │
│    "Vistoria agendada para sexta-feira"           │
│                                                     │
│ Hoje, 11:15                                        │
│ 📄 Maria Santos adicionou 3 documentos em #1235   │
│    [Ver Documentos]                                │
│                                                     │
│ Ontem, 16:45                                       │
│ ✅ Pedro Costa concluiu #1232                     │
│    "Auditoria aprovada sem ressalvas"             │
│                                                     │
│ 22/01, 10:00                                       │
│ 🔄 Ana Lima atualizou status de #1240            │
│    Ativa → Em Revisão                             │
│                                                     │
│                        [Carregar Mais] ↓           │
└────────────────────────────────────────────────────┘
```

**Filtros Disponíveis:**
- Por usuário
- Por tipo de atividade
- Por investigação
- Por período

---

## 🎛️ Personalizando Seu Dashboard

### Reorganizar Widgets

1. Clique no ícone **⚙️** (canto superior direito)
2. Ative **"Modo de Edição"**
3. Arraste widgets para nova posição
4. Clique **"Salvar Layout"**

### Adicionar/Remover Widgets

**Widgets Disponíveis:**
- ✅ Métricas de Performance
- ✅ Gráficos de Tendência
- ✅ Lista de Investigações
- ✅ Alertas
- ✅ Timeline
- ✅ Mapa de Casos (geoespacial)
- ✅ Estatísticas da Equipe
- ✅ Tarefas Pendentes

**Como Adicionar:**
1. Modo de edição ativado
2. Clique **"+ Adicionar Widget"**
3. Selecione da biblioteca
4. Configure parâmetros

### Filtros Globais

```
┌─────────────────────────────────────────────┐
│ 🔍 Filtros                                   │
├─────────────────────────────────────────────┤
│                                              │
│ Período: [Últimos 30 dias ▼]               │
│ Status:  [Todos ▼]                          │
│ Equipe:  [Minha Equipe ▼]                  │
│ Prioridade: [Todas ▼]                       │
│                                              │
│ [Aplicar Filtros]  [Limpar]                │
└─────────────────────────────────────────────┘
```

---

## 📊 Interpretando Métricas

### Taxa de Conclusão

**Fórmula:**
```
Taxa = (Concluídas / Total Iniciadas) × 100
```

**Benchmarks:**
| Taxa | Interpretação |
|------|---------------|
| > 80% | Excelente |
| 70-80% | Bom |
| 50-70% | Adequado |
| < 50% | Revisar processos |

### Tempo Médio de Conclusão

**Como calcular:**
```
Tempo Médio = Soma(Data Conclusão - Data Início) / Número de Casos
```

**Por Tipo de Caso:**
| Tipo | Tempo Ideal |
|------|-------------|
| Simples | 7-15 dias |
| Moderado | 30-45 dias |
| Complexo | 60-90 dias |

### Produtividade da Equipe

```
┌────────────────────────────────────┐
│ Top Performers (Este Mês)         │
├────────────────────────────────────┤
│                                    │
│ 1. João Silva                     │
│    8 casos concluídos             │
│    Média: 35 dias                 │
│    ⭐⭐⭐⭐⭐                      │
│                                    │
│ 2. Maria Santos                   │
│    6 casos concluídos             │
│    Média: 42 dias                 │
│    ⭐⭐⭐⭐                        │
│                                    │
│ 3. Pedro Costa                    │
│    5 casos concluídos             │
│    Média: 38 dias                 │
│    ⭐⭐⭐⭐                        │
└────────────────────────────────────┘
```

---

## 🚨 Alertas e Notificações

### Configurar Notificações

1. Clique em **👤 Perfil** → **Configurações**
2. Aba **"Notificações"**
3. Configure preferências:

```
✅ Email
  ✓ Prazos próximos (3 dias)
  ✓ Menções ao meu nome
  ✓ Novos documentos
  ✗ Atualizações gerais

✅ Push (Navegador)
  ✓ Alertas críticos
  ✓ Mensagens diretas
  ✗ Comentários

✅ Resumo Diário
  ✓ Enviar às 09:00
  ✓ Incluir pendências
  ✓ Incluir estatísticas
```

### Tipos de Alertas

**🔴 Críticos:**
- Prazo vencido
- Erro em integração
- Documento obrigatório faltando

**🟡 Importantes:**
- Prazo em 24-48h
- Aprovação pendente
- Comentário importante

**🟢 Informativos:**
- Progresso da equipe
- Relatório semanal
- Dicas de uso

---

## 📱 Dashboard Mobile

### Acesso Mobile

O dashboard é responsivo e otimizado para mobile:

**Funcionalidades Disponíveis:**
- ✅ Visualizar métricas principais
- ✅ Acessar investigações
- ✅ Upload de documentos (câmera)
- ✅ Adicionar comentários
- ✅ Receber notificações push

**Limitações:**
- ❌ Edição de layouts
- ❌ Relatórios complexos
- ❌ Configurações avançadas

### App Nativo

**Download:**
- 📱 iOS: App Store → "AgroADB"
- 🤖 Android: Play Store → "AgroADB"

**Recursos Extras:**
- Modo offline
- Sincronização automática
- Geolocalização
- Câmera integrada

---

## 💡 Dicas de Uso

### Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `Ctrl + K` | Busca global |
| `Ctrl + N` | Nova investigação |
| `Ctrl + D` | Ir para dashboard |
| `Ctrl + ,` | Configurações |
| `/` | Focar na busca |
| `?` | Mostrar ajuda |

### Produtividade

**Morning Routine (5 min):**
1. Verificar alertas críticos
2. Revisar pendências do dia
3. Priorizar 3 tarefas principais
4. Responder comentários urgentes

**Weekly Review (15 min):**
1. Analisar métricas da semana
2. Verificar prazos próximos
3. Atualizar status de casos
4. Planejar semana seguinte

---

## 🎯 Checklist de Dashboard Saudável

```
✅ Casos ativos: 50-60% do total
✅ Taxa de conclusão: > 70%
✅ Tempo médio: Dentro do benchmark
✅ Alertas críticos: 0
✅ Pendências: < 10
✅ Rascunhos: < 15% do total
✅ Documentos revisados: 100%
✅ Comentários lidos: Todos
```

---

## 📚 Recursos Adicionais

- [Tutorial 1: Primeira Investigação](./01-primeira-investigacao.md)
- [Tutorial 3: Gerando Relatórios](./03-relatorios.md)
- [Guia de Analytics Avançado](../guias/analytics-avancado.md)

---

**Última atualização:** 05/02/2026  
**Versão:** 1.0
