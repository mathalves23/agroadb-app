# Tutorial 5: Integrações Jurídicas (PJe e Outros)

**Duração estimada:** 5-8 minutos  
**Nível:** Avançado  
**Objetivo:** Utilizar integrações com sistemas jurídicos e bases de dados oficiais

---

## ⚖️ Integrações Disponíveis

### 1. **PJe (Processo Judicial Eletrônico)**
- Consulta de processos
- Acompanhamento de movimentações
- Download de petições e decisões
- Alertas de prazos processuais

### 2. **TJSP (Tribunal de Justiça de São Paulo)**
- Busca de processos por CPF/CNPJ
- Consulta de distribuição
- Certidões online

### 3. **Cartórios e Registros**
- Consulta de matrículas de imóveis
- Certidões de ônus e gravames
- Registro de contratos

### 4. **Receita Federal**
- Consulta CNPJ
- Situação cadastral
- Vínculos societários

### 5. **INCRA**
- Certificação de imóveis rurais
- CCIR (Certificado de Cadastro de Imóvel Rural)
- SNCR (Sistema Nacional de Cadastro Rural)

### 6. **Bureaus de Crédito**
- Serasa
- Boa Vista
- SPC Brasil

---

## 🔌 Configuração Inicial

### Passo 1: Acessar Integrações

```
Menu → Configurações → Integrações
```

### Passo 2: Ativar Integração PJe

```
┌──────────────────────────────────────────────┐
│ ⚖️  PJe - Processo Judicial Eletrônico      │
├──────────────────────────────────────────────┤
│                                              │
│ Status: ● Inativo                           │
│                                              │
│ [Ativar Integração]                         │
│                                              │
│ Credenciais Necessárias:                    │
│   • Certificado Digital A1 ou A3            │
│   • Login institucional                     │
│   • Senha PJe                               │
│                                              │
│ Tribunais Suportados:                       │
│   ✅ TRF1, TRF2, TRF3, TRF4, TRF5          │
│   ✅ TST, TRT (todas regiões)              │
│   ✅ TSE, TRE (todos estados)              │
│                                              │
└──────────────────────────────────────────────┘
```

### Passo 3: Configurar Certificado Digital

**Tipos Suportados:**
- **A1**: Armazenado no computador (arquivo .pfx)
- **A3**: Cartão ou token USB

**Upload Certificado A1:**
```
1. Clique em "Upload Certificado"
2. Selecione arquivo .pfx
3. Digite senha do certificado
4. Clique "Validar"

✅ Certificado validado com sucesso!
   Titular: JOÃO SILVA
   CPF: 123.456.789-00
   Validade: até 05/02/2025
```

**Configurar Token A3:**
```
1. Conecte o token USB
2. Instale driver (se necessário)
3. Clique "Detectar Token"
4. Digite PIN do token
5. Clique "Validar"

✅ Token detectado!
   Marca: SafeNet
   Certificado: MARIA SANTOS
   Validade: até 15/06/2025
```

---

## 🔍 Consulta PJe

### Buscar Processo

**Por Número:**
```
┌──────────────────────────────────────────────┐
│ 🔍 Buscar Processo PJe                       │
├──────────────────────────────────────────────┤
│                                              │
│ Número do Processo:                         │
│ [0001234-56.2024.4.03.6100____________]     │
│                                              │
│ Tribunal: [TRF3 ▼]                          │
│                                              │
│ [Buscar]                                    │
└──────────────────────────────────────────────┘
```

**Por CPF/CNPJ:**
```
CPF/CNPJ: [123.456.789-00_______]

Filtros:
  Tribunal: [Todos ▼]
  Ano: [2024 ▼]
  Tipo: [Todos ▼]
  Status: [Ativos ▼]

[Buscar]
```

### Resultado da Busca

