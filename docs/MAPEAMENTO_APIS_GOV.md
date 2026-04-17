# Mapeamento de APIs Governamentais — AgroADB

Este documento mapeia as APIs relevantes para o AgroADB, prioriza integrações
e lista o checklist de credenciamento/acesso.

Fonte principal: Catálogo Conecta gov.br — https://www.gov.br/conecta/catalogo/

## Prioridade de Integrações (Top 8)

1. **SIGEF GEO** (INCRA)  
   - Uso: validação de imóveis rurais georreferenciados, perímetros e área.  
   - Valor: alta prioridade para investigações fundiárias.

2. **SNCR — Sistema Nacional de Cadastro Rural (INCRA)**  
   - Uso: CCIR, cadastro do imóvel rural, proprietários.  
   - Valor: essencial para comprovação de titularidade e cadastro rural.

3. **SICAR (CPF/CNPJ, Imóvel, Tema)**  
   - Uso: CAR por documento, imóvel e camadas temáticas.  
   - Valor: ambiental e regularidade de imóveis rurais.

4. **SIPRA — Beneficiários da Reforma Agrária**  
   - Uso: vínculos com assentamentos e programas agrários.  
   - Valor: contexto fundiário e histórico.

5. **DataJud (CNJ)**  
   - Uso: metadados de processos públicos.  
   - Valor: risco jurídico e histórico processual.

6. **Consulta CNPJ (Receita)**  
   - Uso: dados cadastrais, situação cadastral, quadro societário.  
   - Valor: validação de empresas ligadas ao alvo.

7. **CTCA — Controle de Tensões e Conflitos Agrários**  
   - Uso: conflitos agrários e situações críticas em área rural.  
   - Valor: análise de risco.

8. **CAF / DAP / Pronaf**  
   - Uso: registros rurais e agricultura familiar.  
   - Valor: perfil socioeconômico do produtor.

## Integrações já existentes no backend

- **CAR (por estado)**: `POST /api/v1/integrations/car/query`  
- **Tribunais**: `POST /api/v1/integrations/tribunais/query`  
- **Órgãos federais (IBAMA, ICMBio, CVM)**  
- **Bureaus (Serasa, Boa Vista)**

## Novas integrações adicionadas

### DataJud (CNJ)
**Endpoint:** `POST /api/v1/legal/datajud/proxy`  
**Objetivo:** acessar a API Pública do DataJud via proxy autenticado.

**Base oficial:** `https://api-publica.datajud.cnj.jus.br`

Exemplo de payload:
```json
{
  "path": "/tribunais/TRT2/_search",
  "method": "POST",
  "payload": {
    "query": {
      "match": { "numeroProcesso": "0000000-00.0000.0.00.0000" }
    },
    "size": 10
  }
}
```

### Conecta gov.br (SNCR/SIGEF/SICAR)

