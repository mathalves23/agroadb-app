import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'

import { formatCPFCNPJ } from '@/lib/utils'
import {
  buildLegalCharts,
  createSummarySources,
} from '@/pages/investigationDetail/summary'
import type { InvestigationDetailTab } from '@/pages/investigationDetail/InvestigationTabs'
import { investigationService } from '@/services/investigationService'
import { legalService } from '@/services/legalService'

interface AxiosLikeError {
  response?: { data?: { detail?: string } }
  message?: string
}

function downloadBlob(blob: Blob, fileName: string) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

export function useInvestigationDetailData(id: string | undefined, activeTab: InvestigationDetailTab) {
  const queryClient = useQueryClient()
  const [dataJudResult, setDataJudResult] = useState<Record<string, unknown> | null>(null)
  const [sigefResult, setSigefResult] = useState<Record<string, unknown> | null>(null)
  const [sncrResult, setSncrResult] = useState<Record<string, unknown> | null>(null)
  const [sncrCcirStatus, setSncrCcirStatus] = useState<string | null>(null)
  const [sncciResult, setSncciResult] = useState<Record<string, unknown> | null>(null)
  const [sncciBoletoStatus, setSncciBoletoStatus] = useState<string | null>(null)
  const [sigefGeoResult, setSigefGeoResult] = useState<Record<string, unknown> | null>(null)
  const [sicarResult, setSicarResult] = useState<Record<string, unknown> | null>(null)
  const [cnpjResult, setCnpjResult] = useState<Record<string, unknown> | null>(null)
  const [cndResult, setCndResult] = useState<Record<string, unknown> | null>(null)
  const [cadinResult, setCadinResult] = useState<Record<string, unknown> | null>(null)
  const [portalServicosResult, setPortalServicosResult] = useState<Record<string, unknown> | null>(null)
  const [servicosEstaduaisResult, setServicosEstaduaisResult] = useState<Record<string, unknown> | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [sncrCodigo, setSncrCodigo] = useState('')
  const [sncrCpfCnpj, setSncrCpfCnpj] = useState('')
  const [sncciCodigoCredito, setSncciCodigoCredito] = useState('')
  const [sncciCodBeneficiario, setSncciCodBeneficiario] = useState('')
  const [sncciCodPlanoParcela, setSncciCodPlanoParcela] = useState('')
  const [sicarCpfCnpj, setSicarCpfCnpj] = useState('')
  const [sigefGeoFilters, setSigefGeoFilters] = useState(
    JSON.stringify(
      {
        parcelaCodigo: '',
        codigoImovel: '',
        detentorCpf: '',
        detentorCnpj: '',
        titularCpf: '',
        titularCnpj: '',
        municipio: '',
        uf: '',
        page: 0,
        size: 20,
      },
      null,
      2
    )
  )
  const [cnpjValue, setCnpjValue] = useState('')
  const [cnpjCpfUsuario, setCnpjCpfUsuario] = useState('')
  const [cndTipoContribuinte, setCndTipoContribuinte] = useState('1')
  const [cndContribuinteConsulta, setCndContribuinteConsulta] = useState('')
  const [cndCodigoIdentificacao, setCndCodigoIdentificacao] = useState('')
  const [cndGerarPdf, setCndGerarPdf] = useState(false)
  const [cndChave, setCndChave] = useState('')
  const [cadinCpf, setCadinCpf] = useState('')
  const [cadinCnpj, setCadinCnpj] = useState('')
  const [portalServicosOrgao, setPortalServicosOrgao] = useState('')
  const [portalServicosId, setPortalServicosId] = useState('')
  const [portalServicosToken, setPortalServicosToken] = useState('')
  const [servicosEstaduaisEmail, setServicosEstaduaisEmail] = useState('')
  const [servicosEstaduaisSenha, setServicosEstaduaisSenha] = useState('')
  const [servicosEstaduaisAuth, setServicosEstaduaisAuth] = useState('')
  const [servicosEstaduaisId, setServicosEstaduaisId] = useState('')
  const [servicosEstaduaisPayload, setServicosEstaduaisPayload] = useState(
    JSON.stringify(
      {
        uf: 'SP',
        idCategoria: '1',
        nomeServico: '',
        siglaServico: '',
        descricaoServico: '',
        statusServico: 'P',
        tagsServico: '',
        nomesPopulares: '',
        solicitanteServico: '',
        url: '',
        linkServicoDigital: '',
        cidade: '',
        contato: '',
        idServicoOrigem: '',
      },
      null,
      2
    )
  )
  const [autoEnrichDone, setAutoEnrichDone] = useState(false)
  const [quickScanRunning, setQuickScanRunning] = useState(false)
  const [quickScanProgress, setQuickScanProgress] = useState(0)
  const [quickScanTotal, setQuickScanTotal] = useState(0)
  const [quickScanLog, setQuickScanLog] = useState<string[]>([])
  const [exportLoading, setExportLoading] = useState(false)
  const summaryRef = useRef<HTMLDivElement>(null)

  const { data: investigation, isLoading } = useQuery({
    queryKey: ['investigation', id],
    queryFn: () => investigationService.get(Number(id)),
    enabled: !!id,
  })

  const { data: properties } = useQuery({
    queryKey: ['investigation-properties', id],
    queryFn: () => investigationService.getProperties(Number(id)),
    enabled: !!investigation && activeTab === 'summary',
  })

  const { data: companies } = useQuery({
    queryKey: ['investigation-companies', id],
    queryFn: () => investigationService.getCompanies(Number(id)),
    enabled: !!investigation && activeTab === 'summary',
  })

  const { data: legalQueries } = useQuery({
    queryKey: ['legal-queries', id],
    queryFn: () => legalService.listLegalQueries(Number(id)),
    enabled: !!id,
  })

  const { data: integrationStatus } = useQuery({
    queryKey: ['integration-status'],
    queryFn: () => legalService.getIntegrationStatus(),
  })

  const { data: riskScore, isLoading: isLoadingRisk } = useQuery({
    queryKey: ['risk-score', id],
    queryFn: () => investigationService.getRiskScore(Number(id)),
    enabled: !!id && activeTab === 'ml',
  })

  const { data: patterns, isLoading: isLoadingPatterns } = useQuery({
    queryKey: ['patterns', id],
    queryFn: () => investigationService.getPatterns(Number(id)),
    enabled: !!id && activeTab === 'ml',
  })

  const { data: networkAnalysis, isLoading: isLoadingNetwork } = useQuery({
    queryKey: ['network-analysis', id],
    queryFn: () => investigationService.getNetworkAnalysis(Number(id)),
    enabled: !!id && activeTab === 'network',
  })

  const defaultCpfCnpj = useMemo(() => investigation?.target_cpf_cnpj || '', [investigation])

  useEffect(() => {
    if (
      investigation?.id &&
      investigation?.target_cpf_cnpj &&
      !autoEnrichDone &&
      !investigation?.target_description?.includes('Receita Federal')
    ) {
      const name = investigation.target_name || ''
      const isAutoName = name.startsWith('Investigação ') || !name.trim()
      if (isAutoName) {
        setAutoEnrichDone(true)
        investigationService
          .enrich(investigation.id)
          .then(() => {
            void queryClient.invalidateQueries({ queryKey: ['investigation', String(investigation.id)] })
          })
          .catch(() => {})
      }
    }
  }, [
    autoEnrichDone,
    investigation?.id,
    investigation?.target_cpf_cnpj,
    investigation?.target_description,
    investigation?.target_name,
    queryClient,
  ])

  useEffect(() => {
    if (!defaultCpfCnpj) {
      return
    }

    setSncrCpfCnpj((value) => value || defaultCpfCnpj)
    setSicarCpfCnpj((value) => value || defaultCpfCnpj)
    setCnpjValue((value) => value || defaultCpfCnpj)
    setCndContribuinteConsulta((value) => value || defaultCpfCnpj)
    setCadinCpf((value) => value || defaultCpfCnpj)
  }, [defaultCpfCnpj])

  const summaryCpfCnpj = useMemo(() => {
    const raw =
      sicarCpfCnpj ||
      sncrCpfCnpj ||
      cadinCpf ||
      cadinCnpj ||
      cnpjValue ||
      cndContribuinteConsulta ||
      defaultCpfCnpj

    return raw ? formatCPFCNPJ(raw) : ''
  }, [
    cadinCnpj,
    cadinCpf,
    cndContribuinteConsulta,
    cnpjValue,
    defaultCpfCnpj,
    sicarCpfCnpj,
    sncrCpfCnpj,
  ])

  const summarySources = useMemo(
    () =>
      createSummarySources({
        dataJudResult,
        cnpjResult,
        cadinResult,
        sncrResult,
        sigefResult,
        sigefGeoResult,
        sicarResult,
        cndResult,
      }),
    [
      cadinResult,
      cndResult,
      cnpjResult,
      dataJudResult,
      sicarResult,
      sigefGeoResult,
      sigefResult,
      sncrResult,
    ]
  )

  const summarySourcesWithData = useMemo(
    () => summarySources.filter((source) => source.result),
    [summarySources]
  )

  const totalQueries = legalQueries?.length ?? 0
  const totalResults = useMemo(
    () => (legalQueries ?? []).reduce((accumulator, item) => accumulator + (item.result_count || 0), 0),
    [legalQueries]
  )

  const latestQuery = useMemo(() => {
    if (!legalQueries || legalQueries.length === 0) {
      return null
    }

    return legalQueries.reduce((latest, current) => {
      if (!latest) {
        return current
      }

      return new Date(current.created_at) > new Date(latest.created_at) ? current : latest
    }, legalQueries[0])
  }, [legalQueries])

  const applyCpfCnpjToForms = useCallback(() => {
    if (!defaultCpfCnpj) {
      return
    }

    setSncrCpfCnpj(defaultCpfCnpj)
    setSicarCpfCnpj(defaultCpfCnpj)
    setCadinCpf(defaultCpfCnpj)
    setCadinCnpj(defaultCpfCnpj)
    setCnpjValue(defaultCpfCnpj)
    setCndContribuinteConsulta(defaultCpfCnpj)
  }, [defaultCpfCnpj])

  const runQuickScan = useCallback(async () => {
    if (!defaultCpfCnpj || quickScanRunning || !id) {
      return
    }

    setQuickScanRunning(true)
    setQuickScanLog([])
    setErrorMessage(null)
    const doc = defaultCpfCnpj.replace(/\D/g, '')
    const isCpf = doc.length <= 11

    type ScanTask = {
      label: string
      fn: () => Promise<unknown>
      setter: (data: Record<string, unknown>) => void
    }

    const tasks: ScanTask[] = [
      {
        label: 'SNCR (CPF/CNPJ)',
        fn: () => legalService.conectaSncrCpfCnpj({ cpf_cnpj: doc, investigation_id: Number(id) }),
        setter: (data) => setSncrResult(data),
      },
      {
        label: 'SICAR (CPF/CNPJ)',
        fn: () => legalService.conectaSicarCpfCnpj({ cpf_cnpj: doc, investigation_id: Number(id) }),
        setter: (data) => setSicarResult(data),
      },
      {
        label: isCpf ? 'CADIN (CPF)' : 'CADIN (CNPJ)',
        fn: () =>
          isCpf
            ? legalService.conectaCadinInfoCpf({ cpf: doc, investigation_id: Number(id) })
            : legalService.conectaCadinInfoCnpj({ cnpj: doc, investigation_id: Number(id) }),
        setter: (data) => setCadinResult(data),
      },
      {
        label: 'CND (Certidão)',
        fn: () =>
          legalService.conectaCndCertidao({
            tipoContribuinte: isCpf ? 1 : 2,
            contribuinteConsulta: doc,
            codigoIdentificacao: '',
            investigation_id: Number(id),
          }),
        setter: (data) => setCndResult(data),
      },
    ]

    if (!isCpf) {
      tasks.push(
        {
          label: 'CNPJ (Receita)',
          fn: () => legalService.conectaCnpjBasica({ cnpj: doc, cpf_usuario: '', investigation_id: Number(id) }),
          setter: (data) => setCnpjResult(data),
        },
        {
          label: 'CNPJ (BrasilAPI)',
          fn: () => legalService.brasilApiCnpj({ cnpj: doc, investigation_id: Number(id) }),
          setter: () => {},
        },
        {
          label: 'CNPJ (ReceitaWS)',
          fn: () => legalService.redesimCnpj({ cnpj: doc, investigation_id: Number(id) }),
          setter: () => {},
        },
        {
          label: 'CVM (Fundos)',
          fn: () => legalService.cvmFundos({ cnpj: doc, investigation_id: Number(id) }),
          setter: () => {},
        },
        {
          label: 'CVM (FII)',
          fn: () => legalService.cvmFii({ cnpj: doc, investigation_id: Number(id) }),
          setter: () => {},
        },
        {
          label: 'Caixa FGTS (CRF)',
          fn: () => legalService.caixaFgtsConsultar({ cnpj: doc, investigation_id: Number(id) }),
          setter: () => {},
        }
      )
    }

    if (doc.length === 11) {
      tasks.push({
        label: 'BNMP/CNJ (Mandados)',
        fn: () => legalService.bnmpConsultar({ cpf: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
    } else if (investigation?.target_name) {
      tasks.push({
        label: 'BNMP/CNJ (Mandados)',
        fn: () => legalService.bnmpConsultar({ nome: investigation.target_name, investigation_id: Number(id) }),
        setter: () => {},
      })
    }

    if (doc.length === 11) {
      tasks.push({
        label: 'SEEU/CNJ (Execução Penal)',
        fn: () => legalService.seeuConsultar({ cpf: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
    } else if (doc.length === 14) {
      tasks.push({
        label: 'SEEU/CNJ (Execução Penal)',
        fn: () => legalService.seeuConsultar({ cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
    } else if (investigation?.target_name) {
      tasks.push({
        label: 'SEEU/CNJ (Execução Penal)',
        fn: () => legalService.seeuConsultar({ nome_parte: investigation.target_name, investigation_id: Number(id) }),
        setter: () => {},
      })
    }

    if (doc.length === 11) {
      tasks.push({
        label: 'SIGEF Público (Parcelas)',
        fn: () => legalService.sigefPublicoParcelas({ cpf: doc, paginas: 5, investigation_id: Number(id) }),
        setter: () => {},
      })
    } else if (doc.length === 14) {
      tasks.push({
        label: 'SIGEF Público (Parcelas)',
        fn: () => legalService.sigefPublicoParcelas({ cnpj: doc, paginas: 5, investigation_id: Number(id) }),
        setter: () => {},
      })
    }

    if (doc.length === 11) {
      tasks.push({
        label: 'Receita Federal (CPF)',
        fn: () => legalService.receitaCpfConsultar({ cpf: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
    }

    if (doc.length === 14) {
      tasks.push({
        label: 'Receita Federal (CNPJ)',
        fn: () => legalService.receitaCnpjConsultar({ cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
    }

    tasks.push(
      {
        label: 'Transparência (Sanções)',
        fn: () => legalService.transparenciaSancoes({ cpf_cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      },
      {
        label: 'Transparência (Contratos)',
        fn: () => legalService.transparenciaContratos({ cpf_cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      },
      {
        label: 'Transparência (Servidores)',
        fn: () => legalService.transparenciaServidores({ cpf_cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      },
      {
        label: 'Transparência (Benefícios)',
        fn: () => legalService.transparenciaBeneficios({ cpf_cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      },
      {
        label: 'TSE (Candidatos)',
        fn: () => legalService.tseBuscar({ query: investigation?.target_name || doc, investigation_id: Number(id) }),
        setter: () => {},
      },
      {
        label: isCpf ? 'TJMG (CPF)' : 'TJMG (CNPJ)',
        fn: () =>
          legalService.tjmgProcessos({
            ...(isCpf ? { cpf: doc } : { cnpj: doc }),
            investigation_id: Number(id),
          }),
        setter: () => {},
      }
    )

    setQuickScanTotal(tasks.length)
    setQuickScanProgress(0)

    for (let index = 0; index < tasks.length; index += 1) {
      const task = tasks[index]
      setQuickScanLog((current) => [...current, `Consultando ${task.label}...`])
      try {
        const result = await task.fn()
        task.setter(result as Record<string, unknown>)
        setQuickScanLog((current) => [...current, `✓ ${task.label} — dados recebidos`])
      } catch (error) {
        const axiosError = error as AxiosLikeError
        const rawDetail = axiosError?.response?.data?.detail
        let message: string

        if (rawDetail && typeof rawDetail === 'object') {
          message =
            ((rawDetail as Record<string, unknown>).detail as string) ||
            ((rawDetail as Record<string, unknown>).message as string) ||
            JSON.stringify(rawDetail)
        } else if (typeof rawDetail === 'string') {
          message = rawDetail
        } else {
          message = axiosError?.message || 'Erro desconhecido'
        }

        if (message.includes('credentials_missing') || message.includes('Credenciais')) {
          const credentialMatch = message.match(/"detail"\s*:\s*"([^"]+)"/)
          message = credentialMatch ? credentialMatch[1] : 'Credenciais não configuradas'
        }

        setQuickScanLog((current) => [...current, `✗ ${task.label} — ${message}`])
      }

      setQuickScanProgress(index + 1)
    }

    void queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })
    setQuickScanLog((current) => [...current, 'Enriquecendo investigação com dados cadastrais...'])

    try {
      await investigationService.enrich(Number(id))
      void queryClient.invalidateQueries({ queryKey: ['investigation', id] })
      setQuickScanLog((current) => [...current, '✓ Dados cadastrais importados para a investigação'])
    } catch {
      setQuickScanLog((current) => [...current, '⚠ Enriquecimento parcial — alguns dados não disponíveis'])
    }

    setQuickScanRunning(false)
  }, [defaultCpfCnpj, id, investigation, queryClient, quickScanRunning])

  const { chartByProvider, chartByDate, pieData } = useMemo(
    () => buildLegalCharts(legalQueries),
    [legalQueries]
  )

  const exportPDF = useCallback(async () => {
    if (!id) {
      return
    }

    setExportLoading(true)
    try {
      const blob = await investigationService.exportPDF(Number(id))
      downloadBlob(
        blob,
        `relatorio_${investigation?.target_name?.replace(/\s/g, '_') || id}_${new Date().toISOString().slice(0, 10)}.pdf`
      )
    } catch (error) {
      const axiosError = error as AxiosLikeError
      setErrorMessage(axiosError?.response?.data?.detail || 'Erro ao exportar PDF')
    } finally {
      setExportLoading(false)
    }
  }, [id, investigation])

  const handleExportExcel = useCallback(async () => {
    if (!id) {
      return
    }

    setExportLoading(true)
    try {
      const blob = await investigationService.exportExcel(Number(id))
      downloadBlob(
        blob,
        `investigacao_${investigation?.target_name?.replace(/\s/g, '_') || id}_${new Date().toISOString().slice(0, 10)}.xlsx`
      )
    } catch (error) {
      const axiosError = error as AxiosLikeError
      setErrorMessage(axiosError?.response?.data?.detail || 'Erro ao exportar para Excel')
    } finally {
      setExportLoading(false)
    }
  }, [id, investigation])

  const handleExportCSV = useCallback(async () => {
    if (!id) {
      return
    }

    setExportLoading(true)
    try {
      const blob = await investigationService.exportCSV(Number(id))
      downloadBlob(
        blob,
        `investigacao_${investigation?.target_name?.replace(/\s/g, '_') || id}_${new Date().toISOString().slice(0, 10)}.csv`
      )
    } catch (error) {
      const axiosError = error as AxiosLikeError
      setErrorMessage(axiosError?.response?.data?.detail || 'Erro ao exportar para CSV')
    } finally {
      setExportLoading(false)
    }
  }, [id, investigation])

  const exportTrustBundle = useCallback(async () => {
    if (!id) {
      return
    }

    setExportLoading(true)
    try {
      const blob = await investigationService.exportTrustBundle(Number(id))
      downloadBlob(
        blob,
        `agroadb_evidencia_inv_${id}_${(investigation?.target_name || 'investigacao').replace(/\s/g, '_').slice(0, 60)}_${new Date().toISOString().slice(0, 10)}.zip`
      )
    } catch (error) {
      const axiosError = error as AxiosLikeError
      setErrorMessage(axiosError?.response?.data?.detail || 'Erro ao gerar pacote de evidência')
    } finally {
      setExportLoading(false)
    }
  }, [id, investigation])

  return {
    cnpjResult,
    companies,
    dataJudResult,
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
    properties,
    quickScanLog,
    quickScanProgress,
    quickScanRunning,
    quickScanTotal,
    riskScore,
    servicosEstaduaisResult,
    setServicosEstaduaisResult,
    setPortalServicosResult,
    portalServicosResult,
    summaryCpfCnpj,
    summaryRef,
    summarySources,
    summarySourcesWithData,
    totalQueries,
    totalResults,
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
    cnpjValue,
    defaultCpfCnpj,
    runQuickScan,
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
    setSicarCpfCnpj,
    setSicarResult,
    setServicosEstaduaisAuth,
    setServicosEstaduaisEmail,
    setServicosEstaduaisId,
    setServicosEstaduaisPayload,
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
    setPortalServicosId,
    setPortalServicosToken,
    setPortalServicosOrgao,
    sicarCpfCnpj,
    sicarResult,
    servicosEstaduaisAuth,
    servicosEstaduaisEmail,
    servicosEstaduaisId,
    servicosEstaduaisPayload,
    servicosEstaduaisSenha,
    sigefGeoFilters,
    sigefGeoResult,
    sigefResult,
    sncciBoletoStatus,
    sncciCodBeneficiario,
    sncciCodPlanoParcela,
    sncciCodigoCredito,
    sncciResult,
    sncrCcirStatus,
    sncrCodigo,
    sncrCpfCnpj,
    sncrResult,
    portalServicosId,
    portalServicosOrgao,
    portalServicosToken,
  }
}