```
┌──────────────────────────────────────────────────────────┐
│ 📑 Processos Encontrados: 3                               │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ 📄 0001234-56.2024.4.03.6100                             │
│    TRF3 - 6ª Vara Federal de São Paulo                  │
│    Autor: JOÃO SILVA                                     │
│    Réu: FAZENDA NACIONAL                                 │
│    Assunto: Desapropriação para reforma agrária         │
│    Status: ⚖️ Em andamento                              │
│    Última movimentação: 03/02/2024                      │
│                                                           │
│    [Ver Detalhes] [Acompanhar] [Adicionar à Investig.]│
│                                                           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ 📄 0005678-90.2023.4.03.6100                             │
│    TRF3 - 12ª Vara Federal de São Paulo                 │
│    Status: ✅ Sentenciado                               │
│    [Ver Detalhes]                                        │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Adicionar Processo à Investigação

```
1. Clique "Adicionar à Investigação"
2. Selecione investigação de destino
3. O processo será vinculado automaticamente

✅ Processo vinculado com sucesso!

Recursos disponíveis:
  • Acompanhamento automático
  • Alertas de movimentações
  • Download de documentos
  • Linha do tempo integrada
```

---

## 📊 Dashboard de Processos

```
┌──────────────────────────────────────────────────────────┐
│ ⚖️  Processos Acompanhados (Investigação #1234)          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│ Processo Principal: 0001234-56.2024.4.03.6100            │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Timeline de Movimentações                           │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │                                                     │ │
│ │ 📅 03/02/2024 - Juntada de Petição                │ │
│ │    Petição nº 45678                                │ │
│ │    [📄 Baixar PDF]                                 │ │
│ │                                                     │ │
│ │ 📅 30/01/2024 - Despacho                           │ │
│ │    "Cite-se o réu..."                              │ │
│ │    [📄 Baixar PDF]                                 │ │
│ │                                                     │ │
│ │ 📅 25/01/2024 - Distribuição                       │ │
│ │    6ª Vara Federal - SP                            │ │
│ │                                                     │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                           │
│ Alertas Ativos:                                          │
│   ⚠️  Prazo para manifestação: 5 dias                   │
│   🔔 Aguardando juntada de documentos                   │
│                                                           │
│ Documentos Baixados (12):                                │
│   📄 peticao_inicial.pdf (450 KB)                       │
│   📄 procuracao.pdf (120 KB)                            │
│   📄 despacho_cite_se.pdf (85 KB)                       │
│   [Ver Todos]                                            │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 🏛️ Outras Integrações Jurídicas

### TJSP - Tribunal de Justiça de SP

```
┌──────────────────────────────────────────────┐
│ Consulta TJSP                                │
├──────────────────────────────────────────────┤
│                                              │
│ Tipo de Consulta:                           │
│   ● Processo (número)                       │
│   ○ CPF/CNPJ (nome da parte)               │
│   ○ OAB (advogado)                         │
│                                              │
│ Dados:                                       │
│ [____________________________________]       │
│                                              │
│ [Consultar]                                 │
└──────────────────────────────────────────────┘
```

### Cartórios Online

**Consulta de Matrícula:**
```
Estado: [São Paulo ▼]
Comarca: [São Paulo ▼]
CRI: [1º Cartório ▼]

Matrícula: [45678__________]

[Consultar]

Resultado:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MATRÍCULA Nº 45.678 - 1º CRI - SP

Imóvel: Fazenda São José
Área: 500 hectares
Localização: Campo Grande/MS

Proprietário:
  JOÃO DA SILVA
  CPF: 123.456.789-00

Ônus e Gravames:
  • Hipoteca (R$ 500.000,00) - Banco XYZ
  • Penhora (Proc. 1234-56.2023)

Última Atualização: 15/01/2024

[Baixar Certidão Completa (PDF)]
[Adicionar à Investigação]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🏢 Integrações Empresariais

### Receita Federal - Consulta CNPJ

```
CNPJ: [12.345.678/0001-90______]

[Consultar]

┌──────────────────────────────────────────────┐
│ 📊 Dados Cadastrais                          │
├──────────────────────────────────────────────┤
│                                              │
│ Razão Social:                                │
│   AGROPECUÁRIA SÃO JOSÉ LTDA                │
│                                              │
│ Nome Fantasia: Fazenda São José             │
│                                              │
│ CNPJ: 12.345.678/0001-90                    │
│ Situação: ✅ ATIVA                          │
│ Data Abertura: 10/03/2015                   │
│                                              │
│ Atividade Principal:                         │
│   01.21-1-01 - Cultivo de café              │
│                                              │
│ Capital Social: R$ 1.000.000,00             │
│                                              │
│ Sócios:                                      │
│   • JOÃO DA SILVA (80%)                     │
│     CPF: 123.456.789-00                     │
│   • MARIA DA SILVA (20%)                    │
│     CPF: 987.654.321-00                     │
│                                              │
│ [Baixar Comprovante]                        │
│ [Adicionar à Investigação]                  │
└──────────────────────────────────────────────┘
```

### Mapa de Vínculos Societários

```
     ┌─────────────────────┐
     │ JOÃO DA SILVA       │
     │ CPF: 123.456.789-00 │
     └──────────┬──────────┘
                │
      ┌─────────┴─────────┐
      │                   │
┌─────▼─────┐       ┌────▼──────┐
│ Empresa A │       │ Empresa B │
│ 80% sócio │       │ 50% sócio │
└───────────┘       └───────────┘

[Exportar Diagrama]
[Ver Detalhes Completos]
```

---

## 🌾 INCRA - Sistema Fundiário

### CCIR - Certificado de Cadastro

```
Código do Imóvel: [123.456.789.012-3____]

[Consultar CCIR]

┌──────────────────────────────────────────────┐
│ 🌾 CCIR - Certificado Válido                │
├──────────────────────────────────────────────┤
│                                              │
│ Código INCRA: 123.456.789.012-3             │
│ Validade: até 31/12/2024                    │
│                                              │
│ Imóvel: FAZENDA SÃO JOSÉ                    │
│ Área Total: 500,00 hectares                 │
│ Módulos Fiscais: 10 MF                      │
│                                              │
│ Classificação: Média Propriedade            │
│                                              │
│ ITR 2023: ✅ Pago                           │
│ Valor: R$ 12.500,00                         │
│                                              │
│ Situação: ✅ Regular                        │
│                                              │
│ [Baixar CCIR (PDF)]                         │
│ [Consultar ITR]                             │
└──────────────────────────────────────────────┘
```

---

## 💳 Bureaus de Crédito

### Serasa - Consulta de Restrições

```
⚠️ ATENÇÃO: Consulta sensível
   Requer autorização específica

CPF/CNPJ: [________________]
Investigação: #1234

Motivo da Consulta:
[Due diligence em aquisição______]

[✓] Li e aceito os termos de uso

[Consultar Serasa]

┌──────────────────────────────────────────────┐
│ 📊 Resumo de Restrições                      │
├──────────────────────────────────────────────┤
│                                              │
│ JOÃO DA SILVA - CPF 123.456.789-00          │
│                                              │
│ Score: 450 (Baixo)                          │
│                                              │
│ Pendências Financeiras:                      │
│   🔴 3 protestos (R$ 85.000,00)             │
│   🔴 2 ações judiciais                      │
│   🟡 1 cheque sem fundo                     │
│                                              │
│ Dívidas Ativas:                              │
│   Total: R$ 125.000,00                      │
│   Vencidas há mais de 90 dias               │
│                                              │
│ ⚠️  Risco: ALTO                             │
│                                              │
│ [Relatório Completo (PDF)]                  │
└──────────────────────────────────────────────┘
```

---

## 🔔 Alertas e Monitoramento

### Configurar Alertas Automáticos

```
┌──────────────────────────────────────────────┐
│ Monitoramento de Processos                  │
├──────────────────────────────────────────────┤
│                                              │
│ Processo: 0001234-56.2024.4.03.6100         │
│                                              │
│ Alertar quando:                              │
│   ✅ Nova movimentação                      │
│   ✅ Prazo próximo (3 dias antes)           │
│   ✅ Sentença publicada                     │
│   ✅ Recurso interposto                     │
│   ☐ Qualquer juntada                        │
│                                              │
│ Notificar:                                   │
│   ✅ Email                                   │
│   ✅ Push (app)                             │
│   ☐ SMS                                      │
│   ☐ Webhook                                  │
│                                              │
│ Destinatários:                               │
│   • joao@empresa.com                        │
│   • maria@empresa.com                       │
│   [+ Adicionar]                             │
│                                              │
│ [Salvar Configuração]                       │
└──────────────────────────────────────────────┘
```

---

## 📥 Download em Lote

### Baixar Todos Documentos do Processo

```
Processo: 0001234-56.2024.4.03.6100

Documentos Disponíveis: 45

┌──────────────────────────────────────────────┐
│ Selecionar para Download:                    │
├──────────────────────────────────────────────┤
│                                              │
│ ☑ Petição Inicial                           │
│ ☑ Documentos da Inicial (15)                │
│ ☑ Despachos (8)                             │
│ ☑ Decisões (3)                              │
│ ☑ Contestação                                │
│ ☑ Documentos da Contestação (12)            │
│ ☐ Manifestações (5)                         │
│                                              │
│ [✓ Selecionar Todos]                        │
│                                              │
│ Formato:                                     │
│   ● PDF individual (ZIP)                    │
│   ○ PDF único (mesclado)                    │
│                                              │
│ [Baixar Selecionados (42 documentos)]       │
└──────────────────────────────────────────────┘

Progresso:
▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░ 70% (30 de 42)

Baixados automaticamente para:
📁 Investigação #1234 → Documentos → PJe → Processo_0001234
```

---

## 💡 Dicas Avançadas

### 1. Automações

**Criar Regra:**
```yaml
SE novo processo distribuído
   CPF/CNPJ monitorado: 123.456.789-00
ENTÃO
   • Criar investigação automática
   • Notificar equipe jurídica
   • Baixar petição inicial
   • Adicionar tag #automatico
```

### 2. Webhooks

**Integração com Outros Sistemas:**
```
URL Webhook: https://seusite.com/webhook/agroadb

Eventos:
  ✅ Nova movimentação processual
  ✅ Documento disponível
  ✅ Prazo próximo

Formato: JSON
Autenticação: Bearer Token
```

### 3. API Personalizada

```python
# Exemplo de uso da API
from agroadb import AgroADBClient

client = AgroADBClient(api_key="sua_chave")

# Consultar processo
processo = client.pje.get_processo("0001234-56.2024.4.03.6100")

# Monitorar
client.pje.monitor(processo.id, alert_emails=["joao@email.com"])

# Baixar documentos
docs = client.pje.download_docs(processo.id, save_to="./docs/")
```

---

## ⚠️ Avisos Importantes

### Uso Responsável

```
⚠️  ATENÇÃO:

1. Consultas a bases de dados oficiais devem respeitar
   a LGPD e regulamentações específicas

2. Mantenha sigilo das informações obtidas

3. Use apenas para fins legítimos e autorizados

4. Documente a finalidade de cada consulta

5. Não compartilhe credenciais de acesso
```

### Limites de Consulta

```
Plano Atual: Professional

Limites Mensais:
  • PJe: 500 consultas
  • TJSP: 300 consultas
  • Receita Federal: 1.000 consultas
  • Serasa: 50 consultas
  • INCRA: Ilimitado

Uso Atual (Fevereiro):
  PJe: █████░░░░░ 45%  (225/500)
  TJSP: ████░░░░░ 30%  (90/300)
  Receita: ██░░░░░ 15% (150/1000)
```

---

## 📚 Recursos Adicionais

- [Guia de Certificação Digital](../guias/certificado-digital.md)
- [LGPD e Consultas](../guias/lgpd-consultas.md)
- [API Reference](../api/integrações.md)

---

**Última atualização:** 05/02/2026  
**Versão:** 1.0
