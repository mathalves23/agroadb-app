# Tutorial 1: Como Criar Sua Primeira Investigação

**Duração estimada:** 5-7 minutos  
**Nível:** Iniciante  
**Objetivo:** Aprender a criar e configurar uma investigação completa no AgroADB

---

## 📋 O Que Você Vai Aprender

- Como acessar o módulo de investigações
- Preenchimento correto de todos os campos
- Configuração de prioridades e status
- Atribuição de responsáveis
- Upload de documentos iniciais
- Boas práticas de nomenclatura

---

## 🎯 Pré-requisitos

- ✅ Acesso ao sistema AgroADB
- ✅ Permissões de criação de investigações
- ✅ Dados básicos do caso a ser investigado

---

## Passo 1: Acessando o Módulo de Investigações

### 1.1 Login no Sistema

1. Acesse o AgroADB através do seu navegador
2. Faça login com suas credenciais
3. Você será direcionado ao **Dashboard Principal**

### 1.2 Navegando para Investigações

**Opção 1 - Menu Lateral:**
```
🏠 Dashboard
📁 Investigações  ← Clique aqui
👥 Usuários
📊 Analytics
⚙️  Configurações
```

**Opção 2 - Atalho:**
- Pressione `Ctrl + I` (Windows/Linux) ou `Cmd + I` (Mac)
- Ou clique no botão **"+ Nova Investigação"** no dashboard

### 1.3 Interface de Investigações

Você verá uma lista de investigações existentes com:
- **Status** (Ativa, Concluída, Arquivada)
- **Prioridade** (Alta, Média, Baixa)
- **Responsável**
- **Data de criação**
- **Última atualização**

---

## Passo 2: Criando Nova Investigação

### 2.1 Iniciando o Processo

1. Clique no botão **"+ Nova Investigação"** (canto superior direito)
2. Um formulário será aberto com campos obrigatórios e opcionais

### 2.2 Preenchendo Informações Básicas

#### **Título da Investigação** (Obrigatório)

**Boas práticas de nomenclatura:**

```
✅ BOM:
- "Arrendamento Irregular - Fazenda São José - 2024"
- "Due Diligence - Aquisição Terras Vale do Rio - Q1/2024"
- "Grilagem Suspeita - Região Norte - Município XYZ"

❌ EVITAR:
- "Investigação 1"
- "Caso importante"
- "Verificar"
```

**Dica:** Use formato claro:
```
[Tipo do Caso] - [Local/Propriedade] - [Período]
```

#### **Descrição** (Obrigatório)

Forneça contexto detalhado:

```markdown
**O QUE:** Suspeita de arrendamento irregular de terras públicas

**ONDE:** Fazenda São José, Município de Campo Grande/MS

**QUANDO:** Identificado em 15/01/2024

**CONTEXTO:**
Denúncia anônima reportou arrendamento de área de 500 hectares
sem autorização do órgão competente. Área pode estar sobreposta
a terras da União.

**OBJETIVO:**
- Verificar titularidade das terras
- Confirmar existência de contrato de arrendamento
- Identificar partes envolvidas
- Avaliar impactos ambientais

**DOCUMENTOS INICIAIS:**
- Denúncia anônima (PDF)
- Coordenadas geográficas
- Imagens de satélite
```

**Caracteres recomendados:** 200-500 caracteres (mínimo: 50)

---

### 2.3 Configurando Status e Prioridade

#### **Status da Investigação**

Selecione o status inicial:

| Status | Quando Usar |
|--------|-------------|
| **🟡 Rascunho** | Investigação ainda em planejamento |
| **🔵 Ativa** | Investigação em andamento (padrão) |
| **🟢 Concluída** | Investigação finalizada |
| **⚫ Arquivada** | Investigação suspensa/cancelada |

**Recomendação:** Comece sempre com **Ativa** para casos urgentes ou **Rascunho** para planejamento.

#### **Prioridade**

Defina a urgência:

| Prioridade | Critérios | Exemplo |
|------------|-----------|---------|
| **🔴 Alta** | Urgente, prazos legais, risco iminente | Ordem judicial, denúncia grave |
| **🟡 Média** | Importante, prazo moderado | Due diligence comercial |
| **🟢 Baixa** | Rotineira, sem prazo crítico | Auditoria preventiva |

**Matriz de Priorização:**
```
ALTO IMPACTO + URGENTE = ALTA
ALTO IMPACTO + NÃO URGENTE = MÉDIA
BAIXO IMPACTO + URGENTE = MÉDIA
BAIXO IMPACTO + NÃO URGENTE = BAIXA
```

