# 🚀 Guia de Instalação e Teste - UIs de Colaboração

## 📦 Passo 1: Instalar Dependências

### Frontend
```bash
cd frontend
npm install
```

Isso instalará automaticamente a nova dependência `react-markdown` adicionada ao `package.json`.

---

## ▶️ Passo 2: Iniciar os Serviços

### Backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

O backend estará disponível em: `http://localhost:8000`

### Frontend
```bash
cd frontend
npm run dev
```

O frontend estará disponível em: `http://localhost:5173`

---

## 🧪 Passo 3: Testar as Funcionalidades

### 3.1 Acessar a Aba Colaboração

1. Faça login no sistema
2. Acesse qualquer investigação existente
3. Você verá as abas: `[Resumo] [Consultas Legais] [Rede] [Análise ML] [Colaboração]`
4. Clique na aba **"Colaboração"** (ícone de usuários 👥)

### 3.2 Testar Compartilhamento

#### Compartilhar uma Investigação:
1. Na aba Colaboração, clique no botão **"Compartilhar"** (canto superior direito)
2. No modal que abrir:
   - Digite o email de um usuário existente
   - Selecione o nível de permissão (VIEW, COMMENT, EDIT ou ADMIN)
   - Clique em **"Compartilhar"**
3. ✅ Você verá uma mensagem de sucesso
4. O usuário aparecerá na lista com:
   - Avatar colorido com iniciais
   - Badge colorido da permissão
   - Botão de revogar (aparece ao passar o mouse)

#### Buscar Usuários:
1. Se houver vários usuários compartilhados, use o campo **"Buscar pessoas..."**
2. Digite nome ou email
3. A lista será filtrada em tempo real

#### Revogar Acesso:
1. Passe o mouse sobre um usuário compartilhado
2. Clique no ícone de lixeira 🗑️
3. Confirme a ação
4. O usuário será removido da lista

### 3.3 Testar Comentários

#### Adicionar Comentário Normal:
1. Na seção de comentários, digite um texto no campo
2. Teste Markdown:
   - `**texto em negrito**`
   - `*texto em itálico*`
   - `[meu link](https://exemplo.com)`
3. Clique em **"Enviar"**
4. O comentário aparecerá:
   - À **direita** com fundo **azul** (seus comentários)
   - Com seu avatar colorido
   - Com timestamp relativo ("há X minutos")

#### Adicionar Comentário Privado:
1. Marque a checkbox **"Anotação privada"** antes de enviar
2. Digite o comentário
3. Clique em **"Enviar"**
4. O comentário aparecerá com:
   - Fundo **amarelo**
   - Badge **"🔒 Privado"**
   - Apenas você pode vê-lo

#### Editar Comentário:
1. Passe o mouse sobre um comentário seu
2. Clique no ícone de editar ✏️
3. Altere o texto
4. Clique em **"Salvar"** ou **"Cancelar"**
5. Se salvar, aparecerá marcação **(editado)**

#### Deletar Comentário:
1. Passe o mouse sobre um comentário seu
2. Clique no ícone de deletar 🗑️
3. Confirme a ação
4. O comentário será marcado como deletado

#### Ver Comentários de Outros:
1. Comentários de outros usuários aparecerão:
   - À **esquerda** com fundo **cinza**
   - Com avatares coloridos diferentes
   - Sem botões de editar/deletar (não são seus)

### 3.4 Testar Histórico de Alterações

#### Ver Timeline:
1. Role até a seção de Histórico
2. Você verá uma timeline vertical com:
   - Linha conectora gradiente (azul → roxo → cinza)
   - Cards de alteração com sombra
   - Ícones grandes e coloridos

#### Filtrar por Tipo:
1. Use o dropdown no canto superior direito
2. Selecione um tipo:
   - **Todas as ações**
   - **Criações** (verde)
   - **Atualizações** (azul)
   - **Compartilhamentos** (roxo)
   - **Comentários** (ciano)
   - **Exclusões** (vermelho)
3. A timeline será filtrada

#### Ver Diffs Visuais:
1. Encontre uma alteração que mudou um campo
2. Você verá o diff:
   ```
   Campo alterado: status
   - 🔴 Valor Antigo
   + 🟢 Valor Novo
   ```

#### Ver Badge "Recente":
1. A alteração mais nova terá:
   - Badge verde **"RECENTE"**
   - Animação de pulse no ícone

---

## 🎯 Checklist de Testes

### ShareModal ✅
- [ ] Abrir modal clicando em "Compartilhar"
- [ ] Compartilhar com email válido
- [ ] Ver lista de usuários com avatares
- [ ] Ver badges coloridos de permissão
- [ ] Buscar usuários no campo de busca
- [ ] Revogar acesso de um usuário
- [ ] Ver mensagens de sucesso/erro
- [ ] Testar todos os níveis de permissão (VIEW, COMMENT, EDIT, ADMIN)