**Fluxo de credenciamento Conecta**
1. Acesse o [Catálogo Conecta gov.br](https://www.gov.br/conecta/catalogo/) e solicite acesso aos serviços desejados (SNCR, SIGEF, SICAR).
2. Após aprovação, você receberá **client_id** e **client_secret** (OAuth2) e/ou **api_key** (acesso direto).
3. Configure as variáveis no `.env` do backend (veja seção abaixo).
4. Reinicie o backend. O status das integrações pode ser consultado em `GET /api/v1/integrations/status`.
5. Se as credenciais não estiverem configuradas, os endpoints retornarão **503** com `credentials_missing: true` e mensagem clara para configuração.

**Resposta padronizada dos endpoints Conecta (SNCR/SIGEF/SICAR):**
- Sucesso: `{ "success": true, "items": [...], "data": {...}, "pagination": {}, "warnings": [] }`
- Credenciais ausentes: HTTP 503 com `{ "success": false, "detail": "...", "credentials_missing": true }`

**Endpoints (SNCR):**
- `POST /api/v1/integrations/conecta/sncr/imovel`
- `POST /api/v1/integrations/conecta/sncr/cpf-cnpj`
- `GET /api/v1/integrations/conecta/sncr/situacao/{codigo}`
- `GET /api/v1/integrations/conecta/sncr/ccir/{codigo}`

**Endpoints (SIGEF):**
- `POST /api/v1/integrations/conecta/sigef/imovel`
- `POST /api/v1/integrations/conecta/sigef/parcelas`

**Endpoints (SICAR):**
- `POST /api/v1/integrations/conecta/sicar/cpf-cnpj`
- `GET /api/v1/integrations/conecta/sicar/cpf-cnpj/{cpf_cnpj}`
- `POST /api/v1/integrations/conecta/sicar/imovel`

**Endpoints (SNCCI):**
- `POST /api/v1/integrations/conecta/sncci/parcelas`
- `POST /api/v1/integrations/conecta/sncci/creditos-ativos`
- `GET /api/v1/integrations/conecta/sncci/creditos/{codigo}`
- `POST /api/v1/integrations/conecta/sncci/boletos`

**Endpoints (SIGEF GEO):**
- `POST /api/v1/integrations/conecta/sigef-geo/parcelas`
- `POST /api/v1/integrations/conecta/sigef-geo/parcelas-geojson`

**Endpoints (Consulta CNPJ):**
- `POST /api/v1/integrations/conecta/cnpj/basica`
- `POST /api/v1/integrations/conecta/cnpj/qsa`
- `POST /api/v1/integrations/conecta/cnpj/empresa`

**Endpoints (Consulta CND):**
- `POST /api/v1/integrations/conecta/cnd/certidao`

**Endpoints (CADIN):**
- `POST /api/v1/integrations/conecta/cadin/info-cpf`
- `POST /api/v1/integrations/conecta/cadin/info-cnpj`
- `POST /api/v1/integrations/conecta/cadin/completa-cpf`
- `POST /api/v1/integrations/conecta/cadin/completa-cnpj`
- `GET /api/v1/integrations/conecta/cadin/versao`

**Endpoints (Portal de Serviços):**
- `GET /api/v1/integrations/portal-servicos/orgao/{codSiorg}`
- `GET /api/v1/integrations/portal-servicos/servicos/{servicoId}`
- `GET /api/v1/integrations/portal-servicos/servicos-simples/{servicoId}`
- `POST /api/v1/integrations/portal-servicos/servicos-auth`

**Endpoints (Serviços Estaduais):**
- `POST /api/v1/integrations/servicos-estaduais/auth`
- `POST /api/v1/integrations/servicos-estaduais/servicos`
- `PUT /api/v1/integrations/servicos-estaduais/servicos`
- `GET /api/v1/integrations/servicos-estaduais/servicos/{servicoId}?authorization=TOKEN`

**Objetivo:** usar o Conecta gov.br como camada oficial de integração para cadastros e dados fundiários.

### SIGEF Parcelas (WS externo)
**Endpoint:** `POST /api/v1/integrations/sigef/parcelas`  
**Objetivo:** consulta de parcelas via web service configurável (ex.: Infosimples).

Exemplo de payload:
```json
{
  "cpf": "123.456.789-00",
  "pagina": 1,
  "login_cpf": "000.000.000-00",
  "login_senha": "SUA_SENHA",
  "pkcs12_cert": "/caminho/cert.p12",
  "pkcs12_pass": "SENHA_CERT"
}
```

## Configurações no backend (.env)

### Variáveis de ambiente

```
DATAJUD_API_URL=https://api-publica.datajud.cnj.jus.br
DATAJUD_API_KEY=... (chave pública CNJ)

SIGEF_PARCELAS_API_URL=... (endpoint do WS/RPA)
SIGEF_PARCELAS_MAX_PAGES=5
SIGEF_LOGIN_CPF=
SIGEF_LOGIN_SENHA=
SIGEF_PKCS12_CERT=
SIGEF_PKCS12_PASS=

# Conecta gov.br — use OAuth2 (client_id + client_secret) ou APIKey
CONECTA_SNCR_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_SNCR_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_SNCR_CLIENT_ID=
CONECTA_SNCR_CLIENT_SECRET=
CONECTA_SNCR_API_KEY=
CONECTA_SNCR_IMOVEL_PATH=/api-sncr/v2/consultarImovelPorCodigo/{codigo}
CONECTA_SNCR_CPF_CNPJ_PATH=/api-sncr/v2/consultarImovelPorCpfCnpj/{cpf_cnpj}
CONECTA_SNCR_SITUACAO_PATH=/api-sncr/v2/verificarSituacaoImovel/{codigo}
CONECTA_SNCR_CCIR_PATH=/api-sncr/v2/baixarCcirPorCodigoImovel/{codigo}

CONECTA_SNCCI_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_SNCCI_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_SNCCI_CLIENT_ID=
CONECTA_SNCCI_CLIENT_SECRET=
CONECTA_SNCCI_API_KEY=
CONECTA_SNCCI_PARCELAS_PATH=/sncci/v1/parcelas
CONECTA_SNCCI_CREDITOS_ATIVOS_PATH=/sncci/v1/creditos-ativos
CONECTA_SNCCI_CREDITOS_PATH=/sncci/v1/creditos/{codigo}
CONECTA_SNCCI_BOLETOS_PATH=/sncci/v1/boletos

CONECTA_SIGEF_GEO_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_SIGEF_GEO_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_SIGEF_GEO_CLIENT_ID=
CONECTA_SIGEF_GEO_CLIENT_SECRET=
CONECTA_SIGEF_GEO_API_KEY=
CONECTA_SIGEF_GEO_PARCELAS_PATH=/api-sigef-geo/v1/parcelas
CONECTA_SIGEF_GEO_PARCELAS_GEOJSON_PATH=/api-sigef-geo/v1/parcelas/serpro

CONECTA_CNPJ_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_CNPJ_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_CNPJ_CLIENT_ID=
CONECTA_CNPJ_CLIENT_SECRET=
CONECTA_CNPJ_API_KEY=
CONECTA_CNPJ_BASICA_PATH=/api-cnpj-basica/v2/basica/{cnpj}
CONECTA_CNPJ_QSA_PATH=/api-cnpj-qsa/v2/qsa/{cnpj}
CONECTA_CNPJ_EMPRESA_PATH=/api-cnpj-empresa/v2/empresa/{cnpj}

CONECTA_CND_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_CND_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_CND_CLIENT_ID=
CONECTA_CND_CLIENT_SECRET=
CONECTA_CND_API_KEY=
CONECTA_CND_CERTIDAO_PATH=/api-cnd/v1/ConsultaCnd/certidao

CONECTA_CADIN_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_CADIN_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_CADIN_CLIENT_ID=
CONECTA_CADIN_CLIENT_SECRET=
CONECTA_CADIN_API_KEY=
CONECTA_CADIN_INFO_CPF_PATH=/registro/info/{cpf}/cpf
CONECTA_CADIN_INFO_CNPJ_PATH=/registro/info/{cnpj}/cnpj
CONECTA_CADIN_COMPLETA_CPF_PATH=/registro/consultaCompleta/{cpf}/cpf
CONECTA_CADIN_COMPLETA_CNPJ_PATH=/registro/consultaCompleta/{cnpj}/cnpj
CONECTA_CADIN_VERSAO_PATH=/registro/versaoApi

PORTAL_SERVICOS_API_URL=https://www.servicos.gov.br/api/v1
PORTAL_SERVICOS_AUTH_TOKEN=

SERVICOS_ESTADUAIS_API_URL=https://gov.br/apiestados
SERVICOS_ESTADUAIS_AUTH_TOKEN=

CONECTA_SIGEF_API_URL=
CONECTA_SIGEF_TOKEN_URL=
CONECTA_SIGEF_CLIENT_ID=
CONECTA_SIGEF_CLIENT_SECRET=
CONECTA_SIGEF_API_KEY=
CONECTA_SIGEF_IMOVEL_PATH=
CONECTA_SIGEF_PARCELAS_PATH=
CONECTA_SIGEF_SCOPES=

CONECTA_SICAR_API_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br
CONECTA_SICAR_TOKEN_URL=https://apigateway.conectagov.estaleiro.serpro.gov.br/oauth2/jwt-token
CONECTA_SICAR_CLIENT_ID=
CONECTA_SICAR_CLIENT_SECRET=
CONECTA_SICAR_API_KEY=
CONECTA_SICAR_CPF_CNPJ_PATH=/api-sicar-cpfcnpj/v1/{cpf_cnpj}
CONECTA_SICAR_IMOVEL_PATH=
```

## Checklist de Credenciamento / Acesso

### DataJud (CNJ)
- Solicitar acesso/uso conforme documentação do CNJ.  
- Usar header: `Authorization: APIKey <chave>`.

### SIGEF / SNCR / SIPRA (INCRA)
- Verificar se há acesso via Conecta gov.br.  
- Em geral, requer credenciamento institucional.  
- Avaliar uso de web service de terceiros (ex.: RPA/Infosimples) para consulta pública.

### SICAR (CPF/CNPJ, Imóvel, Tema)
- Verificar disponibilidade via Conecta e regras de uso.  
- Alguns serviços exigem credenciamento.

### Tribunais / PJe / ESAJ / Projudi
- Acesso geralmente exige credenciamento por tribunal.  
- Cada tribunal pode ter termos específicos.

### Receita CNPJ / Serasa / Boa Vista
- Chaves comerciais (contrato).  
- Deve haver base legal para consulta.

## Ativação após obtenção das credenciais Conecta

1. **Obter credenciais:** Solicite no catálogo Conecta gov.br (SNCR/SIGEF/SICAR). Você receberá client_id, client_secret e/ou api_key.
2. **Editar `.env`:** Preencha as variáveis `CONECTA_*_CLIENT_ID`, `CONECTA_*_CLIENT_SECRET` ou `CONECTA_*_API_KEY` para cada serviço que for usar.
3. **URLs e paths:** As URLs base e paths já possuem valores padrão para o gateway SERPRO; ajuste apenas se o contrato indicar outro endpoint.
4. **Reiniciar o backend:** Após salvar o `.env`, reinicie a aplicação.
5. **Validar:** Chame `GET /api/v1/integrations/status` ou use a aba "Consultas Legais" em uma investigação; se as credenciais estiverem corretas, as consultas deixarão de retornar 503 (credenciais ausentes).

## Exemplos de payload (Conecta)

**SNCR – imóvel por código:**
```json
POST /api/v1/integrations/conecta/sncr/imovel
{ "codigo_imovel": "12345678901234", "investigation_id": 1 }
```

**SNCR – por CPF/CNPJ:**
```json
POST /api/v1/integrations/conecta/sncr/cpf-cnpj
{ "cpf_cnpj": "12345678901", "investigation_id": 1 }
```

**SICAR – por CPF/CNPJ:**
```json
POST /api/v1/integrations/conecta/sicar/cpf-cnpj
{ "cpf_cnpj": "12345678901", "investigation_id": 1 }
```

**Resposta de sucesso (exemplo):**
```json
{
  "success": true,
  "items": [...],
  "data": { ... },
  "pagination": {},
  "warnings": []
}
```

**Resposta quando credenciais ausentes (503):**
```json
{
  "detail": {
    "success": false,
    "detail": "Credenciais Conecta SNCR não configuradas. Configure CONECTA_SNCR_* no .env.",
    "credentials_missing": true
  }
}
```

---

## NOVAS Integrações — APIs Públicas Gratuitas

### BrasilAPI (Gratuito, sem auth)
**URL:** `https://brasilapi.com.br/api`  
**Serviço:** `app/services/brasil_api.py`

Endpoints implementados:
- `POST /api/v1/integrations/brasil-api/cnpj` — CNPJ completo
- `POST /api/v1/integrations/brasil-api/cep` — CEP com geolocalização
- `GET /api/v1/integrations/brasil-api/bancos` — Lista de bancos
- `GET /api/v1/integrations/brasil-api/ddd/{ddd}` — Cidades por DDD
- `GET /api/v1/integrations/brasil-api/pix/participantes` — PIX
- `GET /api/v1/integrations/brasil-api/corretoras` — Corretoras CVM
- `GET /api/v1/integrations/brasil-api/municipios/{uf}` — Municípios

### Portal da Transparência — CGU (API Key gratuita)
**URL:** `https://api.portaldatransparencia.gov.br/api-de-dados`  
**Serviço:** `app/services/portal_transparencia.py`  
**Auth:** API Key gratuita. Registre-se em https://portaldatransparencia.gov.br/api-de-dados  
**Config:** `PORTAL_TRANSPARENCIA_API_KEY` no `.env`

Endpoints implementados:
- `POST /api/v1/integrations/transparencia/sancoes` — CEIS + CNEP (sanções)
- `POST /api/v1/integrations/transparencia/contratos` — Contratos federais
- `POST /api/v1/integrations/transparencia/servidores` — Servidores públicos
- `POST /api/v1/integrations/transparencia/beneficios` — Benefícios sociais
- `POST /api/v1/integrations/transparencia/despesas` — Despesas por favorecido
- `POST /api/v1/integrations/transparencia/completa` — Tudo de uma vez

### REDESIM / ReceitaWS (Gratuito, sem auth)
**URL:** `https://receitaws.com.br/v1/cnpj` + fallback `https://minhareceita.org`  
**Serviço:** `app/services/redesim_api.py`

Endpoints implementados:
- `POST /api/v1/integrations/redesim/cnpj` — CNPJ público (3 consultas/min grátis)

### IBGE — Serviço de Dados (Gratuito, sem auth)
**URL:** `https://servicodados.ibge.gov.br/api`  
**Serviço:** `app/services/ibge_api.py`

Endpoints implementados:
- `GET /api/v1/integrations/ibge/estados` — Listar estados
- `GET /api/v1/integrations/ibge/municipios/{uf}` — Municípios de UF
- `GET /api/v1/integrations/ibge/municipio/{codigo_ibge}` — Dados do município
- `GET /api/v1/integrations/ibge/nome/{nome}` — Frequência de nomes
- `GET /api/v1/integrations/ibge/malha/{codigo_ibge}` — Malha GeoJSON

### TSE — Tribunal Superior Eleitoral (Gratuito, sem auth)
**URL:** `https://dadosabertos.tse.jus.br/api/3`  
**Serviço:** `app/services/tse_api.py`

Endpoints implementados:
- `POST /api/v1/integrations/tse/buscar` — Buscar datasets eleitorais
- `GET /api/v1/integrations/tse/candidatos/{ano}` — Candidatos por ano
- `GET /api/v1/integrations/tse/bens/{ano}` — Bens declarados

### CVM — Comissão de Valores Mobiliários (Gratuito, sem auth)
**URL:** `https://dados.cvm.gov.br/api/3`  
**Serviço:** `app/services/cvm_api.py`

Endpoints implementados:
- `POST /api/v1/integrations/cvm/fundos` — Fundos de investimento
- `POST /api/v1/integrations/cvm/fii` — Fundos imobiliários (FII)
- `POST /api/v1/integrations/cvm/participantes` — Participantes do mercado

### BCB — Banco Central do Brasil (Gratuito, sem auth)
**URL:** `https://olinda.bcb.gov.br` + `https://api.bcb.gov.br`  
**Serviço:** `app/services/bcb_api.py`

Endpoints implementados:
- `GET /api/v1/integrations/bcb/selic` — Taxa SELIC
- `GET /api/v1/integrations/bcb/ipca` — IPCA (inflação)
- `GET /api/v1/integrations/bcb/cdi` — CDI
- `GET /api/v1/integrations/bcb/cambio/{moeda}` — Câmbio PTAX
- `GET /api/v1/integrations/bcb/pix/participantes` — PIX

### TJMG — Tribunal de Justiça de Minas Gerais (Gratuito, consulta pública)
**URL Consulta Pública:** `https://pje-consulta-publica.tjmg.jus.br`  
**URL Gestão de Acessos:** `https://gestao-acessos-api.tjmg.jus.br`  
**Serviço:** `app/services/tjmg_api.py`

Endpoints implementados:
- `POST /api/v1/integrations/tjmg/processos` — Consulta completa (CPF, CNPJ, nome, advogado, número)
- `POST /api/v1/integrations/tjmg/processos/cpf` — Processos por CPF
- `POST /api/v1/integrations/tjmg/processos/cnpj` — Processos por CNPJ
- `GET /api/v1/integrations/tjmg/processos/{numero}` — Processo por número
- `GET /api/v1/integrations/tjmg/configuration` — Configuração da API de Gestão

Dados consultados: assunto, classe judicial, data de distribuição, jurisdição, movimentos processuais, polo ativo/passivo (CPF/CNPJ, nome, OAB), órgão julgador, situação.

### Antecedentes Criminais / MG — Polícia Civil de Minas Gerais
**URL:** `https://www.policiacivil.mg.gov.br/pagina/emissao-atestado`  
**Serviço:** `app/services/antecedentes_mg.py`

Endpoints implementados:
- `POST /api/v1/integrations/antecedentes-mg/consultar` — Consultar antecedentes (CPF + RG emitido em MG)
- `GET /api/v1/integrations/antecedentes-mg/disponibilidade` — Verificar disponibilidade do portal

Dados consultados: conseguiu_emitir_certidao_negativa, numero, codigo.  
Uso: Due Diligence, dossiê KYC, verificação de pendências criminais em MG.

### SICAR Público — Cadastro Ambiental Rural (Gratuito, sem auth)
**URL:** `https://consultapublica.car.gov.br/publico`  
**Serviço:** `app/services/sicar_publico.py`

Endpoints implementados:
- `POST /api/v1/integrations/sicar-publico/imovel` — Consultar imóvel por número CAR
- `GET /api/v1/integrations/sicar-publico/municipio/{codigo_ibge}` — Imóveis por município
- `GET /api/v1/integrations/sicar-publico/disponibilidade` — Verificar disponibilidade

Dados consultados: area, car, coordenadas (polígono geográfico), municipio, status, tipo.  
Uso: validação de imóveis rurais, coordenadas geográficas, dossiê KYC de imóveis rurais.

### dados.gov.br — Portal de Dados Abertos (Gratuito)
**URL:** `https://dados.gov.br/dados/api/publico`  
**Serviço:** `app/services/dados_gov.py`

Endpoints implementados:
- `POST /api/v1/integrations/dados-gov/buscar` — Buscar datasets
- `GET /api/v1/integrations/dados-gov/rural` — Datasets rurais
- `GET /api/v1/integrations/dados-gov/ambiental` — Datasets ambientais
- `GET /api/v1/integrations/dados-gov/organizacoes` — Organizações

---

## Resumo de Todas as Bases

| # | Base | Auth | Gratuito | Tipo |
|---|------|:----:|:--------:|------|
| 1 | SNCR/INCRA | Conecta OAuth2 | Gov only | Cadastro Rural |
| 2 | SIGEF | Conecta OAuth2 | Gov only | Parcelas Georreferenciadas |
| 3 | SIGEF GEO | Conecta OAuth2 | Gov only | Dados Geoespaciais |
| 4 | SICAR | Conecta OAuth2 | Gov only | Cadastro Ambiental Rural |
| 5 | SNCCI | Conecta OAuth2 | Gov only | Crédito Instalação |
| 6 | CNPJ/RFB | Conecta OAuth2 | Gov only | Dados Empresariais |
| 7 | CND | Conecta OAuth2 | Gov only | Certidão de Débitos |
| 8 | CADIN | Conecta OAuth2 | Gov only | Restrições Cadastrais |
| 9 | DataJud/CNJ | API Key (pública) | Sim | Processos Judiciais |
| 10 | SIGEF Parcelas WS | Config | Pago | Parcelas INCRA (RPA) |
| 11 | Portal gov.br | Token | Parcial | Serviços Públicos |
| 12 | Serv. Estaduais | HTTP Basic | Gov only | Carta de Serviços |
| 13 | **BrasilAPI** | Nenhuma | **Sim** | CNPJ, CEP, Bancos, PIX |
| 14 | **Transparência/CGU** | API Key (grátis) | **Sim** | Sanções, Contratos, Servidores |
| 15 | **ReceitaWS** | Nenhuma | **Sim** | CNPJ público |
| 16 | **IBGE** | Nenhuma | **Sim** | Municípios, Nomes, Malhas |
| 17 | **TSE** | Nenhuma | **Sim** | Candidatos, Bens Declarados |
| 18 | **CVM** | Nenhuma | **Sim** | Fundos, FIIs, Corretoras |
| 19 | **BCB** | Nenhuma | **Sim** | SELIC, IPCA, CDI, Câmbio |
| 20 | **dados.gov.br** | Nenhuma | **Sim** | Datasets Abertos |
| 21 | **TJMG** | Nenhuma | **Sim** | Processos Judiciais MG |
| 22 | **Antecedentes/MG** | Nenhuma | **Sim** | Certidão Criminal MG |
| 23 | **SICAR/CAR** | Nenhuma | **Sim** | Imóvel Rural por CAR |
| — | CAR (por estado) | Config | Parcial | CAR estadual |
| — | Tribunais | Config | Parcial | ESAJ, Projudi, PJe |
| — | IBAMA/ICMBio/CVM | Config | Parcial | Órgãos Federais |
| — | Serasa/Boa Vista | Pago | Não | Bureaus de Crédito |

**Total: 23+ bases de dados integradas, sendo 11 totalmente gratuitas e sem autenticação.**

## Scrapers (complemento às APIs)

Além das APIs, o backend dispõe de **scrapers** que acessam páginas públicas e fontes abertas para enriquecer a base de dados quando as APIs não estão configuradas ou para obter dados adicionais:

| Fonte        | Scraper                | O que faz |
|-------------|------------------------|-----------|
| Tribunais   | `TribunaisScraper`     | Consulta pública ESAJ, Projudi e PJe (processos, partes, movimentações). |
| CAR/SICAR   | `CARPublicScraper`     | Demonstrativo e consulta pública CAR (servicos.car.gov.br, consultapublica.car.gov.br). |
| SNCR/CCIR   | `SNCRPublicScraper`    | Consulta CCIR e código do imóvel (sncr.serpro.gov.br). |
| SIGEF       | `SigefParcelasScraper` | Parcelas certificadas via ArcGIS REST (IBAMA, estados). |
| CNPJ        | `ReceitaScraper`       | Fallback HTML na Receita quando as APIs (BrasilAPI, ReceitaWS, etc.) falham. |

Os scrapers estão em `backend/app/scrapers/`. A lista `SCRAPERS_LEGAL_GOV` agrupa os que complementam as integrações legais/governamentais para uso em workers ou filas. Uso programático:

```python
from app.scrapers import TribunaisScraper, CARPublicScraper, SNCRPublicScraper, SigefParcelasScraper

# Exemplo: buscar processo nos tribunais
scraper = TribunaisScraper()
resultados = await scraper.search(process_number="0000000-00.0000.0.00.0000", state="SP")
```

---

## 22. Caixa — Regularidade do Empregador (FGTS / CRF)

| Item | Detalhe |
|------|---------|
| **Provedor** | Caixa Econômica Federal |
| **Portal** | https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf |
| **Autenticação** | Nenhuma (consulta pública) |
| **Gratuito** | Sim |

### Dados retornados

| Campo | Descrição |
|-------|-----------|
| `crf` | Número do Certificado de Regularidade do FGTS |
| `situacao` | REGULAR / IRREGULAR / NÃO ENCONTRADO |
| `razao_social` | Razão social da empresa |
| `inscricao` | CNPJ ou CEI consultado |
| `endereco` | Endereço do empregador |
| `validade_inicio_data` | Data de início da validade do CRF |
| `validade_fim_data` | Data de fim da validade do CRF |
| `datahora` | Data/hora da consulta |
| `historico_cabecalho` | Cabeçalho do histórico |
| `historico_lista` | Listagem de históricos |

### Endpoints AgroADB

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/integrations/caixa-fgts/consultar` | Consulta regularidade FGTS por CNPJ ou CEI |
| GET | `/api/v1/integrations/caixa-fgts/disponibilidade` | Verifica se o portal está acessível |

### Parâmetros de consulta

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `cnpj` | Sim (ou CEI) | CNPJ da empresa |
| `cei` | Sim (ou CNPJ) | CEI (Cadastro Específico do INSS) |
| `investigation_id` | Não | ID da investigação para auditoria |

### Uso no Quick Scan

A consulta FGTS é executada automaticamente no Quick Scan para investigações que possuem CNPJ.

---

---

## 23. BNMP — Banco Nacional de Mandados de Prisão (CNJ)

| Item | Detalhe |
|------|---------|
| **Provedor** | Conselho Nacional de Justiça (CNJ) |
| **Portal** | https://portalbnmp.pdpj.jus.br/#/pesquisa-peca |
| **Autenticação** | Nenhuma (consulta pública) |
| **Gratuito** | Sim |

### Dados retornados

| Campo | Descrição |
|-------|-----------|
| `nome` | Nome completo do procurado |
| `cpf` | CPF |
| `processo` | Número do processo |
| `tribunal` | Tribunal de origem |
| `orgao_judicial` | Órgão judiciário expedidor |
| `tipificacao_penal` | Tipificação penal (artigo + lei) |
| `especie_prisao` | Espécie de prisão |
| `regime` | Regime de cumprimento |
| `pena_ano` / `pena_mes` / `pena_dia` | Pena total |
| `situacao` | Situação do mandado (Aguardando Cumprimento) |
| `validade_data` | Data de validade |
| `expedicao_datahora` | Data/hora da expedição |
| `recaptura` | Indicador de recaptura |
| `sexo` / `nascimento_data` / `nacionalidade` / `naturalidade` | Dados pessoais |
| `mae` / `pai` | Filiação |
| `rg` / `rji` | Documentos |

### Endpoints AgroADB

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/integrations/bnmp/consultar` | Consulta mandados por CPF ou Nome |
| GET | `/api/v1/integrations/bnmp/disponibilidade` | Verifica se o portal BNMP está acessível |

### Parâmetros de consulta

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `cpf` | Sim (ou nome) | CPF do investigado |
| `nome` | Sim (ou CPF) | Nome completo |
| `nome_mae` | Não | Nome da mãe (refina busca por nome) |
| `investigation_id` | Não | ID da investigação para auditoria |

### Uso no Quick Scan

A consulta BNMP é executada automaticamente no Quick Scan — por CPF quando disponível, ou por nome do investigado.

---

---

## 24. SEEU — Sistema Eletrônico de Execução Unificado (CNJ)

| Item | Detalhe |
|------|---------|
| **Provedor** | Conselho Nacional de Justiça (CNJ) |
| **Portal** | https://seeu.pje.jus.br/seeu/processo/consultaPublica.do?actionType=iniciar |
| **Autenticação** | Nenhuma (consulta pública) |
| **Gratuito** | Sim |

### Dados retornados

| Campo | Descrição |
|-------|-----------|
| `processos_encontrados` | Lista de processos encontrados |
| `primeiro_processo` | Primeiro processo retornado (detalhado) |
| `informacoes_gerais` | Informações gerais do processo |
| `movimentacoes` | Lista de movimentações processuais |
| `partes` | Partes envolvidas no processo |
| `classe_processual` | Classe processual |
| `data_distribuicao` | Data de distribuição |
| `numero_processo` | Número unificado do processo |

### Endpoints AgroADB

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/integrations/seeu/consultar` | Consulta processos por CPF, CNPJ, nome ou nº processo |
| GET | `/api/v1/integrations/seeu/disponibilidade` | Verifica se o portal SEEU está acessível |

### Parâmetros de consulta

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `cpf` | Sim (ou outro) | CPF da parte |
| `cnpj` | Sim (ou outro) | CNPJ da parte |
| `nome_parte` | Sim (ou outro) | Nome da parte |
| `nome_mae` | Não | Nome da mãe (refina busca) |
| `numero_processo` | Sim (ou outro) | Número do processo |
| `investigation_id` | Não | ID da investigação para auditoria |

### Uso no Quick Scan

A consulta SEEU é executada automaticamente no Quick Scan — por CPF, CNPJ ou nome do investigado.

---

---

## 25. SIGEF Público — Parcelas INCRA (consulta direta)

| Item | Detalhe |
|------|---------|
| **Provedor** | INCRA (Instituto Nacional de Colonização e Reforma Agrária) |
| **Portal** | https://sigef.incra.gov.br/consultar/parcelas |
| **Autenticação** | Nenhuma (consulta pública) |
| **Gratuito** | Sim |
| **Paginação** | Até 5 páginas (acima o portal fica instável) |

### Dados retornados

| Campo | Descrição |
|-------|-----------|
| `parcelas` | Lista de parcelas encontradas |
| `codigo_parcela` | Código da parcela no SIGEF |
| `area_ha` | Área em hectares |
| `cns` | Código Nacional SNCR |
| `matricula` | Número da matrícula |
| `detentor` | Nome do detentor/proprietário |
| `nome` | Nome do imóvel |
| `paginas` | Total de páginas disponíveis |
| `paginas_retornadas` | Páginas efetivamente consultadas |
| `resultados` | Total de resultados |
| `resultados_retornados` | Resultados efetivamente retornados |

### Endpoints AgroADB

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/integrations/sigef-publico/parcelas` | Consulta parcelas por CPF, CNPJ ou código do imóvel |
| GET | `/api/v1/integrations/sigef-publico/disponibilidade` | Verifica se o portal está acessível |

### Parâmetros de consulta

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `cpf` | Sim (ou outro) | CPF do detentor |
| `cnpj` | Sim (ou outro) | CNPJ do detentor |
| `codigo_imovel` | Sim (ou outro) | Código do imóvel SIGEF |
| `paginas` | Não | Número máximo de páginas (padrão: 5) |
| `investigation_id` | Não | ID da investigação para auditoria |

### Diferença dos outros serviços SIGEF

| Serviço | Tipo | Requer credencial |
|---------|------|-------------------|
| `sigef_parcelas.py` | WS externo configurável | Sim (URL) |
| `conecta_sigef.py` | Via Conecta gov.br | Sim (OAuth) |
| **`sigef_publico.py`** | **Portal público direto** | **Não** |

### Uso no Quick Scan

A consulta SIGEF Público é executada automaticamente no Quick Scan para CPF ou CNPJ.

---

## 26. Receita Federal — Consulta CPF (Situação Cadastral)

| Campo | Valor |
|-------|-------|
| **Portal** | https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp |
| **Serviço** | `backend/app/services/receita_cpf.py` — `ReceitaCPFService` |
| **Autenticação** | Nenhuma (consulta pública) |
| **Gratuito** | Sim |

### Dados retornados

| Campo | Descrição |
|-------|-----------|
| `cpf` | CPF consultado |
| `nome` | Nome da Pessoa Física |
| `situacao_cadastral` | REGULAR, SUSPENSA, CANCELADA, etc. |
| `data_inscricao` | Data de inscrição no CPF |
| `data_nascimento` | Data de nascimento informada |
| `ano_obito` | Ano de óbito (se constar) |
| `digito_verificador` | Dígito verificador do CPF |

### Endpoints AgroADB

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/integrations/receita-cpf/consultar` | Consulta situação cadastral por CPF |
| GET | `/api/v1/integrations/receita-cpf/disponibilidade` | Verifica se o portal está acessível |

### Parâmetros de consulta

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `cpf` | Sim | CPF a consultar (11 dígitos) |
| `data_nascimento` | Não | Data de nascimento DD/MM/AAAA |
| `investigation_id` | Não | ID da investigação para auditoria |

### Uso no Quick Scan

A consulta Receita Federal CPF é executada automaticamente no Quick Scan para investigações com CPF.

---

## 27. Receita Federal — Consulta CNPJ (Dados Cadastrais PJ)

| Campo | Valor |
|-------|-------|
| **Portal** | https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva/Cnpjreva_Solicitacao.asp |
| **Serviço** | `backend/app/services/receita_cnpj.py` — `ReceitaCNPJService` |
| **Autenticação** | Nenhuma (consulta pública) |
| **Gratuito** | Sim |
| **Fallbacks** | BrasilAPI → ReceitaWS → MinhaReceita |

### Dados retornados

| Campo | Descrição |
|-------|-----------|
| `cnpj` | CNPJ consultado |
| `razao_social` | Razão social / nome empresarial |
| `nome_fantasia` | Nome fantasia |
| `situacao_cadastral` | ATIVA, SUSPENSA, INAPTA, BAIXADA, etc. |
| `situacao_cadastral_data` | Data da situação cadastral |
| `abertura_data` | Data de abertura |
| `natureza_juridica` | Natureza jurídica |
| `porte` | MEI, ME, EPP, demais |
| `capital_social` | Capital social |
| `atividade_economica` | CNAE principal (código + descrição) |
| `atividade_economica_secundaria_lista` | CNAEs secundários |
| `endereco` | Logradouro, número, complemento, bairro, município, UF, CEP |
| `telefone` | Telefone de contato |
| `email` | E-mail |
| `qsa` | Quadro de Sócios e Administradores (nome, qualificação, país) |
| `matriz_filial` | MATRIZ ou FILIAL |

### Endpoints AgroADB

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/integrations/receita-cnpj/consultar` | Consulta dados cadastrais por CNPJ |
| GET | `/api/v1/integrations/receita-cnpj/disponibilidade` | Verifica se o portal está acessível |

### Parâmetros de consulta

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `cnpj` | Sim | CNPJ a consultar (14 dígitos) |
| `investigation_id` | Não | ID da investigação para auditoria |

### Estratégia de fallback

A consulta tenta 4 fontes em sequência até obter dados completos:

1. **Receita Federal** (portal direto) — parse de HTML
2. **BrasilAPI** (`brasilapi.com.br/api/cnpj/v1`) — JSON
3. **ReceitaWS** (`receitaws.com.br/v1/cnpj`) — JSON
4. **MinhaReceita** (`minhareceita.org`) — JSON

### Uso no Quick Scan

A consulta Receita Federal CNPJ é executada automaticamente no Quick Scan para investigações com CNPJ.

---

## Observações importantes

- **Nunca versionar chaves reais no Git.** Use `.env` local.
- **Respeitar LGPD e políticas de uso** dos órgãos.
- **Limitar paginação** (SIGEF) para evitar instabilidade.
- **Scrapers:** respeitar rate limit e delay entre requisições; várias páginas públicas usam captcha e podem bloquear consultas automatizadas.
- **APIs gratuitas** (BrasilAPI, IBGE, TSE, CVM, BCB, dados.gov.br, Caixa FGTS, BNMP/CNJ, SEEU/CNJ, SIGEF Público, Receita Federal CPF, Receita Federal CNPJ) não requerem nenhuma configuração.
- **Portal da Transparência** requer apenas uma API Key gratuita, obtida pelo próprio site.