---

### 2.4 Atribuindo Responsáveis

#### **Investigador Principal**

1. Clique no campo **"Responsável"**
2. Digite o nome ou email do investigador
3. Selecione da lista de usuários

**Dica:** O investigador principal será notificado automaticamente.

#### **Equipe Colaboradora** (Opcional)

1. Clique em **"Adicionar Colaborador"**
2. Selecione múltiplos usuários
3. Defina permissões:
   - 👁️ **Visualização**: Apenas leitura
   - ✏️ **Edição**: Pode modificar
   - 🗑️ **Gestão**: Controle total

**Exemplo de Equipe:**
```
👤 João Silva (Investigador Principal)
   └── Permissão: Gestão

👥 Colaboradores:
   ├── Maria Santos (Analista)
   │   └── Permissão: Edição
   ├── Pedro Costa (Advogado)
   │   └── Permissão: Visualização
   └── Ana Lima (Estagiária)
       └── Permissão: Visualização
```

---

### 2.5 Definindo Datas e Prazos

#### **Data de Início** (Obrigatório)

- Padrão: Data atual
- Pode ser alterada para data retroativa

#### **Data Prevista de Conclusão** (Opcional)

Calcule baseado em:
- Complexidade do caso
- Recursos disponíveis
- Prazos legais

**Guia de Estimativa:**

| Tipo de Investigação | Prazo Típico |
|----------------------|--------------|
| Verificação Simples | 7-15 dias |
| Due Diligence | 30-45 dias |
| Investigação Complexa | 60-90 dias |
| Auditoria Completa | 90-120 dias |

#### **Marco Críticos** (Opcional)

Adicione datas importantes:
```
📅 15/02/2024 - Vistoria in loco
📅 28/02/2024 - Relatório preliminar
📅 15/03/2024 - Audiência
📅 30/03/2024 - Relatório final
```

---

### 2.6 Categorizando a Investigação

#### **Tags e Etiquetas**

Adicione tags para organização:

```
Sugestões de Tags:
#arrendamento
#terras-publicas
#grilagem
#due-diligence
#ambiental
#regularizacao-fundiaria
#grupo-economico
#judicial
```

**Como Adicionar:**
1. Digite a tag no campo
2. Pressione Enter
3. Tag é adicionada com cor automática

#### **Categoria Principal**

Selecione uma categoria:
- 🏞️ Fundiário
- 🌳 Ambiental
- 💼 Comercial
- ⚖️ Jurídico
- 🔍 Investigativo

---

### 2.7 Configurações Avançadas

#### **Nível de Confidencialidade**

| Nível | Descrição | Acesso |
|-------|-----------|--------|
| 🟢 **Público** | Informações públicas | Todos usuários |
| 🟡 **Interno** | Restrito à organização | Equipe interna |
| 🔴 **Confidencial** | Altamente sensível | Apenas equipe do caso |
| ⚫ **Secreto** | Extrema confidencialidade | Apenas gestor + principal |

**Recomendação:** Comece com **Interno** e ajuste conforme necessário.

#### **Notificações**

Configure quando receber alertas:
- ✅ Novo comentário
- ✅ Documento adicionado
- ✅ Status alterado
- ✅ Prazo se aproximando (3 dias antes)
- ✅ Menção do seu nome

---

## Passo 3: Adicionando Documentos Iniciais

### 3.1 Upload de Arquivos

1. Role até a seção **"Documentos"**
2. Clique em **"Adicionar Documentos"**
3. Selecione arquivo(s) ou arraste para a área

**Formatos Suportados:**
```
📄 Documentos: PDF, DOC, DOCX, TXT
📊 Planilhas: XLS, XLSX, CSV
🖼️ Imagens: JPG, PNG, GIF
🗺️ Geoespacial: KML, KMZ, SHP
📦 Compactados: ZIP, RAR
```

**Limites:**
- Tamanho máximo por arquivo: 50 MB
- Total por investigação: 500 MB (pode ser ampliado)

### 3.2 Organizando Documentos

#### **Categorias de Documentos**

Organize por tipo:

```
📁 Investigação #123
  ├── 📂 Denúncias
  │   └── denuncia_anonima.pdf
  ├── 📂 Documentação Legal
  │   ├── matricula_imovel.pdf
  │   └── contrato_arrendamento.pdf
  ├── 📂 Imagens e Mapas
  │   ├── foto_aerea_2024.jpg
  │   └── coordenadas.kml
  └── 📂 Relatórios
      └── relatorio_preliminar.docx
```

#### **Metadados**

