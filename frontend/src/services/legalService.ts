import { api } from '@/lib/axios'

export type LegalQueryEntry = {
  id: number
  provider: string
  query_type: string
  query_params: Record<string, unknown>
  result_count: number
  response: Record<string, unknown>
  created_at: string
}

export type LegalSummary = {
  summary: Record<string, { total: number; queries: number }>
  updated_at: string
}

export type IntegrationStatus = {
  datajud: { configured: boolean; api_url: string }
  sigef_parcelas: { configured: boolean; api_url: string }
  conecta: {
    sncr: boolean
    sigef: boolean
    sicar: boolean
    sncci?: boolean
    sigef_geo?: boolean
    cnpj?: boolean
    cnd?: boolean
    cadin?: boolean
  }
  portal_servicos?: { configured: boolean; api_url: string }
  servicos_estaduais?: { configured: boolean; api_url: string }
  brasil_api?: { configured: boolean; api_url: string; auth_required: boolean }
  portal_transparencia?: { configured: boolean; api_url: string; auth_required: boolean }
  ibge?: { configured: boolean; api_url: string; auth_required: boolean }
  tse?: { configured: boolean; api_url: string; auth_required: boolean }
  cvm?: { configured: boolean; api_url: string; auth_required: boolean }
  bcb?: { configured: boolean; api_url: string; auth_required: boolean }
  dados_gov?: { configured: boolean; api_url: string; auth_required: boolean }
  redesim_cnpj?: { configured: boolean; api_url: string; auth_required: boolean }
  tjmg?: { configured: boolean; api_url: string; auth_required: boolean }
  antecedentes_mg?: { configured: boolean; api_url: string; auth_required: boolean }
  sicar_publico?: { configured: boolean; api_url: string; auth_required: boolean }
  caixa_fgts?: { configured: boolean; api_url: string; auth_required: boolean }
  bnmp_cnj?: { configured: boolean; api_url: string; auth_required: boolean }
  seeu_cnj?: { configured: boolean; api_url: string; auth_required: boolean }
  sigef_publico?: { configured: boolean; api_url: string; auth_required: boolean }
  receita_cpf?: { configured: boolean; api_url: string; auth_required: boolean }
  receita_cnpj?: { configured: boolean; api_url: string; auth_required: boolean }
}

