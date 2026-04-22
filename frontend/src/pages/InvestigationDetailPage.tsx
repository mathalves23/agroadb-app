import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, XCircle } from 'lucide-react'
import { investigationService } from '@/services/investigationService'
import { useAuthStore } from '@/stores/authStore'
import { legalService } from '@/services/legalService'
import { LegalQueriesTab } from '@/components/legal/LegalQueriesTab'
import {
  InvestigationHeader,
  EnrichedDataCard,
} from '@/components/investigation'
import ShareModal from '@/components/ShareModal'
import { PanelListLoader } from '@/components/Loading'
import { EmptyState } from '@/components/EmptyState'
import {
  InvestigationTabs,
  type InvestigationDetailTab,
} from '@/pages/investigationDetail/InvestigationTabs'
import { InvestigationSummaryTab } from '@/pages/investigationDetail/InvestigationSummaryTab'
import { InvestigationMlTab } from '@/pages/investigationDetail/InvestigationMlTab'
import { InvestigationNetworkTab } from '@/pages/investigationDetail/InvestigationNetworkTab'
import { InvestigationCollaborationTab } from '@/pages/investigationDetail/InvestigationCollaborationTab'
import { LegalConfigWarning } from '@/pages/investigationDetail/LegalConfigWarning'
import { LegalSummaryOverview } from '@/pages/investigationDetail/LegalSummaryOverview'
import { LegalHistoryPanel } from '@/pages/investigationDetail/LegalHistoryPanel'
import { useInvestigationDetailData } from '@/pages/investigationDetail/useInvestigationDetailData'

interface AxiosLikeError {
  response?: { data?: { detail?: string } }
  message?: string
}

