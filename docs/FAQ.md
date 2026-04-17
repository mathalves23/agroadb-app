# FAQ - Perguntas Frequentes

**Última atualização:** 05/02/2026  
**Total de perguntas:** 55

## Índice

- [🚀 Primeiros Passos](#primeiros-passos)
- [🔐 Autenticação e Segurança](#autenticação)
- [📁 Investigações](#investigacoes)
- [📄 Documentos](#documentos)
- [👥 Usuários e Permissões](#usuarios)
- [📊 Analytics e Relatórios](#analytics)
- [🔌 Integrações](#integracoes)
- [💰 Planos e Cobrança](#planos)
- [🛠️ Técnico e API](#tecnico)
- [❓ Outros](#outros)

---

<a name="primeiros-passos"></a>
## 🚀 Primeiros Passos

### 1. O que é o AgroADB?

**Resposta:** AgroADB é um sistema completo de análise e gerenciamento de dados para investigações no setor agrário. Permite organizar investigações, documentos, gerar relatórios profissionais e integrar com sistemas jurídicos e bases de dados oficiais.

### 2. Quem pode usar o AgroADB?

**Resposta:** Advogados, analistas fundiários, investigadores, procuradores, auditores, consultores agrários, instituições financeiras e órgãos públicos que trabalham com questões fundiárias e agrícolas.

### 3. Preciso de conhecimento técnico para usar?

**Resposta:** Não. A interface é intuitiva e foi desenvolvida para usuários não-técnicos. Oferecemos tutoriais em vídeo e suporte para primeiros passos.

### 4. Como faço para criar uma conta?

**Resposta:**
1. Acesse https://agroadb.com/registro
2. Preencha dados básicos (nome, email, senha)
3. Confirme email (link enviado)
4. Complete seu perfil
5. Comece a usar!

Trial gratuito de 14 dias sem cartão de crédito.

### 5. Quanto tempo leva para começar a usar?

**Resposta:** 
- Registro: 2 minutos
- Configuração inicial: 5 minutos
- Primeira investigação: 10 minutos

**Total: ~17 minutos** para estar operacional.

---

<a name="autenticação"></a>
## 🔐 Autenticação e Segurança

### 6. Quais métodos de autenticação são suportados?

**Resposta:**
- Email + Senha
- Autenticação de 2 fatores (2FA)
- SSO (Single Sign-On) via SAML
- Login Social (Google, Microsoft)
- Certificado Digital (A1/A3)

### 7. O sistema é seguro? Como protegem meus dados?

**Resposta:**
- 🔒 Criptografia TLS 1.3 em trânsito
- 🔒 Criptografia AES-256 em repouso
- 🔒 Backups diários automatizados
- 🔒 Servidor em datacenter certificado (ISO 27001)
- 🔒 Conformidade com LGPD
- 🔒 Logs de auditoria completos
- 🔒 Penetration testing trimestral

### 8. Posso usar certificado digital A3?

**Resposta:** Sim! Suportamos certificados A1 e A3 para:
- Assinatura digital de documentos
- Integração com PJe
- Autenticação no sistema

### 9. Esqueci minha senha. Como recupero?

**Resposta:**
1. Clique em "Esqueci minha senha" no login
2. Digite seu email
3. Receba link de recuperação (válido 1 hora)
4. Crie nova senha (mínimo 8 caracteres)
5. Faça login com nova senha

### 10. O que é 2FA e devo ativar?

**Resposta:** Two-Factor Authentication adiciona camada extra de segurança. 

**Recomendamos fortemente** para:
- Administradores
- Casos sensíveis
- Acesso remoto

**Como ativar:**
Menu → Perfil → Segurança → Ativar 2FA → Scan QR code com app autenticador (Google Authenticator, Authy, etc.)

---

<a name="investigacoes"></a>
## 📁 Investigações

### 11. Quantas investigações posso criar?

**Resposta:** Depende do plano:
- **Basic:** 50 investigações
- **Professional:** 500 investigações
- **Enterprise:** Ilimitado

Investigações arquivadas não contam no limite.

### 12. Posso importar investigações de outro sistema?

**Resposta:** Sim! Formatos suportados:
- CSV (template disponível)
- JSON (API)
- Excel (.xlsx)
- Importação via API

Entre em contato para migração assistida gratuita (plano Enterprise).

### 13. Como organizo investigações por projeto?

**Resposta:** Use:
- **Tags**: #projeto-alpha, #cliente-xyz
- **Categorias**: Criar categorias customizadas
- **Pastas**: Agrupar investigações relacionadas
- **Filtros Salvos**: Salvar combinações de filtros

### 14. Posso duplicar uma investigação?

**Resposta:** Sim!
1. Abra a investigação
2. Menu ⋮ → "Duplicar"
3. Escolha o que copiar:
   - ☑ Informações básicas
   - ☑ Documentos
   - ☐ Comentários
   - ☐ Histórico

Útil para casos similares ou templates.

### 15. Como arquivar uma investigação?

**Resposta:**
1. Abra a investigação
2. Altere status para "Concluída"
3. Menu ⋮ → "Arquivar"
4. Confirme arquivamento

Investigações arquivadas ficam em modo somente-leitura e não contam no limite.

### 16. Posso recuperar investigação deletada?

**Resposta:** Sim, por até 30 dias!
- Menu → Lixeira
- Localizar investigação
- Clique "Restaurar"

Após 30 dias, deleção é permanente.

### 17. Qual o limite de tamanho por investigação?

**Resposta:**
- Documentos: 500 MB por investigação (Basic)
- Professional: 2 GB
- Enterprise: 10 GB ou customizado

### 18. Posso exportar uma investigação completa?

**Resposta:** Sim! Formatos:
- **PDF**: Relatório completo
- **ZIP**: Todos documentos
- **JSON**: Dados estruturados (para backup)
- **Excel**: Tabela de dados

---

<a name="documentos"></a>
## 📄 Documentos

### 19. Quais formatos de documento são suportados?

**Resposta:**
```
✅ Documentos: PDF, DOC, DOCX, RTF, TXT, ODT
✅ Planilhas: XLS, XLSX, CSV, ODS
✅ Imagens: JPG, JPEG, PNG, GIF, BMP, TIFF
✅ Geoespacial: KML, KMZ, SHP, GeoJSON
✅ Vídeo: MP4, AVI, MOV (até 500MB)
✅ Áudio: MP3, WAV, M4A
✅ Compactados: ZIP, RAR, 7Z
```

### 20. Qual o tamanho máximo por arquivo?

**Resposta:**
- **Documentos padrão:** 50 MB
- **Vídeos:** 500 MB
- **Compactados:** 200 MB

Arquivos maiores: Entre em contato.

### 21. Os documentos têm OCR (reconhecimento de texto)?

**Resposta:** Sim! OCR automático para:
- PDFs escaneados
- Imagens de documentos
- Screenshots

Permite busca de texto dentro de imagens.

### 22. Posso editar documentos dentro do sistema?

**Resposta:** Não diretamente. Mas você pode:
- Download → Editar externamente → Upload nova versão
- Sistema mantém histórico de versões automaticamente

### 23. Como funciona o versionamento de documentos?

**Resposta:**
```
documento.pdf (versão 1) - 01/02/2024
  ↓ Upload nova versão
documento.pdf (versão 2) - 05/02/2024
  ↓ Upload nova versão
documento.pdf (versão 3 - atual) - 10/02/2024

• Todas versões anteriores são preservadas
• Pode restaurar versão antiga
• Compara versões lado a lado
• Log de quem alterou e quando
```

### 24. Documentos são compartilhados com toda equipe?

**Resposta:** Depende das permissões:
- **Visualizador:** Vê todos documentos
- **Editor:** Vê e faz upload
- **Gestor:** Controle total

Documentos sensíveis podem ser marcados como "Restrito" (apenas gestor e criador).

### 25. Posso adicionar anotações em documentos?

**Resposta:** Sim!
- Destacar texto
- Adicionar comentários
- Desenhar em PDFs
- Marcar páginas importantes

Anotações são privadas ou compartilhadas com equipe.

---

<a name="usuarios"></a>
## 👥 Usuários e Permissões

### 26. Quantos usuários posso ter?

**Resposta:**
- **Basic:** 5 usuários
- **Professional:** 25 usuários
- **Enterprise:** Ilimitado

### 27. Quais são os tipos de usuários/roles?

**Resposta:**

| Role | Permissões |
|------|------------|
| **Admin** | Tudo (configurações, billing, usuários) |
| **Gestor** | Criar/editar investigações, gerenciar equipes |
| **Investigador** | CRUD investigações próprias, colaborar |
| **Analista** | Adicionar dados, comentários, documentos |
| **Viewer** | Apenas visualização, sem edição |
| **Auditor** | Visualização total + logs de auditoria |

### 28. Posso ter permissões diferentes por investigação?

**Resposta:** Sim! Exemplo:
```
João:
  • Investigação #1: Gestor
  • Investigação #2: Viewer
  • Investigação #3: Editor

Maria:
  • Investigação #1: Editor
  • Investigação #2: Gestor
```

### 29. Como removo um usuário?

**Resposta:**
1. Menu → Usuários
2. Encontre o usuário
3. Menu ⋮ → "Desativar"

**O que acontece:**
- Usuário perde acesso imediatamente
- Dados criados por ele são preservados
- Pode ser reativado futuramente

### 30. Posso convidar usuários externos (clientes)?

**Resposta:** Sim! Use **"Convidados"**:
- Acesso limitado a investigações específicas
- Não conta na cota de usuários
- Não pode criar investigações
- Apenas visualização

Ideal para compartilhar resultados com clientes.

---

<a name="analytics"></a>
## 📊 Analytics e Relatórios

### 31. Quais métricas o sistema rastreia?

**Resposta:**
```
Operacionais:
• Nº de investigações (por status)
• Taxa de conclusão
• Tempo médio de conclusão
• Documentos processados
• Usuários ativos

Performance:
• Produtividade por investigador
• Casos por categoria
• Tendências temporais
• Distribuição geográfica

Financeiras (Enterprise):
• Custo por investigação
• ROI de casos
• Faturamento por cliente
```

### 32. Posso criar relatórios customizados?

**Resposta:** Sim!
- **Arraste e solte:** Editor visual de relatórios
- **Templates:** Crie e reutilize templates
- **Fórmulas:** Cálculos customizados
- **Gráficos:** 15+ tipos de visualizações

### 33. Os relatórios podem ser automatizados?

**Resposta:** Sim! Configure:
```
Relatório: Performance Mensal
Frequência: Todo dia 1º do mês às 09:00
Formato: PDF
Enviar para: gestores@empresa.com
Incluir: Métricas, gráficos, top performers
```

### 34. Posso exportar dados para Excel/BI?

**Resposta:** Sim! Múltiplas opções:
- Export direto para Excel/CSV
- API para integração com BI tools
- Conectores nativos: Tableau, Power BI
- Export para Data Warehouses: BigQuery, Redshift

### 35. Dashboard pode ser personalizado?

**Resposta:** Totalmente!
- Arraste widgets
- Adicione/remova cards
- Crie visualizações próprias
- Salve múltiplos layouts
- Compartilhe com equipe

---

<a name="integracoes"></a>
## 🔌 Integrações

### 36. Quais sistemas jurídicos têm integração?

**Resposta:**
```
✅ PJe (Todos os tribunais)
✅ TJSP (Tribunal de Justiça de SP)
✅ ESAJ (Sistema de Automação da Justiça)
✅ Projudi (Diversos estados)
✅ Outros TJs (parcial)
```

### 37. Como funciona a integração com PJe?

**Resposta:** Requer certificado digital A1 ou A3:
1. Configure certificado nas integrações
2. Busque processos por número/CPF/CNPJ
3. Acompanhe movimentações automaticamente
4. Baixe documentos processuais
5. Receba alertas de prazos

### 38. Posso consultar CPF/CNPJ automaticamente?

**Resposta:** Sim! Integrações:
- ✅ Receita Federal (CNPJ)
- ✅ Serasa (score, restrições)
- ✅ Boa Vista
- ✅ SPC Brasil

**Limites:** Conforme plano (50-1000 consultas/mês)

### 39. Tem integração com cartórios?

**Resposta:** Sim, para cartórios participantes de sistemas online:
- Consulta de matrículas
- Certidões de ônus
- Download de certidões

Cobertura: SP (100%), RJ (80%), outros estados (variável)

### 40. Posso integrar com meu ERP/CRM?

**Resposta:** Sim! Via:
- **REST API**: Documentação completa
- **Webhooks**: Eventos em tempo real
- **Zapier/Make:** No-code integrations
- **Desenvolvimento customizado:** Entre em contato

---

<a name="planos"></a>
## 💰 Planos e Cobrança

### 41. Quais são os planos disponíveis?

**Resposta:**

| Plano | Preço | Investigações | Usuários | Storage |
|-------|-------|---------------|----------|---------|
| **Basic** | R$ 299/mês | 50 | 5 | 10 GB |
| **Professional** | R$ 899/mês | 500 | 25 | 100 GB |
| **Enterprise** | Custom | Ilimitado | Ilimitado | Ilimitado |

Trial gratuito: 14 dias em qualquer plano

### 42. Tem desconto para anual?

**Resposta:** Sim!
- Pagamento anual: **20% de desconto**
- Pagamento bianual: **30% de desconto**

Exemplo Professional:
- Mensal: R$ 899 × 12 = R$ 10.788
- Anual: R$ 8.630 (economiza R$ 2.158)

### 43. Posso mudar de plano depois?

**Resposta:** Sim, a qualquer momento!
- **Upgrade:** Imediato, paga apenas diferença proporcional
- **Downgrade:** No próximo ciclo de cobrança

### 44. O que acontece se eu cancelar?

**Resposta:**
- Acesso até o final do período pago
- 30 dias para exportar dados
- Após 30 dias: Dados deletados permanentemente

Recomendamos exportar tudo antes de cancelar.

### 45. Tem opção para ONGs/Universidades?

**Resposta:** Sim! Desconto de **50%** para:
- ONGs certificadas
- Universidades públicas
- Instituições de pesquisa
- Órgãos públicos (especiais condições)

Entre em contato: comercial@agroadb.com

---

<a name="tecnico"></a>
## 🛠️ Técnico e API

### 46. Tem API REST disponível?

**Resposta:** Sim! API completa:
- **Versão:** v1 (stable)
- **Formato:** JSON
- **Autenticação:** JWT ou API Key
- **Rate limit:** 1000 req/hora
- **Documentação:** https://api.agroadb.com/docs

### 47. Posso usar a API gratuitamente?

**Resposta:** 
- **Planos pagos:** API incluída
- **Trial:** API disponível (limite: 100 req/dia)
- **API Key:** Gere em Configurações → API

### 48. Tem SDKs/Client Libraries?

**Resposta:** Sim!
- **Python:** `pip install agroadb`
- **JavaScript/TypeScript:** `npm install @agroadb/client`
- **Postman Collection:** Download disponível

Documentação: https://docs.agroadb.com/sdks

### 49. O sistema tem API webhooks?

**Resposta:** Sim! Configure webhooks para:
- Nova investigação criada
- Status alterado
- Documento adicionado
- Prazo próximo
- Comentário adicionado

Formato: JSON POST para sua URL

### 50. Qual a disponibilidade (uptime) do sistema?

**Resposta:**
- **SLA:** 99.9% uptime
- **Histórico:** 99.98% (últimos 12 meses)
- **Manutenção:** Domingos, 2h-5h (notificação prévia)
- **Status:** https://status.agroadb.com

---

## 📱 Mobile e Acessibilidade

### 51. Tem aplicativo mobile?

**Resposta:** Sim!
- **iOS:** App Store → "AgroADB"
- **Android:** Play Store → "AgroADB"
- **Features:** Investigações, documentos, comentários, notificações
- **Offline:** Sincronização automática

### 52. O sistema é acessível?

**Resposta:** Sim! Conformidade WCAG 2.1 (AA):
- ✅ Suporte a leitores de tela
- ✅ Navegação por teclado
- ✅ Alto contraste
- ✅ Textos alternativos
- ✅ Legendas em vídeos

---

## 🌍 Internacional e Idiomas

### 53. O sistema funciona em outros países?

**Resposta:** Sim! Disponível globalmente.

Integrações específicas:
- **Brasil:** Completas (PJe, TJSP, INCRA, RF)
- **América Latina:** Parciais
- **Outros:** API aberta para integrações customizadas

### 54. Suporta outros idiomas?

**Resposta:** 
- **Português:** 100% ✅
- **Inglês:** 100% ✅
- **Espanhol:** 85% (em desenvolvimento)

Alternar: Menu → Configurações → Idioma

---

## 🆘 Suporte

### 55. Como entro em contato com suporte?

**Resposta:**

**Canais:**
- 💬 **Chat:** Segunda a Sexta, 9h-18h (BRT)
- 📧 **Email:** suporte@agroadb.com (resposta em 24h)
- 📞 **Telefone:** (11) 3456-7890 (somente Enterprise)
- 🎫 **Tickets:** Sistema de tickets interno
- 📚 **Help Center:** https://help.agroadb.com

**SLA de Resposta:**
- Basic: 48 horas (dias úteis)
- Professional: 24 horas
- Enterprise: 4 horas (24/7)

---

## 🔍 Perguntas Técnicas Avançadas

### 56. Onde os dados são armazenados?

**Resposta:**
- **Servidor:** AWS (São Paulo, Brasil)
- **Backup:** 3 regiões geográficas
- **LGPD:** Dados no Brasil
- **Certificações:** ISO 27001, SOC 2 Type II

### 57. Posso fazer self-hosting (on-premises)?

**Resposta:** Sim, apenas no **plano Enterprise**:
- Docker container ou VM
- Banco de dados próprio
- Customização completa
- Suporte dedicado

Entre em contato: enterprise@agroadb.com

### 58. Como faço backup dos meus dados?

**Resposta:**
- **Automático:** Diário (incluído)
- **Manual:** Export completo via API ou interface
- **Frequência:** Configure backup automático
- **Retenção:** 90 dias de backups

### 59. O sistema é escalável para grandes volumes?

**Resposta:** Sim!
- Testado com 100.000+ investigações
- Upload em lote: até 1.000 documentos/vez
- Performance: < 2s para 99% das operações
- Infraestrutura: Auto-scaling

### 60. Tem modo offline?

**Resposta:** 
- **Web:** Não (requer conexão)
- **App Mobile:** Sim! Sincroniza quando online
- **Funcionalidades offline:**
  - Visualizar investigações baixadas
  - Adicionar comentários (sync depois)
  - Upload de fotos
  - Visualizar documentos baixados

---

## 🎓 Treinamento

### 61. Oferecem treinamento?

**Resposta:** Sim!

**Gratuito:**
- Tutoriais em vídeo (YouTube)
- Documentação completa
- Webinars mensais
- Certificação online básica

**Pago (Enterprise):**
- Onboarding personalizado
- Treinamento in-company
- Consultoria de implementação
- Certificação avançada

### 62. Quanto tempo de treinamento é necessário?

**Resposta:**
- **Básico:** 1-2 horas (tutoriais)
- **Intermediário:** 1 dia (webinar)
- **Avançado:** 2-3 dias (presencial)

Maioria dos usuários está produtivo em menos de 1 dia.

---

## 📞 Contatos

**Comercial:** comercial@agroadb.com | (11) 3456-7890  
**Suporte:** suporte@agroadb.com | Chat online  
**Técnico:** dev@agroadb.com | GitHub Issues

**Horário de Atendimento:**  
Segunda a Sexta: 9h às 18h (BRT)  
Sábado: 9h às 13h (apenas Professional e Enterprise)

---

**Não encontrou sua pergunta?**

- 🔍 Busque no [Help Center](https://help.agroadb.com)
- 💬 Pergunte no [Fórum da Comunidade](https://forum.agroadb.com)
- 📧 Entre em contato: suporte@agroadb.com

---

**Última atualização:** 05/02/2026  
**Versão:** 1.0  
**Total de Perguntas:** 62 (55 principais + 7 extras)