Para cada documento, preencha:
- **Título descritivo**
- **Descrição** (opcional)
- **Data do documento**
- **Fonte** (ex: "Cartório de Imóveis")
- **Tags** (#matricula, #contrato, etc)

### 3.3 Documentos Linkados

Adicione links para documentos externos:
```
🔗 https://drive.google.com/file/...
🔗 https://cartorio.gov.br/certidao/...
🔗 https://incra.gov.br/consulta/...
```

---

## Passo 4: Salvando e Finalizando

### 4.1 Revisão Final

Antes de salvar, verifique:

**Checklist:**
```
✅ Título claro e descritivo
✅ Descrição completa (mínimo 50 caracteres)
✅ Status configurado
✅ Prioridade definida
✅ Responsável atribuído
✅ Datas preenchidas
✅ Pelo menos 1 documento adicionado (recomendado)
✅ Tags e categoria definidas
```

### 4.2 Salvando a Investigação

**Opções de Salvamento:**

1. **Salvar como Rascunho**
   - Botão: **"Salvar Rascunho"**
   - A investigação não fica visível para toda equipe
   - Útil para planejar antes de iniciar

2. **Salvar e Ativar**
   - Botão: **"Criar Investigação"** (botão azul)
   - Investigação fica imediatamente ativa
   - Equipe é notificada automaticamente

3. **Salvar e Adicionar Outra**
   - Botão: **"Salvar e Criar Nova"**
   - Útil para criar múltiplas investigações

**Atalhos:**
- `Ctrl + S` / `Cmd + S` - Salvar rascunho
- `Ctrl + Enter` / `Cmd + Enter` - Criar investigação

### 4.3 Confirmação

Após salvar, você verá:
```
✅ Investigação criada com sucesso!

📋 Investigação #1234
   "Arrendamento Irregular - Fazenda São José"

Próximos passos:
▶ Adicionar mais documentos
▶ Convidar colaboradores
▶ Iniciar análise
```

---

## Passo 5: Próximas Ações

### 5.1 Visualizando Sua Investigação

A investigação criada estará disponível em:
1. **Lista de Investigações** (ordenada por data de criação)
2. **Seu Dashboard** (seção "Minhas Investigações")
3. **Barra de Pesquisa** (use o número ou título)

### 5.2 Editando Informações

Para editar a investigação:
1. Clique na investigação na lista
2. Botão **"Editar"** no canto superior direito
3. Ou pressione `E` quando estiver visualizando

### 5.3 Adicionando Mais Conteúdo

**Timeline de Ações:**
```
Dia 1: Criar investigação + Upload documentos iniciais
Dia 2-3: Análise preliminar + Adicionar notas
Dia 4-7: Coleta de evidências + Atualizações diárias
Semana 2: Vistoria + Fotos + Relatório preliminar
Semana 3-4: Análise aprofundada + Parecer técnico
Mês 2: Relatório final + Conclusões
```

---

## 💡 Dicas e Boas Práticas

### ✅ DO (Faça)

1. **Título Descritivo**
   - Use padrão consistente
   - Inclua local e ano
   - Seja específico

2. **Documentação Desde o Início**
   - Upload todos documentos relevantes
   - Organize em pastas lógicas
   - Use metadados completos

3. **Atualizações Regulares**
   - Registre progresso diariamente
   - Use comentários para comunicação
   - Atualize status conforme avança

4. **Colaboração Efetiva**
   - Atribua tarefas claras
   - Use @menções para notificar
   - Compartilhe findings importantes

5. **Backup de Segurança**
   - Exporte relatórios regularmente
   - Mantenha cópias de documentos críticos

### ❌ DON'T (Evite)

1. **Títulos Genéricos**
   - ❌ "Investigação 1"
   - ✅ "Due Diligence - Fazenda Vista Alegre - Q1/2024"

2. **Descrições Vazias**
   - ❌ "Verificar"
   - ✅ Contexto completo com objetivos

3. **Falta de Organização**
   - ❌ Todos documentos soltos
   - ✅ Estrutura de pastas clara

4. **Ignorar Prazos**
   - ❌ Sem data de conclusão
   - ✅ Prazos realistas configurados

5. **Trabalhar Sozinho**
   - ❌ Não adicionar colaboradores
   - ✅ Equipe completa desde o início

---

## 🎯 Exemplo Prático Completo

### Caso: Investigação de Arrendamento Irregular

```yaml
INVESTIGAÇÃO #1234
==================

INFORMAÇÕES BÁSICAS:
  Título: "Arrendamento Irregular - Fazenda São José - 2024"
  Status: Ativa
  Prioridade: Alta
  
  Descrição: |
    Denúncia anônima reportou arrendamento irregular de 500 hectares
    de terras públicas na Fazenda São José, Campo Grande/MS.
    
    Objetivo: Verificar titularidade, identificar partes envolvidas,
    avaliar impactos ambientais e legais.
    
    Documentos iniciais: Denúncia, coordenadas GPS, imagens de satélite.

RESPONSÁVEIS:
  Principal: João Silva (Investigador Sênior)
  Colaboradores:
    - Maria Santos (Analista Fundiária) - Edição
    - Dr. Pedro Costa (Advogado) - Visualização

DATAS:
  Início: 15/01/2024
  Conclusão Prevista: 15/03/2024 (60 dias)
  
  Marcos:
    - 25/01/2024: Vistoria in loco
    - 10/02/2024: Relatório preliminar
    - 01/03/2024: Parecer jurídico
    - 15/03/2024: Relatório final

DOCUMENTOS (7):
  📂 Denúncias
    └── denuncia_anonima_15012024.pdf
  📂 Documentação Legal
    ├── matricula_imovel_sp45678.pdf
    └── certidao_negativa_debitos.pdf
  📂 Geoespacial
    ├── coordenadas_gps.kml
    └── imagem_satelite_2024.jpg
  📂 Fotos
    ├── foto_entrada_fazenda.jpg
    └── foto_area_cultivada.jpg

TAGS:
  #arrendamento #terras-publicas #campo-grande-ms 
  #fundiario #alta-prioridade #judicial

CATEGORIA: Fundiário
CONFIDENCIALIDADE: Confidencial
```

---

## 🔍 Troubleshooting (Resolução de Problemas)

### Problema 1: Não Consigo Salvar a Investigação

**Possíveis Causas:**
- Campos obrigatórios não preenchidos
- Título muito curto (mínimo: 10 caracteres)
- Descrição vazia

**Solução:**
1. Verifique campos marcados com asterisco (*)
2. Preencha título com pelo menos 10 caracteres
3. Adicione descrição com mínimo 50 caracteres

### Problema 2: Não Encontro Usuário para Atribuir

**Possíveis Causas:**
- Usuário não cadastrado no sistema
- Sem permissões de visualizar outros usuários

**Solução:**
1. Verifique se nome está correto
2. Solicite cadastro do usuário ao administrador
3. Use email completo na busca

### Problema 3: Arquivo Não Faz Upload

**Possíveis Causas:**
- Arquivo maior que 50 MB
- Formato não suportado
- Conexão instável

**Solução:**
1. Comprimir arquivo se possível
2. Converter para formato suportado
3. Tentar novamente ou usar conexão melhor

### Problema 4: Investigação Não Aparece na Lista

**Possíveis Causas:**
- Salva como rascunho
- Filtros ativos na lista
- Não tem permissão de visualização

**Solução:**
1. Verificar aba "Rascunhos"
2. Limpar filtros (botão "Limpar Filtros")
3. Contatar administrador para permissões

---

## 📚 Recursos Adicionais

### Documentação Relacionada

- 📖 [Tutorial 2: Entendendo o Dashboard](./02-dashboard.md)
- 📖 [Tutorial 3: Gerando Relatórios Profissionais](./03-relatorios.md)
- 📖 [Tutorial 4: Colaboração em Equipe](./04-colaboracao.md)
- 📖 [Guia de Referência Rápida](../guias/referencia-rapida.md)

### Casos de Uso

- 📋 [Caso 1: Investigação de Arrendamento Irregular](../casos-uso/01-arrendamento-irregular.md)
- 📋 [Caso 2: Due Diligence em Aquisição](../casos-uso/02-due-diligence.md)

### Vídeos

- 🎥 [Vídeo: Criando sua Primeira Investigação](https://youtube.com/agroadb/tutorial-1)
- 🎥 [Webinar: Melhores Práticas](https://youtube.com/agroadb/webinar-1)

---

## ❓ Precisa de Ajuda?

**Suporte Técnico:**
- 📧 Email: suporte@agroadb.com
- 💬 Chat: Segunda a Sexta, 9h-18h
- 📞 Telefone: (11) 3456-7890

**Comunidade:**
- 👥 Fórum: https://forum.agroadb.com
- 💡 Base de Conhecimento: https://help.agroadb.com

---

**Última atualização:** 05/02/2026  
**Versão:** 1.0  
**Autor:** Equipe AgroADB

---

🎉 **Parabéns!** Você completou o tutorial e está pronto para criar investigações profissionais no AgroADB!