export const legalService = {
  async datajudProxy(payload: {
    path: string
    method?: 'GET' | 'POST'
    params?: Record<string, unknown>
    payload?: Record<string, unknown>
    investigation_id?: number
    query_type?: string
  }) {
    const response = await api.post('/legal/datajud/proxy', payload)
    return response.data
  },

  async sigefParcelas(payload: Record<string, unknown>) {
    const response = await api.post('/integrations/sigef/parcelas', payload)
    return response.data
  },

  async conectaSncrImovel(payload: { codigo_imovel: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/sncr/imovel', payload)
    return response.data
  },

  async conectaSncrCpfCnpj(payload: { cpf_cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/sncr/cpf-cnpj', payload)
    return response.data
  },

  async conectaSncrSituacao(codigo: string, investigationId?: number) {
    const response = await api.get(`/integrations/conecta/sncr/situacao/${codigo}`, {
      params: investigationId ? { investigation_id: investigationId } : undefined,
    })
    return response.data
  },

  async conectaSncrCcir(codigo: string) {
    const response = await api.get(`/integrations/conecta/sncr/ccir/${codigo}`, {
      responseType: 'blob',
    })
    return response.data as Blob
  },

  async conectaSncciParcelas(payload: { cod_credito: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/sncci/parcelas', payload)
    return response.data
  },

  async conectaSncciCreditosAtivos(payload: { cod_beneficiario: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/sncci/creditos-ativos', payload)
    return response.data
  },

  async conectaSncciCreditos(codigo: string, investigationId?: number) {
    const response = await api.get(`/integrations/conecta/sncci/creditos/${codigo}`, {
      params: investigationId ? { investigation_id: investigationId } : undefined,
    })
    return response.data
  },

  async conectaSncciBoletos(payload: { cd_plano_pagamento_parcela: string }) {
    const response = await api.post('/integrations/conecta/sncci/boletos', payload, {
      responseType: 'blob',
    })
    return response.data as Blob
  },

  async conectaSigefGeoParcelas(payload: Record<string, unknown>) {
    const response = await api.post('/integrations/conecta/sigef-geo/parcelas', payload)
    return response.data
  },

  async conectaSigefGeoParcelasGeojson(payload: Record<string, unknown>) {
    const response = await api.post('/integrations/conecta/sigef-geo/parcelas-geojson', payload)
    return response.data
  },

  async conectaCnpjBasica(payload: { cnpj: string; cpf_usuario: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/cnpj/basica', payload)
    return response.data
  },

  async conectaCnpjQsa(payload: { cnpj: string; cpf_usuario: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/cnpj/qsa', payload)
    return response.data
  },

  async conectaCnpjEmpresa(payload: { cnpj: string; cpf_usuario: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/cnpj/empresa', payload)
    return response.data
  },

  async conectaCndCertidao(payload: {
    tipoContribuinte: number
    contribuinteConsulta: string
    codigoIdentificacao: string
    gerarCertidaoPdf?: boolean
    chave?: string
    investigation_id?: number
  }) {
    const response = await api.post('/integrations/conecta/cnd/certidao', payload)
    return response.data
  },

  async conectaCadinInfoCpf(payload: { cpf: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/cadin/info-cpf', payload)
    return response.data
  },

  async conectaCadinInfoCnpj(payload: { cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/cadin/info-cnpj', payload)
    return response.data
  },

  async conectaCadinCompletaCpf(payload: { cpf: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/cadin/completa-cpf', payload)
    return response.data
  },

  async conectaCadinCompletaCnpj(payload: { cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/cadin/completa-cnpj', payload)
    return response.data
  },

  async conectaCadinVersao() {
    const response = await api.get('/integrations/conecta/cadin/versao')
    return response.data
  },

  async portalServicosOrgao(codSiorg: string) {
    const response = await api.get(`/integrations/portal-servicos/orgao/${codSiorg}`)
    return response.data
  },

  async portalServicosServico(servicoId: string) {
    const response = await api.get(`/integrations/portal-servicos/servicos/${servicoId}`)
    return response.data
  },

  async portalServicosServicoSimples(servicoId: string) {
    const response = await api.get(`/integrations/portal-servicos/servicos-simples/${servicoId}`)
    return response.data
  },

  async portalServicosAuth(authorization?: string) {
    const response = await api.post('/integrations/portal-servicos/servicos-auth', {
      authorization,
    })
    return response.data
  },

  async servicosEstaduaisAuth(payload: { email: string; senha: string }) {
    const response = await api.post('/integrations/servicos-estaduais/auth', payload)
    return response.data
  },

  async servicosEstaduaisInserir(payload: Record<string, unknown>) {
    const response = await api.post('/integrations/servicos-estaduais/servicos', payload)
    return response.data
  },

  async servicosEstaduaisEditar(payload: Record<string, unknown>) {
    const response = await api.put('/integrations/servicos-estaduais/servicos', payload)
    return response.data
  },

  async servicosEstaduaisConsultar(servicoId: string, authorization: string) {
    const response = await api.get(`/integrations/servicos-estaduais/servicos/${servicoId}`, {
      params: { authorization },
    })
    return response.data
  },

  async conectaSigefImovel(payload: { codigo_imovel: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/sigef/imovel', payload)
    return response.data
  },

  async conectaSigefParcelas(payload: { cpf_cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/sigef/parcelas', payload)
    return response.data
  },

  async conectaSicarCpfCnpj(payload: { cpf_cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/sicar/cpf-cnpj', payload)
    return response.data
  },

  async conectaSicarCpfCnpjGet(cpfCnpj: string, investigationId?: number) {
    const response = await api.get(`/integrations/conecta/sicar/cpf-cnpj/${cpfCnpj}`, {
      params: investigationId ? { investigation_id: investigationId } : undefined,
    })
    return response.data
  },

  async conectaSicarImovel(payload: { codigo_imovel: string; investigation_id?: number }) {
    const response = await api.post('/integrations/conecta/sicar/imovel', payload)
    return response.data
  },

  // ======================================================================
  // BrasilAPI (Gratuito, sem auth)
  // ======================================================================

  async brasilApiCnpj(payload: { cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/brasil-api/cnpj', payload)
    return response.data
  },

  async brasilApiCep(cep: string) {
    const response = await api.post('/integrations/brasil-api/cep', { cep })
    return response.data
  },

  async brasilApiBancos() {
    const response = await api.get('/integrations/brasil-api/bancos')
    return response.data
  },

  async brasilApiDdd(ddd: string) {
    const response = await api.get(`/integrations/brasil-api/ddd/${ddd}`)
    return response.data
  },

  async brasilApiPixParticipantes() {
    const response = await api.get('/integrations/brasil-api/pix/participantes')
    return response.data
  },

  async brasilApiCorretoras() {
    const response = await api.get('/integrations/brasil-api/corretoras')
    return response.data
  },

  async brasilApiMunicipios(uf: string) {
    const response = await api.get(`/integrations/brasil-api/municipios/${uf}`)
    return response.data
  },

  // ======================================================================
  // Portal da Transparência (CGU)
  // ======================================================================

  async transparenciaSancoes(payload: { cpf_cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/transparencia/sancoes', payload)
    return response.data
  },

  async transparenciaContratos(payload: { cpf_cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/transparencia/contratos', payload)
    return response.data
  },

  async transparenciaServidores(payload: { cpf_cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/transparencia/servidores', payload)
    return response.data
  },

  async transparenciaBeneficios(payload: { cpf_cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/transparencia/beneficios', payload)
    return response.data
  },

  async transparenciaDespesas(payload: { cpf_cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/transparencia/despesas', payload)
    return response.data
  },

  async transparenciaCompleta(payload: { cpf_cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/transparencia/completa', payload)
    return response.data
  },

  // ======================================================================
  // REDESIM / ReceitaWS — CNPJ público
  // ======================================================================

  async redesimCnpj(payload: { cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/redesim/cnpj', payload)
    return response.data
  },

  // ======================================================================
  // IBGE (Gratuito, sem auth)
  // ======================================================================

  async ibgeEstados() {
    const response = await api.get('/integrations/ibge/estados')
    return response.data
  },

  async ibgeMunicipios(uf: string) {
    const response = await api.get(`/integrations/ibge/municipios/${uf}`)
    return response.data
  },

  async ibgeMunicipio(codigoIbge: string) {
    const response = await api.get(`/integrations/ibge/municipio/${codigoIbge}`)
    return response.data
  },

  async ibgeNome(nome: string) {
    const response = await api.get(`/integrations/ibge/nome/${nome}`)
    return response.data
  },

  async ibgeMalha(codigoIbge: string) {
    const response = await api.get(`/integrations/ibge/malha/${codigoIbge}`)
    return response.data
  },

  // ======================================================================
  // TSE - Tribunal Superior Eleitoral
  // ======================================================================

  async tseBuscar(payload: { query: string; investigation_id?: number }) {
    const response = await api.post('/integrations/tse/buscar', payload)
    return response.data
  },

  async tseCandidatos(ano: number) {
    const response = await api.get(`/integrations/tse/candidatos/${ano}`)
    return response.data
  },

  async tseBens(ano: number) {
    const response = await api.get(`/integrations/tse/bens/${ano}`)
    return response.data
  },

  // ======================================================================
  // CVM - Comissão de Valores Mobiliários
  // ======================================================================

  async cvmFundos(payload: { cnpj?: string; nome?: string; investigation_id?: number }) {
    const response = await api.post('/integrations/cvm/fundos', payload)
    return response.data
  },

  async cvmFii(payload: { cnpj?: string; investigation_id?: number }) {
    const response = await api.post('/integrations/cvm/fii', payload)
    return response.data
  },

  async cvmParticipantes(payload: { cnpj?: string }) {
    const response = await api.post('/integrations/cvm/participantes', payload)
    return response.data
  },

  // ======================================================================
  // BCB - Banco Central do Brasil
  // ======================================================================

  async bcbSelic() {
    const response = await api.get('/integrations/bcb/selic')
    return response.data
  },

  async bcbIpca() {
    const response = await api.get('/integrations/bcb/ipca')
    return response.data
  },

  async bcbCdi() {
    const response = await api.get('/integrations/bcb/cdi')
    return response.data
  },

  async bcbCambio(moeda: string, data?: string) {
    const params = data ? { data } : undefined
    const response = await api.get(`/integrations/bcb/cambio/${moeda}`, { params })
    return response.data
  },

  async bcbPixParticipantes() {
    const response = await api.get('/integrations/bcb/pix/participantes')
    return response.data
  },

  // ======================================================================
  // dados.gov.br
  // ======================================================================

  async dadosGovBuscar(payload: { query: string; pagina?: number }) {
    const response = await api.post('/integrations/dados-gov/buscar', payload)
    return response.data
  },

  async dadosGovRural(pagina?: number) {
    const response = await api.get('/integrations/dados-gov/rural', { params: { pagina } })
    return response.data
  },

  async dadosGovAmbiental(pagina?: number) {
    const response = await api.get('/integrations/dados-gov/ambiental', { params: { pagina } })
    return response.data
  },

  async dadosGovOrganizacoes(query?: string) {
    const response = await api.get('/integrations/dados-gov/organizacoes', { params: { query } })
    return response.data
  },

  // ======================================================================
  // TJMG — Tribunal de Justiça de Minas Gerais
  // ======================================================================

  async tjmgProcessos(payload: {
    cpf?: string
    cnpj?: string
    nome_parte?: string
    nome_advogado?: string
    numero_processo?: string
    investigation_id?: number
  }) {
    const response = await api.post('/integrations/tjmg/processos', payload)
    return response.data
  },

  async tjmgProcessosCpf(payload: { cpf: string; investigation_id?: number }) {
    const response = await api.post('/integrations/tjmg/processos/cpf', payload)
    return response.data
  },

  async tjmgProcessosCnpj(payload: { cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/tjmg/processos/cnpj', payload)
    return response.data
  },

  async tjmgProcessoNumero(numero: string, investigationId?: number) {
    const response = await api.get(`/integrations/tjmg/processos/${numero}`, {
      params: investigationId ? { investigation_id: investigationId } : undefined,
    })
    return response.data
  },

  async tjmgConfiguration() {
    const response = await api.get('/integrations/tjmg/configuration')
    return response.data
  },

  // ======================================================================
  // Antecedentes Criminais / MG
  // ======================================================================

  async antecedentesMgConsultar(payload: { cpf: string; rg: string; investigation_id?: number }) {
    const response = await api.post('/integrations/antecedentes-mg/consultar', payload)
    return response.data
  },

  async antecedentesMgDisponibilidade() {
    const response = await api.get('/integrations/antecedentes-mg/disponibilidade')
    return response.data
  },

  // ======================================================================
  // SICAR Público — Cadastro Ambiental Rural
  // ======================================================================

  async sicarPublicoImovel(payload: { car: string; investigation_id?: number }) {
    const response = await api.post('/integrations/sicar-publico/imovel', payload)
    return response.data
  },

  async sicarPublicoMunicipio(codigoIbge: string) {
    const response = await api.get(`/integrations/sicar-publico/municipio/${codigoIbge}`)
    return response.data
  },

  async sicarPublicoDisponibilidade() {
    const response = await api.get('/integrations/sicar-publico/disponibilidade')
    return response.data
  },

  // ======================================================================
  // Caixa — Regularidade do Empregador (FGTS / CRF)
  // ======================================================================

  async caixaFgtsConsultar(payload: { cnpj?: string; cei?: string; investigation_id?: number }) {
    const response = await api.post('/integrations/caixa-fgts/consultar', payload)
    return response.data
  },

  async caixaFgtsDisponibilidade() {
    const response = await api.get('/integrations/caixa-fgts/disponibilidade')
    return response.data
  },

  // ======================================================================
  // BNMP — Banco Nacional de Mandados de Prisão (CNJ)
  // ======================================================================

  async bnmpConsultar(payload: { cpf?: string; nome?: string; nome_mae?: string; investigation_id?: number }) {
    const response = await api.post('/integrations/bnmp/consultar', payload)
    return response.data
  },

  async bnmpDisponibilidade() {
    const response = await api.get('/integrations/bnmp/disponibilidade')
    return response.data
  },

  // ======================================================================
  // SEEU — Sistema Eletrônico de Execução Unificado (CNJ)
  // ======================================================================

  async seeuConsultar(payload: {
    cpf?: string; cnpj?: string; nome_parte?: string;
    nome_mae?: string; numero_processo?: string; investigation_id?: number
  }) {
    const response = await api.post('/integrations/seeu/consultar', payload)
    return response.data
  },

  async seeuDisponibilidade() {
    const response = await api.get('/integrations/seeu/disponibilidade')
    return response.data
  },

  // ======================================================================
  // SIGEF Público — Parcelas INCRA (consulta direta)
  // ======================================================================

  async sigefPublicoParcelas(payload: {
    cpf?: string; cnpj?: string; codigo_imovel?: string;
    paginas?: number; investigation_id?: number
  }) {
    const response = await api.post('/integrations/sigef-publico/parcelas', payload)
    return response.data
  },

  async sigefPublicoDisponibilidade() {
    const response = await api.get('/integrations/sigef-publico/disponibilidade')
    return response.data
  },

  // ======================================================================
  // Receita Federal — Consulta CPF (Situação Cadastral)
  // ======================================================================

  async receitaCpfConsultar(payload: { cpf: string; data_nascimento?: string; investigation_id?: number }) {
    const response = await api.post('/integrations/receita-cpf/consultar', payload)
    return response.data
  },

  async receitaCpfDisponibilidade() {
    const response = await api.get('/integrations/receita-cpf/disponibilidade')
    return response.data
  },

  // ======================================================================
  // Receita Federal — Consulta CNPJ (Dados Cadastrais PJ)
  // ======================================================================

  async receitaCnpjConsultar(payload: { cnpj: string; investigation_id?: number }) {
    const response = await api.post('/integrations/receita-cnpj/consultar', payload)
    return response.data
  },

  async receitaCnpjDisponibilidade() {
    const response = await api.get('/integrations/receita-cnpj/disponibilidade')
    return response.data
  },

  // ======================================================================
  // Queries e Status
  // ======================================================================

  async listLegalQueries(investigationId: number): Promise<LegalQueryEntry[]> {
    const response = await api.get<LegalQueryEntry[]>(`/legal/queries/investigation/${investigationId}`)
    return response.data
  },

  async getLegalSummary(): Promise<LegalSummary> {
    const response = await api.get<LegalSummary>('/legal/queries/summary')
    return response.data
  },

  async getIntegrationStatus(): Promise<IntegrationStatus> {
    const response = await api.get<IntegrationStatus>('/integrations/status')
    return response.data
  },
}