export default function InvestigationDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<InvestigationDetailTab>('summary')
  const [shareModalOpen, setShareModalOpen] = useState(false)
  const user = useAuthStore((s) => s.user)
  const currentUserId = user?.id ?? null
  const isDevMode = process.env.NODE_ENV !== 'production'
  const {
    applyCpfCnpjToForms,
    cadinCnpj,
    cadinCpf,
    cadinResult,
    chartByDate,
    chartByProvider,
    cndChave,
    cndCodigoIdentificacao,
    cndContribuinteConsulta,
    cndGerarPdf,
    cndResult,
    cndTipoContribuinte,
    cnpjCpfUsuario,
    cnpjResult,
    cnpjValue,
    companies,
    defaultCpfCnpj,
    errorMessage,
    exportLoading,
    exportPDF,
    exportTrustBundle,
    handleExportCSV,
    handleExportExcel,
    integrationStatus,
    investigation,
    isLoading,
    isLoadingNetwork,
    isLoadingPatterns,
    isLoadingRisk,
    latestQuery,
    legalQueries,
    networkAnalysis,
    patterns,
    pieData,
    portalServicosId,
    portalServicosOrgao,
    portalServicosResult,
    portalServicosToken,
    properties,
    quickScanLog,
    quickScanProgress,
    quickScanRunning,
    quickScanTotal,
    riskScore,
    runQuickScan,
    sicarCpfCnpj,
    sicarResult,
    servicosEstaduaisAuth,
    servicosEstaduaisEmail,
    servicosEstaduaisId,
    servicosEstaduaisPayload,
    servicosEstaduaisResult,
    servicosEstaduaisSenha,
    setCadinCnpj,
    setCadinCpf,
    setCadinResult,
    setCndChave,
    setCndCodigoIdentificacao,
    setCndContribuinteConsulta,
    setCndGerarPdf,
    setCndResult,
    setCndTipoContribuinte,
    setCnpjCpfUsuario,
    setCnpjResult,
    setCnpjValue,
    setDataJudResult,
    setErrorMessage,
    setPortalServicosId,
    setPortalServicosOrgao,
    setPortalServicosResult,
    setPortalServicosToken,
    setSicarCpfCnpj,
    setSicarResult,
    setServicosEstaduaisAuth,
    setServicosEstaduaisEmail,
    setServicosEstaduaisId,
    setServicosEstaduaisPayload,
    setServicosEstaduaisResult,
    setServicosEstaduaisSenha,
    setSigefGeoFilters,
    setSigefGeoResult,
    setSigefResult,
    setSncciBoletoStatus,
    setSncciCodBeneficiario,
    setSncciCodPlanoParcela,
    setSncciCodigoCredito,
    setSncciResult,
    setSncrCcirStatus,
    setSncrCodigo,
    setSncrCpfCnpj,
    setSncrResult,
    sigefGeoFilters,
    sigefGeoResult,
    sncciBoletoStatus,
    sncciCodBeneficiario,
    sncciCodPlanoParcela,
    sncciCodigoCredito,
    sncciResult,
    sncrCcirStatus,
    sncrCodigo,
    sncrCpfCnpj,
    sncrResult,
    summaryCpfCnpj,
    summarySources,
    summarySourcesWithData,
    totalQueries,
    totalResults,
  } = useInvestigationDetailData(id, activeTab)

  const riskReviewMutation = useMutation({
    mutationFn: () => investigationService.acknowledgeRiskScoreReview(Number(id)),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['investigation', id] })
      void queryClient.invalidateQueries({ queryKey: ['risk-score', id] })
    },
  })

  const dataJudConfigured = integrationStatus?.datajud?.configured ?? true
  const sigefConfigured = integrationStatus?.sigef_parcelas?.configured ?? true
  const sncrConfigured = integrationStatus?.conecta?.sncr ?? true
  const sncciConfigured = integrationStatus?.conecta?.sncci ?? true
  const sigefGeoConfigured = integrationStatus?.conecta?.sigef_geo ?? true
  const cnpjConfigured = integrationStatus?.conecta?.cnpj ?? true
  const cndConfigured = integrationStatus?.conecta?.cnd ?? true
  const cadinConfigured = integrationStatus?.conecta?.cadin ?? true
  const portalServicosConfigured = integrationStatus?.portal_servicos?.configured ?? true
  const servicosEstaduaisConfigured = integrationStatus?.servicos_estaduais?.configured ?? true
  const legalWarnings = [
    !dataJudConfigured && 'DataJud',
    !sigefConfigured && 'SIGEF Parcelas',
    !sncrConfigured && 'SNCR',
    !sncciConfigured && 'SNCCI',
    !sigefGeoConfigured && 'SIGEF GEO',
    !cnpjConfigured && 'CNPJ',
    !cndConfigured && 'CND',
    !cadinConfigured && 'CADIN',
    !portalServicosConfigured && 'Portal Serviços',
    !servicosEstaduaisConfigured && 'Serv. Estaduais',
  ].filter(Boolean) as string[]

  const sncrSituacaoMutation = useMutation({
    mutationFn: (codigo: string) => legalService.conectaSncrSituacao(codigo, Number(id)),
    onSuccess: (data) => {
      setSncrResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar SNCR')
    },
  })

  const sncrImovelMutation = useMutation({
    mutationFn: (codigo: string) =>
      legalService.conectaSncrImovel({ codigo_imovel: codigo, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setSncrResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar SNCR')
    },
  })

  const sncrCpfMutation = useMutation({
    mutationFn: (cpfCnpj: string) =>
      legalService.conectaSncrCpfCnpj({ cpf_cnpj: cpfCnpj, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setSncrResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar SNCR')
    },
  })

  const sncrCcirMutation = useMutation({
    mutationFn: (codigo: string) => legalService.conectaSncrCcir(codigo),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `ccir_${sncrCodigo || 'imovel'}.pdf`
      link.click()
      URL.revokeObjectURL(url)
      setSncrCcirStatus('Download do CCIR iniciado.')
      setErrorMessage(null)
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao baixar CCIR')
    },
  })

  const sncciParcelasMutation = useMutation({
    mutationFn: (codigo: string) =>
      legalService.conectaSncciParcelas({ cod_credito: codigo, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setSncciResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar SNCCI')
    },
  })

  const sncciCreditosAtivosMutation = useMutation({
    mutationFn: (codigo: string) =>
      legalService.conectaSncciCreditosAtivos({ cod_beneficiario: codigo, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setSncciResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar SNCCI')
    },
  })

  const sncciCreditosMutation = useMutation({
    mutationFn: (codigo: string) => legalService.conectaSncciCreditos(codigo, Number(id)),
    onSuccess: (data) => {
      setSncciResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar SNCCI')
    },
  })

  const sncciBoletosMutation = useMutation({
    mutationFn: (codigo: string) =>
      legalService.conectaSncciBoletos({ cd_plano_pagamento_parcela: codigo }),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `sncci_boleto_${sncciCodPlanoParcela || 'parcela'}.pdf`
      link.click()
      URL.revokeObjectURL(url)
      setSncciBoletoStatus('Download do boleto iniciado.')
      setErrorMessage(null)
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao baixar boleto SNCCI')
    },
  })

  const sigefGeoMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      legalService.conectaSigefGeoParcelas({ ...payload, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setSigefGeoResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar SIGEF GEO')
    },
  })

  const sigefGeoGeojsonMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      legalService.conectaSigefGeoParcelasGeojson({ ...payload, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setSigefGeoResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar SIGEF GEO (GeoJSON)')
    },
  })

  const sicarCpfCnpjMutation = useMutation({
    mutationFn: (cpfCnpj: string) => legalService.conectaSicarCpfCnpjGet(cpfCnpj, Number(id)),
    onSuccess: (data) => {
      setSicarResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar SICAR')
    },
  })

  const cnpjBasicaMutation = useMutation({
    mutationFn: (payload: { cnpj: string; cpf_usuario: string }) =>
      legalService.conectaCnpjBasica({ ...payload, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setCnpjResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar CNPJ Básica')
    },
  })

  const cnpjQsaMutation = useMutation({
    mutationFn: (payload: { cnpj: string; cpf_usuario: string }) =>
      legalService.conectaCnpjQsa({ ...payload, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setCnpjResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar CNPJ QSA')
    },
  })

  const cnpjEmpresaMutation = useMutation({
    mutationFn: (payload: { cnpj: string; cpf_usuario: string }) =>
      legalService.conectaCnpjEmpresa({ ...payload, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setCnpjResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar CNPJ Empresa')
    },
  })

  const cndCertidaoMutation = useMutation({
    mutationFn: (payload: {
      tipoContribuinte: number
      contribuinteConsulta: string
      codigoIdentificacao: string
      gerarCertidaoPdf?: boolean
      chave?: string
    }) => legalService.conectaCndCertidao({ ...payload, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setCndResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar CND')
    },
  })

  const cadinInfoCpfMutation = useMutation({
    mutationFn: (cpf: string) => legalService.conectaCadinInfoCpf({ cpf, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setCadinResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar CADIN CPF')
    },
  })

  const cadinInfoCnpjMutation = useMutation({
    mutationFn: (cnpj: string) => legalService.conectaCadinInfoCnpj({ cnpj, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setCadinResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar CADIN CNPJ')
    },
  })

  const cadinCompletaCpfMutation = useMutation({
    mutationFn: (cpf: string) => legalService.conectaCadinCompletaCpf({ cpf, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setCadinResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar CADIN CPF completo')
    },
  })

  const cadinCompletaCnpjMutation = useMutation({
    mutationFn: (cnpj: string) => legalService.conectaCadinCompletaCnpj({ cnpj, investigation_id: Number(id) }),
    onSuccess: (data) => {
      setCadinResult(data as Record<string, unknown>)
      setErrorMessage(null)
      queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar CADIN CNPJ completo')
    },
  })

  const portalServicosOrgaoMutation = useMutation({
    mutationFn: (codSiorg: string) => legalService.portalServicosOrgao(codSiorg),
    onSuccess: (data) => {
      setPortalServicosResult(data as Record<string, unknown>)
      setErrorMessage(null)
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar órgão')
    },
  })

  const portalServicosCompletoMutation = useMutation({
    mutationFn: (servicoId: string) => legalService.portalServicosServico(servicoId),
    onSuccess: (data) => {
      setPortalServicosResult(data as Record<string, unknown>)
      setErrorMessage(null)
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar serviço')
    },
  })

  const portalServicosSimplesMutation = useMutation({
    mutationFn: (servicoId: string) => legalService.portalServicosServicoSimples(servicoId),
    onSuccess: (data) => {
      setPortalServicosResult(data as Record<string, unknown>)
      setErrorMessage(null)
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar serviço simples')
    },
  })

  const portalServicosAuthMutation = useMutation({
    mutationFn: (token?: string) => legalService.portalServicosAuth(token),
    onSuccess: (data) => {
      setPortalServicosResult(data as Record<string, unknown>)
      setErrorMessage(null)
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao listar serviços autenticados')
    },
  })

  const servicosEstaduaisAuthMutation = useMutation({
    mutationFn: (payload: { email: string; senha: string }) => legalService.servicosEstaduaisAuth(payload),
    onSuccess: (data) => {
      setServicosEstaduaisResult(data as Record<string, unknown>)
      const authData = data as Record<string, unknown>
      const token = (authData?.authorization || authData?.autorizacao) as string | undefined
      if (token) {
        setServicosEstaduaisAuth(token)
      }
      setErrorMessage(null)
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao autenticar Serviços Estaduais')
    },
  })

  const servicosEstaduaisInserirMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => legalService.servicosEstaduaisInserir(payload),
    onSuccess: (data) => {
      setServicosEstaduaisResult(data as Record<string, unknown>)
      setErrorMessage(null)
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao inserir serviço estadual')
    },
  })

  const servicosEstaduaisEditarMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => legalService.servicosEstaduaisEditar(payload),
    onSuccess: (data) => {
      setServicosEstaduaisResult(data as Record<string, unknown>)
      setErrorMessage(null)
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao editar serviço estadual')
    },
  })

  const servicosEstaduaisConsultarMutation = useMutation({
    mutationFn: (payload: { servicoId: string; authorization: string }) =>
      legalService.servicosEstaduaisConsultar(payload.servicoId, payload.authorization),
    onSuccess: (data) => {
      setServicosEstaduaisResult(data as Record<string, unknown>)
      setErrorMessage(null)
    },
    onError: (error: AxiosLikeError) => {
      setErrorMessage(error?.response?.data?.detail || 'Erro ao consultar serviço estadual')
    },
  })

  if (isLoading) {
    return (
      <PanelListLoader
        message="Carregando..."
        subMessage="Carregando detalhes da investigação e integrações disponíveis."
      />
    )
  }

  if (!investigation) {
    return (
      <EmptyState
        variant="embedded"
        illustration="folder"
        title="Investigação não encontrada"
        description="O identificador não corresponde a nenhum registro ou foi removido."
        action={{
          label: 'Voltar às investigações',
          onClick: () => navigate('/investigations'),
        }}
      />
    )
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate('/investigations')}
        className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>Voltar</span>
      </button>

      <InvestigationHeader
        investigation={investigation}
        onBack={() => navigate('/investigations')}
      />

      <EnrichedDataCard targetDescription={investigation.target_description} />

      <InvestigationTabs activeTab={activeTab} onChange={setActiveTab} />

      {activeTab === 'summary' && (
        <InvestigationSummaryTab
          chartByDate={chartByDate}
          chartByProvider={chartByProvider}
          companies={companies}
          defaultCpfCnpj={defaultCpfCnpj}
          exportLoading={exportLoading}
          handleExportCSV={handleExportCSV}
          handleExportExcel={handleExportExcel}
          isDevMode={isDevMode}
          investigation={investigation}
          latestQuery={latestQuery}
          legalQueries={legalQueries}
          onApplyCpfCnpj={applyCpfCnpjToForms}
          onExportPDF={exportPDF}
          onExportTrustBundle={exportTrustBundle}
          onOpenLegalTab={() => setActiveTab('legal')}
          onRunQuickScan={runQuickScan}
          pieData={pieData}
          properties={properties}
          quickScanLog={quickScanLog}
          quickScanProgress={quickScanProgress}
          quickScanRunning={quickScanRunning}
          quickScanTotal={quickScanTotal}
          summaryCpfCnpj={summaryCpfCnpj}
          summarySources={summarySources}
          summarySourcesWithDataCount={summarySourcesWithData.length}
          totalQueries={totalQueries}
          totalResults={totalResults}
        />
      )}

      {activeTab === 'legal' && (
        <div className="space-y-6">
          <LegalConfigWarning warnings={legalWarnings} />
          {errorMessage && (
            <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-xl p-3">
              <XCircle className="h-4 w-4 text-red-500 shrink-0" />
              <p className="text-xs text-red-700">{errorMessage}</p>
              <button onClick={() => setErrorMessage(null)} className="ml-auto text-red-400 hover:text-red-600 text-xs font-medium">Fechar</button>
            </div>
          )}
          <LegalSummaryOverview
            defaultCpfCnpj={defaultCpfCnpj}
            latestQuery={latestQuery}
            onApplyCpfCnpj={applyCpfCnpjToForms}
            summaryCpfCnpj={summaryCpfCnpj}
            summarySources={summarySources}
            summarySourcesWithDataCount={summarySourcesWithData.length}
            totalQueries={totalQueries}
            totalResults={totalResults}
          />

          <LegalQueriesTab
            investigationId={id}
            defaultCpfCnpj={defaultCpfCnpj}
            onApplyCpfCnpj={applyCpfCnpjToForms}
            onError={setErrorMessage}
            onDataJudResult={setDataJudResult}
            onSigefResult={setSigefResult}
          />

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900">Serviços Estaduais</h2>
              <p className="text-sm text-gray-500 mt-1">
                Integração com a carta de serviços estadual do gov.br.
              </p>
              <div className="mt-4 space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    value={servicosEstaduaisEmail}
                    onChange={(event) => setServicosEstaduaisEmail(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="email@estado.gov.br"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Senha</label>
                  <input
                    type="password"
                    value={servicosEstaduaisSenha}
                    onChange={(event) => setServicosEstaduaisSenha(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="Senha"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Token</label>
                  <input
                    value={servicosEstaduaisAuth}
                    onChange={(event) => setServicosEstaduaisAuth(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="Token de autorização"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">ID do serviço</label>
                  <input
                    value={servicosEstaduaisId}
                    onChange={(event) => setServicosEstaduaisId(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="idServico"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Payload do serviço (JSON)</label>
                  <textarea
                    value={servicosEstaduaisPayload}
                    onChange={(event) => setServicosEstaduaisPayload(event.target.value)}
                    rows={8}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm font-mono text-xs"
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      if (!servicosEstaduaisConfigured) {
                        setErrorMessage('Serviços Estaduais não configurado')
                        return
                      }
                      if (!servicosEstaduaisEmail || !servicosEstaduaisSenha) {
                        setErrorMessage('Informe email e senha')
                        return
                      }
                      servicosEstaduaisAuthMutation.mutate({
                        email: servicosEstaduaisEmail,
                        senha: servicosEstaduaisSenha,
                      })
                    }}
                    disabled={servicosEstaduaisAuthMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {servicosEstaduaisAuthMutation.isPending ? 'Autenticando...' : 'Autenticar'}
                  </button>
                  <button
                    onClick={() => {
                      if (!servicosEstaduaisConfigured) {
                        setErrorMessage('Serviços Estaduais não configurado')
                        return
                      }
                      if (!servicosEstaduaisAuth) {
                        setErrorMessage('Informe o token de autorização')
                        return
                      }
                      try {
                        const payload = JSON.parse(servicosEstaduaisPayload)
                        servicosEstaduaisInserirMutation.mutate({
                          authorization: servicosEstaduaisAuth,
                          ...payload,
                        })
                      } catch (error) {
                        setErrorMessage('JSON inválido no payload do serviço')
                      }
                    }}
                    disabled={servicosEstaduaisInserirMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    {servicosEstaduaisInserirMutation.isPending ? 'Enviando...' : 'Inserir'}
                  </button>
                  <button
                    onClick={() => {
                      if (!servicosEstaduaisConfigured) {
                        setErrorMessage('Serviços Estaduais não configurado')
                        return
                      }
                      if (!servicosEstaduaisAuth) {
                        setErrorMessage('Informe o token de autorização')
                        return
                      }
                      try {
                        const payload = JSON.parse(servicosEstaduaisPayload)
                        servicosEstaduaisEditarMutation.mutate({
                          authorization: servicosEstaduaisAuth,
                          ...payload,
                        })
                      } catch (error) {
                        setErrorMessage('JSON inválido no payload do serviço')
                      }
                    }}
                    disabled={servicosEstaduaisEditarMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    {servicosEstaduaisEditarMutation.isPending ? 'Enviando...' : 'Editar'}
                  </button>
                  <button
                    onClick={() => {
                      if (!servicosEstaduaisConfigured) {
                        setErrorMessage('Serviços Estaduais não configurado')
                        return
                      }
                      if (!servicosEstaduaisAuth || !servicosEstaduaisId) {
                        setErrorMessage('Informe token e ID do serviço')
                        return
                      }
                      servicosEstaduaisConsultarMutation.mutate({
                        servicoId: servicosEstaduaisId,
                        authorization: servicosEstaduaisAuth,
                      })
                    }}
                    disabled={servicosEstaduaisConsultarMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {servicosEstaduaisConsultarMutation.isPending ? 'Consultando...' : 'Consultar'}
                  </button>
                </div>
              </div>
              {servicosEstaduaisResult && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700">Resultado</h3>
                  <pre className="mt-2 text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                    {JSON.stringify(servicosEstaduaisResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900">Portal de Serviços (gov.br)</h2>
              <p className="text-sm text-gray-500 mt-1">
                Consulta órgãos e serviços do Portal gov.br.
              </p>
              <div className="mt-4 space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Código SIORG</label>
                  <input
                    value={portalServicosOrgao}
                    onChange={(event) => setPortalServicosOrgao(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="123456"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">ID do serviço</label>
                  <input
                    value={portalServicosId}
                    onChange={(event) => setPortalServicosId(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="servicoId"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Token (serviços-auth)</label>
                  <input
                    value={portalServicosToken}
                    onChange={(event) => setPortalServicosToken(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="Bearer ..."
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      if (!portalServicosConfigured) {
                        setErrorMessage('Portal de Serviços não configurado')
                        return
                      }
                      if (!portalServicosOrgao) {
                        setErrorMessage('Informe o código SIORG')
                        return
                      }
                      portalServicosOrgaoMutation.mutate(portalServicosOrgao)
                    }}
                    disabled={portalServicosOrgaoMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {portalServicosOrgaoMutation.isPending ? 'Consultando...' : 'Consultar órgão'}
                  </button>
                  <button
                    onClick={() => {
                      if (!portalServicosConfigured) {
                        setErrorMessage('Portal de Serviços não configurado')
                        return
                      }
                      if (!portalServicosId) {
                        setErrorMessage('Informe o ID do serviço')
                        return
                      }
                      portalServicosCompletoMutation.mutate(portalServicosId)
                    }}
                    disabled={portalServicosCompletoMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {portalServicosCompletoMutation.isPending ? 'Consultando...' : 'Serviço completo'}
                  </button>
                  <button
                    onClick={() => {
                      if (!portalServicosConfigured) {
                        setErrorMessage('Portal de Serviços não configurado')
                        return
                      }
                      if (!portalServicosId) {
                        setErrorMessage('Informe o ID do serviço')
                        return
                      }
                      portalServicosSimplesMutation.mutate(portalServicosId)
                    }}
                    disabled={portalServicosSimplesMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    {portalServicosSimplesMutation.isPending ? 'Consultando...' : 'Serviço simples'}
                  </button>
                  <button
                    onClick={() => {
                      if (!portalServicosConfigured) {
                        setErrorMessage('Portal de Serviços não configurado')
                        return
                      }
                      portalServicosAuthMutation.mutate(portalServicosToken || undefined)
                    }}
                    disabled={portalServicosAuthMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    {portalServicosAuthMutation.isPending ? 'Consultando...' : 'Serviços autenticados'}
                  </button>
                </div>
              </div>
              {portalServicosResult && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700">Resultado</h3>
                  <pre className="mt-2 text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                    {JSON.stringify(portalServicosResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900">Consulta CADIN</h2>
              <p className="text-sm text-gray-500 mt-1">
                Situação e consulta completa por CPF/CNPJ (Conecta).
              </p>
              <div className="mt-4 space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">CPF</label>
                  <input
                    value={cadinCpf}
                    onChange={(event) => setCadinCpf(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="00000000191"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">CNPJ</label>
                  <input
                    value={cadinCnpj}
                    onChange={(event) => setCadinCnpj(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="00000000000191"
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      if (!cadinConfigured) {
                        setErrorMessage('CADIN (Conecta) não configurado')
                        return
                      }
                      if (!cadinCpf) {
                        setErrorMessage('Informe o CPF')
                        return
                      }
                      cadinInfoCpfMutation.mutate(cadinCpf)
                    }}
                    disabled={cadinInfoCpfMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {cadinInfoCpfMutation.isPending ? 'Consultando...' : 'Info CPF'}
                  </button>
                  <button
                    onClick={() => {
                      if (!cadinConfigured) {
                        setErrorMessage('CADIN (Conecta) não configurado')
                        return
                      }
                      if (!cadinCnpj) {
                        setErrorMessage('Informe o CNPJ')
                        return
                      }
                      cadinInfoCnpjMutation.mutate(cadinCnpj)
                    }}
                    disabled={cadinInfoCnpjMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {cadinInfoCnpjMutation.isPending ? 'Consultando...' : 'Info CNPJ'}
                  </button>
                  <button
                    onClick={() => {
                      if (!cadinConfigured) {
                        setErrorMessage('CADIN (Conecta) não configurado')
                        return
                      }
                      if (!cadinCpf) {
                        setErrorMessage('Informe o CPF')
                        return
                      }
                      cadinCompletaCpfMutation.mutate(cadinCpf)
                    }}
                    disabled={cadinCompletaCpfMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    {cadinCompletaCpfMutation.isPending ? 'Consultando...' : 'Completa CPF'}
                  </button>
                  <button
                    onClick={() => {
                      if (!cadinConfigured) {
                        setErrorMessage('CADIN (Conecta) não configurado')
                        return
                      }
                      if (!cadinCnpj) {
                        setErrorMessage('Informe o CNPJ')
                        return
                      }
                      cadinCompletaCnpjMutation.mutate(cadinCnpj)
                    }}
                    disabled={cadinCompletaCnpjMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    {cadinCompletaCnpjMutation.isPending ? 'Consultando...' : 'Completa CNPJ'}
                  </button>
                </div>
              </div>
              {cadinResult && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700">Resultado</h3>
                  <pre className="mt-2 text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                    {JSON.stringify(cadinResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900">Consulta SNCR</h2>
              <p className="text-sm text-gray-500 mt-1">
                Endpoints oficiais do Conecta (requer credenciais e IP autorizado).
              </p>
              <div className="mt-4 space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Código do imóvel</label>
                  <input
                    value={sncrCodigo}
                    onChange={(event) => setSncrCodigo(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="9510990856428"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">CPF/CNPJ</label>
                  <input
                    value={sncrCpfCnpj}
                    onChange={(event) => setSncrCpfCnpj(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="59346402083"
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      if (!sncrCodigo) {
                        setErrorMessage('Informe o código do imóvel')
                        return
                      }
                      sncrSituacaoMutation.mutate(sncrCodigo)
                    }}
                    disabled={sncrSituacaoMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {sncrSituacaoMutation.isPending ? 'Consultando...' : 'Verificar situação'}
                  </button>
                  <button
                    onClick={() => {
                      if (!sncrCodigo) {
                        setErrorMessage('Informe o código do imóvel')
                        return
                      }
                      sncrImovelMutation.mutate(sncrCodigo)
                    }}
                    disabled={sncrImovelMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {sncrImovelMutation.isPending ? 'Consultando...' : 'Consultar por código'}
                  </button>
                  <button
                    onClick={() => {
                      if (!sncrCpfCnpj) {
                        setErrorMessage('Informe o CPF/CNPJ')
                        return
                      }
                      sncrCpfMutation.mutate(sncrCpfCnpj)
                    }}
                    disabled={sncrCpfMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {sncrCpfMutation.isPending ? 'Consultando...' : 'Consultar por CPF/CNPJ'}
                  </button>
                  <button
                    onClick={() => {
                      if (!sncrCodigo) {
                        setErrorMessage('Informe o código do imóvel')
                        return
                      }
                      sncrCcirMutation.mutate(sncrCodigo)
                    }}
                    disabled={sncrCcirMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    {sncrCcirMutation.isPending ? 'Baixando...' : 'Baixar CCIR'}
                  </button>
                </div>
              </div>
              {sncrCcirStatus && (
                <div className="mt-3 text-sm text-green-700">{sncrCcirStatus}</div>
              )}
              {sncrResult && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700">Resultado</h3>
                  <pre className="mt-2 text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                    {JSON.stringify(sncrResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900">Consulta CND</h2>
              <p className="text-sm text-gray-500 mt-1">
                Certidão Negativa de Débitos (RFB/PGFN).
              </p>
              <div className="mt-4 space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tipo do contribuinte</label>
                  <select
                    value={cndTipoContribuinte}
                    onChange={(event) => setCndTipoContribuinte(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                  >
                    <option value="1">CNPJ</option>
                    <option value="2">CPF</option>
                    <option value="3">NIRF</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Contribuinte</label>
                  <input
                    value={cndContribuinteConsulta}
                    onChange={(event) => setCndContribuinteConsulta(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="CNPJ/CPF/NIRF"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Código de identificação</label>
                  <input
                    value={cndCodigoIdentificacao}
                    onChange={(event) => setCndCodigoIdentificacao(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="Código de identificação"
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    id="cnd-gerar-pdf"
                    type="checkbox"
                    checked={cndGerarPdf}
                    onChange={(event) => setCndGerarPdf(event.target.checked)}
                  />
                  <label htmlFor="cnd-gerar-pdf" className="text-sm text-gray-700">
                    Gerar PDF
                  </label>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Chave (consulta demorada)</label>
                  <input
                    value={cndChave}
                    onChange={(event) => setCndChave(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="Chave opcional"
                  />
                </div>
                <button
                  onClick={() => {
                    if (!cndConfigured) {
                      setErrorMessage('CND (Conecta) não configurado')
                      return
                    }
                    if (!cndContribuinteConsulta || !cndCodigoIdentificacao) {
                      setErrorMessage('Informe contribuinte e código de identificação')
                      return
                    }
                    cndCertidaoMutation.mutate({
                      tipoContribuinte: Number(cndTipoContribuinte),
                      contribuinteConsulta: cndContribuinteConsulta,
                      codigoIdentificacao: cndCodigoIdentificacao,
                      gerarCertidaoPdf: cndGerarPdf,
                      chave: cndChave || undefined,
                    })
                  }}
                  disabled={cndCertidaoMutation.isPending}
                  className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                >
                  {cndCertidaoMutation.isPending ? 'Consultando...' : 'Consultar'}
                </button>
              </div>
              {cndResult && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700">Resultado</h3>
                  <pre className="mt-2 text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                    {JSON.stringify(cndResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900">Consulta SIGEF GEO</h2>
              <p className="text-sm text-gray-500 mt-1">
                Consulta parcelas georreferenciadas (Conecta).
              </p>
              <div className="mt-4 space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Filtros (JSON)</label>
                  <textarea
                    value={sigefGeoFilters}
                    onChange={(event) => setSigefGeoFilters(event.target.value)}
                    rows={8}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm font-mono text-xs"
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      if (!sigefGeoConfigured) {
                        setErrorMessage('SIGEF GEO (Conecta) não configurado')
                        return
                      }
                      try {
                        const parsed = JSON.parse(sigefGeoFilters)
                        sigefGeoMutation.mutate(parsed)
                      } catch (error) {
                        setErrorMessage('JSON inválido para filtros')
                      }
                    }}
                    disabled={sigefGeoMutation.isPending || !sigefGeoConfigured}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {sigefGeoMutation.isPending ? 'Consultando...' : 'Consultar'}
                  </button>
                  <button
                    onClick={() => {
                      if (!sigefGeoConfigured) {
                        setErrorMessage('SIGEF GEO (Conecta) não configurado')
                        return
                      }
                      try {
                        const parsed = JSON.parse(sigefGeoFilters)
                        sigefGeoGeojsonMutation.mutate(parsed)
                      } catch (error) {
                        setErrorMessage('JSON inválido para filtros')
                      }
                    }}
                    disabled={sigefGeoGeojsonMutation.isPending || !sigefGeoConfigured}
                    className="px-4 py-2 rounded-md text-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    {sigefGeoGeojsonMutation.isPending ? 'Consultando...' : 'GeoJSON'}
                  </button>
                </div>
              </div>
              {sigefGeoResult && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700">Resultado</h3>
                  <pre className="mt-2 text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                    {JSON.stringify(sigefGeoResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900">Consulta SICAR CPF/CNPJ</h2>
              <p className="text-sm text-gray-500 mt-1">
                Consulta imóveis no SICAR por CPF/CNPJ (Conecta).
              </p>
              <div className="mt-4 space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">CPF/CNPJ</label>
                  <input
                    value={sicarCpfCnpj}
                    onChange={(event) => setSicarCpfCnpj(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="01234567891"
                  />
                </div>
                <button
                  onClick={() => {
                    if (!sicarCpfCnpj) {
                      setErrorMessage('Informe o CPF/CNPJ')
                      return
                    }
                    sicarCpfCnpjMutation.mutate(sicarCpfCnpj)
                  }}
                  disabled={sicarCpfCnpjMutation.isPending}
                  className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                >
                  {sicarCpfCnpjMutation.isPending ? 'Consultando...' : 'Consultar'}
                </button>
              </div>
              {sicarResult && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700">Resultado</h3>
                  <pre className="mt-2 text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                    {JSON.stringify(sicarResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900">Consulta CNPJ</h2>
              <p className="text-sm text-gray-500 mt-1">
                Consulta básica, QSA ou empresa (Conecta).
              </p>
              <div className="mt-4 space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">CNPJ</label>
                  <input
                    value={cnpjValue}
                    onChange={(event) => setCnpjValue(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="00000000000000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">CPF do usuário (x-cpf-usuario)</label>
                  <input
                    value={cnpjCpfUsuario}
                    onChange={(event) => setCnpjCpfUsuario(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="00000000000"
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      if (!cnpjConfigured) {
                        setErrorMessage('CNPJ (Conecta) não configurado')
                        return
                      }
                      if (!cnpjValue || !cnpjCpfUsuario) {
                        setErrorMessage('Informe CNPJ e CPF do usuário')
                        return
                      }
                      cnpjBasicaMutation.mutate({ cnpj: cnpjValue, cpf_usuario: cnpjCpfUsuario })
                    }}
                    disabled={cnpjBasicaMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {cnpjBasicaMutation.isPending ? 'Consultando...' : 'Básica'}
                  </button>
                  <button
                    onClick={() => {
                      if (!cnpjConfigured) {
                        setErrorMessage('CNPJ (Conecta) não configurado')
                        return
                      }
                      if (!cnpjValue || !cnpjCpfUsuario) {
                        setErrorMessage('Informe CNPJ e CPF do usuário')
                        return
                      }
                      cnpjQsaMutation.mutate({ cnpj: cnpjValue, cpf_usuario: cnpjCpfUsuario })
                    }}
                    disabled={cnpjQsaMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {cnpjQsaMutation.isPending ? 'Consultando...' : 'QSA'}
                  </button>
                  <button
                    onClick={() => {
                      if (!cnpjConfigured) {
                        setErrorMessage('CNPJ (Conecta) não configurado')
                        return
                      }
                      if (!cnpjValue || !cnpjCpfUsuario) {
                        setErrorMessage('Informe CNPJ e CPF do usuário')
                        return
                      }
                      cnpjEmpresaMutation.mutate({ cnpj: cnpjValue, cpf_usuario: cnpjCpfUsuario })
                    }}
                    disabled={cnpjEmpresaMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {cnpjEmpresaMutation.isPending ? 'Consultando...' : 'Empresa'}
                  </button>
                </div>
              </div>
              {cnpjResult && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700">Resultado</h3>
                  <pre className="mt-2 text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                    {JSON.stringify(cnpjResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900">Consulta SNCCI</h2>
              <p className="text-sm text-gray-500 mt-1">
                Créditos de instalação e boletos (Conecta).
              </p>
              <div className="mt-4 space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Código do crédito</label>
                  <input
                    value={sncciCodigoCredito}
                    onChange={(event) => setSncciCodigoCredito(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="Código do crédito"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Código do beneficiário</label>
                  <input
                    value={sncciCodBeneficiario}
                    onChange={(event) => setSncciCodBeneficiario(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="Código do beneficiário"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Plano pagamento parcela</label>
                  <input
                    value={sncciCodPlanoParcela}
                    onChange={(event) => setSncciCodPlanoParcela(event.target.value)}
                    className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                    placeholder="cdPlanoPagamentoParcela"
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      if (!sncciCodigoCredito) {
                        setErrorMessage('Informe o código do crédito')
                        return
                      }
                      sncciParcelasMutation.mutate(sncciCodigoCredito)
                    }}
                    disabled={sncciParcelasMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {sncciParcelasMutation.isPending ? 'Consultando...' : 'Parcelas'}
                  </button>
                  <button
                    onClick={() => {
                      if (!sncciCodBeneficiario) {
                        setErrorMessage('Informe o código do beneficiário')
                        return
                      }
                      sncciCreditosAtivosMutation.mutate(sncciCodBeneficiario)
                    }}
                    disabled={sncciCreditosAtivosMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {sncciCreditosAtivosMutation.isPending ? 'Consultando...' : 'Créditos ativos'}
                  </button>
                  <button
                    onClick={() => {
                      if (!sncciCodigoCredito) {
                        setErrorMessage('Informe o código do crédito')
                        return
                      }
                      sncciCreditosMutation.mutate(sncciCodigoCredito)
                    }}
                    disabled={sncciCreditosMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-green-600 hover:bg-green-700"
                  >
                    {sncciCreditosMutation.isPending ? 'Consultando...' : 'Crédito por código'}
                  </button>
                  <button
                    onClick={() => {
                      if (!sncciCodPlanoParcela) {
                        setErrorMessage('Informe o código da parcela')
                        return
                      }
                      sncciBoletosMutation.mutate(sncciCodPlanoParcela)
                    }}
                    disabled={sncciBoletosMutation.isPending}
                    className="px-4 py-2 rounded-md text-sm text-white bg-blue-600 hover:bg-blue-700"
                  >
                    {sncciBoletosMutation.isPending ? 'Baixando...' : 'Baixar boleto'}
                  </button>
                </div>
              </div>
              {sncciBoletoStatus && (
                <div className="mt-3 text-sm text-green-700">{sncciBoletoStatus}</div>
              )}
              {sncciResult && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700">Resultado</h3>
                  <pre className="mt-2 text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                    {JSON.stringify(sncciResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>

          <LegalHistoryPanel legalQueries={legalQueries} />
        </div>
      )}

      {activeTab === 'ml' && investigation && (
        <InvestigationMlTab
          investigation={investigation}
          isLoadingPatterns={isLoadingPatterns}
          isLoadingRisk={isLoadingRisk}
          onAcknowledgeRiskReview={() => riskReviewMutation.mutate()}
          patterns={patterns}
          riskReviewSubmitting={riskReviewMutation.isPending}
          riskScore={riskScore}
        />
      )}

      {activeTab === 'network' && investigation && (
        <InvestigationNetworkTab
          isLoadingNetwork={isLoadingNetwork}
          networkAnalysis={networkAnalysis}
        />
      )}

      {activeTab === 'collaboration' && investigation && (
        <InvestigationCollaborationTab
          currentUserId={currentUserId}
          currentUserName={user?.full_name || user?.username || 'Você'}
          investigationId={Number(id)}
          onShare={() => setShareModalOpen(true)}
        />
      )}

      {/* Share Modal */}
      {investigation && (
        <ShareModal
          investigationId={investigation.id}
          investigationName={investigation.target_name}
          isOpen={shareModalOpen}
          onClose={() => setShareModalOpen(false)}
          canManageGuestLinks={
            !!user &&
            (investigation.user_id === user.id || user.is_superuser === true)
          }
        />
      )}
    </div>
  )
}