### CommentThread ✅
- [ ] Adicionar comentário normal
- [ ] Adicionar comentário com Markdown (**negrito**, *itálico*, [link](url))
- [ ] Adicionar comentário privado
- [ ] Ver comentários próprios à direita (azul)
- [ ] Ver comentários de outros à esquerda (cinza)
- [ ] Editar próprio comentário
- [ ] Deletar próprio comentário
- [ ] Ver timestamps relativos
- [ ] Ver marcação "(editado)"

### ChangeLog ✅
- [ ] Ver timeline vertical conectada
- [ ] Ver ícones coloridos por tipo de ação
- [ ] Ver badge "RECENTE" no item mais novo
- [ ] Filtrar por tipo de ação
- [ ] Ver diffs visuais (verde/vermelho)
- [ ] Ver timestamps formatados e relativos
- [ ] Testar hover effect nos cards
- [ ] Ver avatares dos usuários que fizeram mudanças

### Integração ✅
- [ ] Ver aba "Colaboração" na navegação
- [ ] Ver header com gradiente e botão
- [ ] Ver 3 cards de estatísticas
- [ ] Todos os componentes carregando corretamente
- [ ] Modal abrindo ao clicar em "Compartilhar"

---

## 🐛 Resolução de Problemas

### Erro: "react-markdown not found"
```bash
cd frontend
npm install react-markdown@^9.0.1
```

### Erro: "Module not found: ShareModal"
Verifique se o arquivo existe em:
```
frontend/src/components/ShareModal.tsx
```

### Erro: "Cannot read property 'user_id' of null"
O sistema precisa de um usuário autenticado. Faça login primeiro.

### Comentários não aparecem
Verifique:
1. Backend está rodando?
2. Endpoint correto: `/api/v1/collaboration/investigations/{id}/comments`
3. Token JWT está válido?

### Avatares não têm cores
Verifique se a função `getAvatarColor` está implementada nos componentes.

### Markdown não renderiza
Verifique se `react-markdown` foi instalado:
```bash
npm list react-markdown
```

---

## 📊 Endpoints Testados

Durante os testes, os seguintes endpoints serão chamados:

### Compartilhamento:
- `GET /api/v1/collaboration/investigations/{id}/shares`
- `POST /api/v1/collaboration/investigations/{id}/share`
- `DELETE /api/v1/collaboration/investigations/{id}/shares/{user_id}`

### Comentários:
- `GET /api/v1/collaboration/investigations/{id}/comments`
- `POST /api/v1/collaboration/investigations/{id}/comments`
- `PUT /api/v1/collaboration/comments/{comment_id}`
- `DELETE /api/v1/collaboration/comments/{comment_id}`

### Histórico:
- `GET /api/v1/collaboration/investigations/{id}/changelog`

---

## ✅ Critérios de Aceitação

A implementação está completa quando:

1. ✅ Aba "Colaboração" aparece na navegação
2. ✅ Modal de compartilhamento abre e fecha corretamente
3. ✅ Usuários podem ser compartilhados com badges coloridos
4. ✅ Busca de usuários funciona
5. ✅ Acesso pode ser revogado
6. ✅ Comentários podem ser adicionados com Markdown
7. ✅ Layout chat funciona (autor à direita, outros à esquerda)
8. ✅ Comentários privados têm visual diferenciado
9. ✅ Comentários podem ser editados e deletados
10. ✅ Timeline de histórico é exibida com ícones e cores
11. ✅ Diffs visuais aparecem para mudanças
12. ✅ Filtros de histórico funcionam
13. ✅ Todos os timestamps são exibidos corretamente
14. ✅ Avatares coloridos aparecem em todos os componentes
15. ✅ Animações e hover effects funcionam

---

## 🎉 Resultado Esperado

Ao completar todos os testes, você deverá ter:

1. Uma aba "Colaboração" totalmente funcional
2. Sistema de compartilhamento moderno e intuitivo
3. Chat de comentários com suporte a Markdown
4. Timeline visual de histórico de alterações
5. Interface responsiva e visualmente atraente
6. Feedback visual claro para todas as ações

---

## 📞 Próximos Passos

Após testar e validar:

1. ✅ Fazer commit das alterações
2. ✅ Atualizar documentação se necessário
3. ✅ Treinar equipe nas novas funcionalidades
4. ✅ Monitorar uso e feedback dos usuários

---

**Status: PRONTO PARA TESTE** ✅

Execute `npm install` no frontend e comece os testes!
