import { useEffect, useMemo, useState, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  Search,
  Scale,
  Database,
  XCircle,
  Network as NetworkIcon,
  Brain,
  AlertTriangle,
  Users,
  MessageSquare,
  History as HistoryIcon,
  Share2,
} from 'lucide-react'
import { investigationService } from '@/services/investigationService'
import { legalService } from '@/services/legalService'
import { LegalQueriesTab } from '@/components/legal/LegalQueriesTab'
import {
  InvestigationHeader,
  EnrichedDataCard,
  QuickScanPanel,
  KpiCards,
  DossierSummary,
  QueryCharts,
  PropertiesList,
  CompaniesList,
  NetworkGraph,
  RiskScoreCard,
  PatternDetectionCard,
} from '@/components/investigation'
import ShareModal from '@/components/ShareModal'
import CommentThread from '@/components/CommentThread'
import ChangeLog from '@/components/ChangeLog'
import { formatDate, formatDateTime, formatCPFCNPJ } from '@/lib/utils'

interface AxiosLikeError {
  response?: { data?: { detail?: string } }
  message?: string
}

export default function InvestigationDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'summary' | 'legal' | 'network' | 'ml' | 'collaboration'>('summary')
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
        parcelaCodigo: "",
        codigoImovel: "",
        detentorCpf: "",
        detentorCnpj: "",
        titularCpf: "",
        titularCnpj: "",
        municipio: "",
        uf: "",
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
        uf: "SP",
        idCategoria: "1",
        nomeServico: "",
        siglaServico: "",
        descricaoServico: "",
        statusServico: "P",
        tagsServico: "",
        nomesPopulares: "",
        solicitanteServico: "",
        url: "",
        linkServicoDigital: "",
        cidade: "",
        contato: "",
        idServicoOrigem: "",
      },
      null,
      2
    )
  )

  // Collaboration states
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);

  // Get current user ID from localStorage or auth context
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setCurrentUserId(payload.user_id || payload.sub || null);
      } catch (e) {
        console.error('Failed to parse token', e);
      }
    }
  }, []);

  const formatSummaryValue = (value: unknown): string => {
    if (value === null || value === undefined) {
      return ''
    }
    if (typeof value === 'string') {
      return value
    }
    if (typeof value === 'number' || typeof value === 'boolean') {
      return String(value)
    }
    if (Array.isArray(value)) {
      const preview: string[] = value
        .slice(0, 3)
        .map((item) => formatSummaryValue(item))
        .filter((item) => Boolean(item))
      return preview.length ? `${preview.join(' | ')}${value.length > 3 ? ' ...' : ''}` : ''
    }
    if (typeof value === 'object') {
      const keys = Object.keys(value as Record<string, unknown>)
      return keys.length ? `(${keys.slice(0, 4).join(', ')}${keys.length > 4 ? ', ...' : ''})` : ''
    }
    return String(value)
  }

  const findValueByKeys = (
    payload: unknown,
    keys: string[],
    depth = 0,
    visited = new Set<unknown>()
  ): unknown => {
    if (!payload || typeof payload !== 'object') {
      return undefined
    }
    if (visited.has(payload)) {
      return undefined
    }
    visited.add(payload)
    const obj = payload as Record<string, unknown>
    const lowerKeys = Object.keys(obj).reduce<Record<string, string>>((acc, key) => {
      acc[key.toLowerCase()] = key
      return acc
    }, {})
    for (const key of keys) {
      const normalized = key.toLowerCase()
      const realKey = lowerKeys[normalized]
      if (realKey !== undefined) {
        return obj[realKey]
      }
    }
    if (depth > 4) {
      return undefined
    }
    for (const value of Object.values(obj)) {
      if (typeof value === 'object' && value !== null) {
        const found = findValueByKeys(value, keys, depth + 1, visited)
        if (found !== undefined) {
          return found
        }
      }
    }
    return undefined
  }

  const { data: investigation, isLoading } = useQuery({
    queryKey: ['investigation', id],
    queryFn: () => investigationService.get(Number(id)),
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

  // ML & Network Analysis
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

  const defaultCpfCnpj = useMemo(() => investigation?.target_cpf_cnpj || '', [investigation])

  // Auto-enrich: se a investigação tem CPF/CNPJ mas nome auto-gerado e sem descrição enriquecida
  const [autoEnrichDone, setAutoEnrichDone] = useState(false)
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
        investigationService.enrich(investigation.id).then(() => {
          queryClient.invalidateQueries({ queryKey: ['investigation', String(investigation.id)] })
        }).catch(() => {})
      }
    }
  }, [investigation?.id, investigation?.target_cpf_cnpj, investigation?.target_name, investigation?.target_description, autoEnrichDone, queryClient])

  useEffect(() => {
    if (defaultCpfCnpj) {
      if (!sncrCpfCnpj) setSncrCpfCnpj(defaultCpfCnpj)
      if (!sicarCpfCnpj) setSicarCpfCnpj(defaultCpfCnpj)
      if (!cnpjValue) setCnpjValue(defaultCpfCnpj)
      if (!cndContribuinteConsulta) setCndContribuinteConsulta(defaultCpfCnpj)
      if (!cadinCpf) setCadinCpf(defaultCpfCnpj)
    }
  }, [defaultCpfCnpj]) // eslint-disable-line react-hooks/exhaustive-deps

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
    sicarCpfCnpj,
    sncrCpfCnpj,
    cadinCpf,
    cadinCnpj,
    cnpjValue,
    cndContribuinteConsulta,
    defaultCpfCnpj,
  ])

  const buildSummaryFields = (
    result: Record<string, unknown> | null,
    fields: Array<{ label: string; keys: string[] }>
  ) => {
    if (!result) {
      return []
    }
    return fields
      .map((field) => {
        const value = findValueByKeys(result, field.keys)
        const formatted = formatSummaryValue(value)
        return formatted ? { label: field.label, value: formatted } : null
      })
      .filter(Boolean) as Array<{ label: string; value: string }>
  }

  const summarySources = useMemo(
    () => [
      {
        label: 'DataJud',
        result: dataJudResult,
        fields: [
          { label: 'Processos', keys: ['hits', 'processos'] },
          { label: 'Total', keys: ['total'] },
        ],
      },
      {
        label: 'CNPJ (Conecta)',
        result: cnpjResult,
        fields: [
          { label: 'Razão social', keys: ['razaoSocial', 'razao_social', 'nomeEmpresarial', 'nome'] },
          { label: 'Nome fantasia', keys: ['nomeFantasia', 'nome_fantasia'] },
          { label: 'Situação', keys: ['situacao', 'situacaoCadastral', 'status'] },
          { label: 'Atividade', keys: ['atividadePrincipal', 'cnaePrincipal', 'cnae'] },
          { label: 'Endereço', keys: ['endereco', 'logradouro', 'enderecoCompleto'] },
          { label: 'Municipio/UF', keys: ['municipio', 'cidade', 'uf', 'estado'] },
        ],
      },
      {
        label: 'CADIN (Conecta)',
        result: cadinResult,
        fields: [
          { label: 'Situação', keys: ['situacao', 'status', 'possuiRestricao'] },
          { label: 'Órgão', keys: ['orgao', 'orgaoResponsavel'] },
          { label: 'Data', keys: ['data', 'dataRegistro', 'dataAtualizacao'] },
          { label: 'Descrição', keys: ['descricao', 'motivo'] },
        ],
      },
      {
        label: 'SNCR (Conecta)',
        result: sncrResult,
        fields: [
          { label: 'Código imóvel', keys: ['codigoImovel', 'codigo_imovel', 'imovel'] },
          { label: 'Nome imóvel', keys: ['nomeImovel', 'nome_imovel'] },
          { label: 'Situação', keys: ['situacao', 'status'] },
          { label: 'Área (ha)', keys: ['areaHa', 'area_ha', 'area'] },
          { label: 'Município/UF', keys: ['municipio', 'uf', 'estado'] },
        ],
      },
      {
        label: 'SIGEF Parcelas',
        result: sigefResult,
        fields: [
          { label: 'Resultado', keys: ['resultados', 'resultados_retornados'] },
          { label: 'Área (ha)', keys: ['area_ha', 'areaHa', 'area'] },
          { label: 'Matrícula', keys: ['matricula'] },
          { label: 'Detentor', keys: ['detentor', 'nome'] },
        ],
      },
      {
        label: 'SIGEF GEO (Conecta)',
        result: sigefGeoResult,
        fields: [
          { label: 'Código parcela', keys: ['parcelaCodigo', 'codigo_parcela'] },
          { label: 'Código imóvel', keys: ['codigoImovel', 'codigo_imovel'] },
          { label: 'Situação', keys: ['status', 'situacao'] },
          { label: 'Área (ha)', keys: ['areaHa', 'area_ha', 'area'] },
        ],
      },
      {
        label: 'SICAR (Conecta)',
        result: sicarResult,
        fields: [
          { label: 'Situação', keys: ['situacao', 'status'] },
          { label: 'Imóvel', keys: ['imovel', 'codigoImovel', 'codigo_imovel'] },
          { label: 'Município/UF', keys: ['municipio', 'uf', 'estado'] },
        ],
      },
      {
        label: 'CND (Conecta)',
        result: cndResult,
        fields: [
          { label: 'Situação', keys: ['situacao', 'status', 'resultado'] },
          { label: 'Validade', keys: ['validade', 'dataValidade'] },
          { label: 'Emitente', keys: ['orgao', 'emissor'] },
        ],
      },
    ],
    [dataJudResult, cnpjResult, cadinResult, sncrResult, sigefResult, sigefGeoResult, sicarResult, cndResult]
  )

  const summarySourcesWithData = useMemo(
    () => summarySources.filter((source) => source.result),
    [summarySources]
  )

  const totalQueries = legalQueries?.length ?? 0
  const totalResults = useMemo(
    () => (legalQueries ?? []).reduce((acc, item) => acc + (item.result_count || 0), 0),
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

  const applyCpfCnpjToForms = () => {
    if (!defaultCpfCnpj) {
      return
    }
    setSncrCpfCnpj(defaultCpfCnpj)
    setSicarCpfCnpj(defaultCpfCnpj)
    setCadinCpf(defaultCpfCnpj)
    setCadinCnpj(defaultCpfCnpj)
    setCnpjValue(defaultCpfCnpj)
    setCndContribuinteConsulta(defaultCpfCnpj)
  }

  // ─── Quick Scan ───
  const [quickScanRunning, setQuickScanRunning] = useState(false)
  const [quickScanProgress, setQuickScanProgress] = useState(0)
  const [quickScanTotal, setQuickScanTotal] = useState(0)
  const [quickScanLog, setQuickScanLog] = useState<string[]>([])

  const runQuickScan = useCallback(async () => {
    if (!defaultCpfCnpj || quickScanRunning) return
    setQuickScanRunning(true)
    setQuickScanLog([])
    setErrorMessage(null)
    const doc = defaultCpfCnpj.replace(/\D/g, '')
    const isCpf = doc.length <= 11

    type ScanTask = { label: string; fn: () => Promise<unknown>; setter: (d: Record<string, unknown>) => void }
    const tasks: ScanTask[] = [
      {
        label: 'SNCR (CPF/CNPJ)',
        fn: () => legalService.conectaSncrCpfCnpj({ cpf_cnpj: doc, investigation_id: Number(id) }),
        setter: (d) => setSncrResult(d),
      },
      {
        label: 'SICAR (CPF/CNPJ)',
        fn: () => legalService.conectaSicarCpfCnpj({ cpf_cnpj: doc, investigation_id: Number(id) }),
        setter: (d) => setSicarResult(d),
      },
      {
        label: isCpf ? 'CADIN (CPF)' : 'CADIN (CNPJ)',
        fn: () =>
          isCpf
            ? legalService.conectaCadinInfoCpf({ cpf: doc, investigation_id: Number(id) })
            : legalService.conectaCadinInfoCnpj({ cnpj: doc, investigation_id: Number(id) }),
        setter: (d) => setCadinResult(d),
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
        setter: (d) => setCndResult(d),
      },
    ]
    if (!isCpf) {
      tasks.push({
        label: 'CNPJ (Receita)',
        fn: () => legalService.conectaCnpjBasica({ cnpj: doc, cpf_usuario: '', investigation_id: Number(id) }),
        setter: (d) => setCnpjResult(d),
      })
      tasks.push({
        label: 'CNPJ (BrasilAPI)',
        fn: () => legalService.brasilApiCnpj({ cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
      tasks.push({
        label: 'CNPJ (ReceitaWS)',
        fn: () => legalService.redesimCnpj({ cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
      tasks.push({
        label: 'CVM (Fundos)',
        fn: () => legalService.cvmFundos({ cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
      tasks.push({
        label: 'CVM (FII)',
        fn: () => legalService.cvmFii({ cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
      tasks.push({
        label: 'Caixa FGTS (CRF)',
        fn: () => legalService.caixaFgtsConsultar({ cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
    }

    // BNMP — Mandados de Prisão (CNJ)
    if (doc && doc.replace(/\D/g, '').length === 11) {
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

    // SEEU — Execução Penal (CNJ)
    if (doc && doc.replace(/\D/g, '').length === 11) {
      tasks.push({
        label: 'SEEU/CNJ (Execução Penal)',
        fn: () => legalService.seeuConsultar({ cpf: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
    } else if (doc && doc.replace(/\D/g, '').length === 14) {
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

    // SIGEF Público — Parcelas INCRA (consulta direta, até 5 páginas)
    if (doc && doc.replace(/\D/g, '').length === 11) {
      tasks.push({
        label: 'SIGEF Público (Parcelas)',
        fn: () => legalService.sigefPublicoParcelas({ cpf: doc, paginas: 5, investigation_id: Number(id) }),
        setter: () => {},
      })
    } else if (doc && doc.replace(/\D/g, '').length === 14) {
      tasks.push({
        label: 'SIGEF Público (Parcelas)',
        fn: () => legalService.sigefPublicoParcelas({ cnpj: doc, paginas: 5, investigation_id: Number(id) }),
        setter: () => {},
      })
    }

    // Receita Federal — Situação Cadastral CPF
    if (doc && doc.replace(/\D/g, '').length === 11) {
      tasks.push({
        label: 'Receita Federal (CPF)',
        fn: () => legalService.receitaCpfConsultar({ cpf: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
    }

    // Receita Federal — Dados Cadastrais CNPJ
    if (doc && doc.replace(/\D/g, '').length === 14) {
      tasks.push({
        label: 'Receita Federal (CNPJ)',
        fn: () => legalService.receitaCnpjConsultar({ cnpj: doc, investigation_id: Number(id) }),
        setter: () => {},
      })
    }

    // APIs gratuitas para CPF e CNPJ
    tasks.push({
      label: 'Transparência (Sanções)',
      fn: () => legalService.transparenciaSancoes({ cpf_cnpj: doc, investigation_id: Number(id) }),
      setter: () => {},
    })
    tasks.push({
      label: 'Transparência (Contratos)',
      fn: () => legalService.transparenciaContratos({ cpf_cnpj: doc, investigation_id: Number(id) }),
      setter: () => {},
    })
    tasks.push({
      label: 'Transparência (Servidores)',
      fn: () => legalService.transparenciaServidores({ cpf_cnpj: doc, investigation_id: Number(id) }),
      setter: () => {},
    })
    tasks.push({
      label: 'Transparência (Benefícios)',
      fn: () => legalService.transparenciaBeneficios({ cpf_cnpj: doc, investigation_id: Number(id) }),
      setter: () => {},
    })
    tasks.push({
      label: 'TSE (Candidatos)',
      fn: () => legalService.tseBuscar({ query: investigation?.target_name || doc, investigation_id: Number(id) }),
      setter: () => {},
    })
    tasks.push({
      label: isCpf ? 'TJMG (CPF)' : 'TJMG (CNPJ)',
      fn: () =>
        legalService.tjmgProcessos({
          ...(isCpf ? { cpf: doc } : { cnpj: doc }),
          investigation_id: Number(id),
        }),
      setter: () => {},
    })

    setQuickScanTotal(tasks.length)
    setQuickScanProgress(0)

    for (let i = 0; i < tasks.length; i++) {
      const task = tasks[i]
      setQuickScanLog((prev) => [...prev, `Consultando ${task.label}...`])
      try {
        const result = await task.fn()
        task.setter(result as Record<string, unknown>)
        setQuickScanLog((prev) => [...prev, `✓ ${task.label} — dados recebidos`])
      } catch (err: unknown) {
        const axiosErr = err as AxiosLikeError
        const rawDetail = axiosErr?.response?.data?.detail
        let msg: string
        if (rawDetail && typeof rawDetail === 'object') {
          msg = (rawDetail as Record<string, unknown>).detail as string
            || (rawDetail as Record<string, unknown>).message as string
            || JSON.stringify(rawDetail)
        } else if (typeof rawDetail === 'string') {
          msg = rawDetail
        } else {
          msg = axiosErr?.message || 'Erro desconhecido'
        }
        // Simplify credential-missing messages
        if (msg.includes('credentials_missing') || msg.includes('Credenciais')) {
          const credMatch = msg.match(/"detail"\s*:\s*"([^"]+)"/)
          msg = credMatch ? credMatch[1] : 'Credenciais não configuradas'
        }
        setQuickScanLog((prev) => [...prev, `✗ ${task.label} — ${msg}`])
      }
      setQuickScanProgress(i + 1)
    }

    queryClient.invalidateQueries({ queryKey: ['legal-queries', id] })

    // Enriquecer investigação com dados cadastrais (nome, nascimento, situação)
    setQuickScanLog((prev) => [...prev, 'Enriquecendo investigação com dados cadastrais...'])
    try {
      await investigationService.enrich(Number(id))
      queryClient.invalidateQueries({ queryKey: ['investigation', id] })
      setQuickScanLog((prev) => [...prev, '✓ Dados cadastrais importados para a investigação'])
    } catch {
      setQuickScanLog((prev) => [...prev, '⚠ Enriquecimento parcial — alguns dados não disponíveis'])
    }

    setQuickScanRunning(false)
  }, [defaultCpfCnpj, quickScanRunning, id, queryClient, investigation])

  // ─── Chart Data ───
  const chartByProvider = useMemo(() => {
    if (!legalQueries || legalQueries.length === 0) return []
    const grouped: Record<string, { queries: number; results: number }> = {}
    for (const q of legalQueries) {
      if (!grouped[q.provider]) grouped[q.provider] = { queries: 0, results: 0 }
      grouped[q.provider].queries += 1
      grouped[q.provider].results += q.result_count || 0
    }
    return Object.entries(grouped).map(([provider, data]) => ({
      name: provider,
      consultas: data.queries,
      resultados: data.results,
    }))
  }, [legalQueries])

  const chartByDate = useMemo(() => {
    if (!legalQueries || legalQueries.length === 0) return []
    const grouped: Record<string, number> = {}
    for (const q of legalQueries) {
      const day = new Date(q.created_at).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
      grouped[day] = (grouped[day] || 0) + 1
    }
    return Object.entries(grouped)
      .slice(-14)
      .map(([date, count]) => ({ date, consultas: count }))
  }, [legalQueries])

  const pieData = useMemo(() => {
    if (!legalQueries || legalQueries.length === 0) return []
    const grouped: Record<string, number> = {}
    for (const q of legalQueries) {
      grouped[q.provider] = (grouped[q.provider] || 0) + 1
    }
    return Object.entries(grouped).map(([name, value]) => ({ name, value }))
  }, [legalQueries])

  // ─── PDF Export ───
  const summaryRef = useRef<HTMLDivElement>(null)

  const exportPDF = useCallback(async () => {
    if (!id) return
    setExportLoading(true)
    try {
      const blob = await investigationService.exportPDF(Number(id))
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `relatorio_${investigation?.target_name?.replace(/\s/g, '_') || id}_${new Date().toISOString().slice(0, 10)}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      const axiosErr = err as AxiosLikeError
      setErrorMessage(axiosErr?.response?.data?.detail || 'Erro ao exportar PDF')
    } finally {
      setExportLoading(false)
    }
  }, [id, investigation])

  // ─── Excel/CSV Export ───
  const [exportLoading, setExportLoading] = useState(false)

  const handleExportExcel = useCallback(async () => {
    if (!id) return
    setExportLoading(true)
    try {
      const blob = await investigationService.exportExcel(Number(id))
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `investigacao_${investigation?.target_name?.replace(/\s/g, '_') || id}_${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      const axiosErr = err as AxiosLikeError
      setErrorMessage(axiosErr?.response?.data?.detail || 'Erro ao exportar para Excel')
    } finally {
      setExportLoading(false)
    }
  }, [id, investigation])

  const handleExportCSV = useCallback(async () => {
    if (!id) return
    setExportLoading(true)
    try {
      const blob = await investigationService.exportCSV(Number(id))
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `investigacao_${investigation?.target_name?.replace(/\s/g, '_') || id}_${new Date().toISOString().slice(0, 10)}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      const axiosErr = err as AxiosLikeError
      setErrorMessage(axiosErr?.response?.data?.detail || 'Erro ao exportar para CSV')
    } finally {
      setExportLoading(false)
    }
  }, [id, investigation])

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
    return <div className="p-8 text-center">Carregando...</div>
  }

  if (!investigation) {
    return <div className="p-8 text-center">Investigação não encontrada</div>
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

      {/* Tabs */}
      <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-xl w-fit">
        <button
          onClick={() => setActiveTab('summary')}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === 'summary'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <span className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            Resumo
          </span>
        </button>
        <button
          onClick={() => setActiveTab('legal')}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === 'legal'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <span className="flex items-center gap-2">
            <Scale className="h-4 w-4" />
            Consultas Legais
          </span>
        </button>
        <button
          onClick={() => setActiveTab('network')}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === 'network'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <span className="flex items-center gap-2">
            <NetworkIcon className="h-4 w-4" />
            Rede
          </span>
        </button>
        <button
          onClick={() => setActiveTab('ml')}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === 'ml'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <span className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            Análise ML
          </span>
        </button>
        <button
          onClick={() => setActiveTab('collaboration')}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === 'collaboration'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <span className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Colaboração
          </span>
        </button>
      </div>

      {activeTab === 'summary' && (
        <div className="space-y-6" ref={summaryRef}>
          <QuickScanPanel
            running={quickScanRunning}
            progress={quickScanProgress}
            total={quickScanTotal}
            log={quickScanLog}
            disabled={!defaultCpfCnpj}
            onRunScan={runQuickScan}
            onExportPDF={exportPDF}
            onExportExcel={handleExportExcel}
            onExportCSV={handleExportCSV}
            exportLoading={exportLoading}
          />

          <KpiCards
            propertiesFound={investigation.properties_found}
            leaseContractsFound={investigation.lease_contracts_found}
            companiesFound={investigation.companies_found}
            totalQueries={totalQueries}
            sourcesWithDataCount={summarySourcesWithData.length}
            totalResults={totalResults}
          />

          <DossierSummary
            summaryCpfCnpj={summaryCpfCnpj}
            defaultCpfCnpj={defaultCpfCnpj}
            targetName={investigation.target_name}
            summarySources={summarySources}
            latestQuery={latestQuery}
            onApplyCpfCnpj={applyCpfCnpjToForms}
            buildSummaryFields={buildSummaryFields}
          />

          {legalQueries && legalQueries.length > 0 && (
            <QueryCharts
              chartByProvider={chartByProvider}
              pieData={pieData}
              chartByDate={chartByDate}
            />
          )}

          {properties && properties.length > 0 && (
            <PropertiesList properties={properties} />
          )}

          {companies && companies.length > 0 && (
            <CompaniesList companies={companies} />
          )}

          {/* Consultas Legais registradas (histórico) */}
          {legalQueries && legalQueries.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-3">
                <div className="bg-indigo-500 rounded-lg p-2">
                  <Scale className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-gray-900">Histórico de Consultas</h2>
                  <p className="text-xs text-gray-500">{legalQueries.length} consulta{legalQueries.length === 1 ? '' : 's'} realizada{legalQueries.length === 1 ? '' : 's'}</p>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100">
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provedor</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Resultados</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Data</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {legalQueries.slice(0, 20).map((query) => (
                      <tr key={query.id} className="hover:bg-gray-50/50 transition">
                        <td className="px-6 py-3">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-indigo-50 text-indigo-700">
                            {query.provider}
                          </span>
                        </td>
                        <td className="px-6 py-3 text-xs text-gray-700">{query.query_type}</td>
                        <td className="px-6 py-3 text-xs text-right font-medium text-gray-900">{query.result_count}</td>
                        <td className="px-6 py-3 text-xs text-right text-gray-500">{formatDateTime(query.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Estado vazio */}
          {(!properties || properties.length === 0) && (!companies || companies.length === 0) && (!legalQueries || legalQueries.length === 0) && summarySourcesWithData.length === 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
              <Search className="mx-auto h-12 w-12 text-gray-300" />
              <h3 className="mt-4 text-base font-medium text-gray-900">Nenhum dado encontrado ainda</h3>
              <p className="mt-2 text-sm text-gray-500">
                Acesse a aba <button onClick={() => setActiveTab('legal')} className="text-indigo-600 font-medium hover:underline">Consultas Legais</button> para pesquisar nas bases governamentais.
              </p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'legal' && (
        <div className="space-y-6">
          {/* Config warnings — compact */}
          {(() => {
            const warnings: string[] = []
            if (!dataJudConfigured) warnings.push('DataJud')
            if (!sigefConfigured) warnings.push('SIGEF Parcelas')
            if (!sncrConfigured) warnings.push('SNCR')
            if (!sncciConfigured) warnings.push('SNCCI')
            if (!sigefGeoConfigured) warnings.push('SIGEF GEO')
            if (!cnpjConfigured) warnings.push('CNPJ')
            if (!cndConfigured) warnings.push('CND')
            if (!cadinConfigured) warnings.push('CADIN')
            if (!portalServicosConfigured) warnings.push('Portal Serviços')
            if (!servicosEstaduaisConfigured) warnings.push('Serv. Estaduais')
            if (warnings.length === 0) return null
            return (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
                <div className="bg-amber-100 rounded-lg p-1.5 shrink-0 mt-0.5">
                  <Database className="h-4 w-4 text-amber-600" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-amber-800">Bases sem credencial configurada</p>
                  <div className="mt-1.5 flex flex-wrap gap-1.5">
                    {warnings.map((w) => (
                      <span key={w} className="px-2 py-0.5 rounded-md bg-amber-100 text-[10px] font-medium text-amber-700">{w}</span>
                    ))}
                  </div>
                  <p className="mt-1.5 text-[10px] text-amber-600">Configure as API keys no arquivo .env do backend para habilitar essas bases.</p>
                </div>
              </div>
            )
          })()}
          {errorMessage && (
            <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-xl p-3">
              <XCircle className="h-4 w-4 text-red-500 shrink-0" />
              <p className="text-xs text-red-700">{errorMessage}</p>
              <button onClick={() => setErrorMessage(null)} className="ml-auto text-red-400 hover:text-red-600 text-xs font-medium">Fechar</button>
            </div>
          )}

          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <h2 className="text-lg font-medium text-gray-900">Resumo do CPF/CNPJ</h2>
                <p className="text-sm text-gray-500">
                  Consolidação das bases consultadas para o documento pesquisado.
                </p>
              </div>
              <div className="text-sm text-gray-700 flex flex-col gap-2 items-start md:items-end">
                <div>
                  <span className="text-gray-500">Documento:</span>
                  <span className="ml-2 font-medium">{summaryCpfCnpj || 'Não informado'}</span>
                </div>
                <button
                  onClick={applyCpfCnpjToForms}
                  disabled={!defaultCpfCnpj}
                  className={`px-3 py-1 rounded-md text-xs ${
                    defaultCpfCnpj
                      ? 'bg-emerald-600 text-white hover:bg-emerald-700'
                      : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  Usar CPF/CNPJ da investigação
                </button>
              </div>
            </div>
            <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs text-gray-500">Consultas registradas</p>
                <p className="text-2xl font-semibold text-gray-900">{totalQueries}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs text-gray-500">Bases com dados</p>
                <p className="text-2xl font-semibold text-gray-900">{summarySourcesWithData.length}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs text-gray-500">Resultados totais</p>
                <p className="text-2xl font-semibold text-gray-900">{totalResults}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs text-gray-500">Última consulta</p>
                <p className="text-sm font-medium text-gray-900">
                  {latestQuery ? formatDate(latestQuery.created_at) : '—'}
                </p>
                {latestQuery && (
                  <p className="text-xs text-gray-500">
                    {latestQuery.provider} • {latestQuery.query_type}
                  </p>
                )}
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {summarySources.map((source) => (
                <span
                  key={source.label}
                  className={`px-3 py-1 rounded-full text-xs ${
                    source.result ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'
                  }`}
                >
                  {source.label}
                </span>
              ))}
            </div>
            <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {summarySources.map((source) => {
                const fields = buildSummaryFields(source.result, source.fields)
                return (
                  <div key={source.label} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-gray-900">{source.label}</h3>
                      <span
                        className={`text-xs px-2 py-1 rounded-full ${
                          source.result ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                        }`}
                      >
                        {source.result ? 'Com dados' : 'Sem dados'}
                      </span>
                    </div>
                    {source.result ? (
                      fields.length ? (
                        <div className="mt-3 space-y-2">
                          {fields.map((field) => (
                            <div key={`${source.label}-${field.label}`} className="text-xs text-gray-700">
                              <span className="text-gray-500">{field.label}:</span>
                              <span className="ml-2 font-medium text-gray-900">{field.value}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="mt-3 text-xs text-gray-500">
                          Dados retornados. Veja o JSON completo abaixo.
                        </div>
                      )
                    ) : (
                      <div className="mt-3 text-xs text-gray-500">
                        Nenhum retorno registrado para esta base.
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
            {summarySourcesWithData.length > 0 && (
              <div className="mt-4 text-xs text-gray-500">
                Bases com retorno: {summarySourcesWithData.map((source) => source.label).join(', ')}
              </div>
            )}
          </div>

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

          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Histórico de Consultas</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {legalQueries && legalQueries.length > 0 ? (
                legalQueries.map((query) => (
                  <div key={query.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {query.provider} • {query.query_type}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(query.created_at).toLocaleString('pt-BR')}
                        </p>
                      </div>
                      <span className="text-sm text-gray-600">
                        {query.result_count} resultados
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="px-6 py-4 text-sm text-gray-500">
                  Nenhuma consulta registrada para esta investigação.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'collaboration' && investigation && (
        <div className="space-y-6">
          {/* Header com botão de compartilhar */}
          <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2">Colaboração e Histórico</h2>
                <p className="text-indigo-100">
                  Compartilhe a investigação, adicione comentários e acompanhe todas as alterações
                </p>
              </div>
              <button
                onClick={() => setShareModalOpen(true)}
                className="flex items-center gap-2 px-5 py-3 bg-white text-indigo-600 rounded-lg font-semibold hover:bg-indigo-50 transition shadow-lg"
              >
                <Share2 className="h-5 w-5" />
                Compartilhar
              </button>
            </div>
          </div>

          {/* Stats de Colaboração */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-3">
                <div className="bg-purple-100 rounded-lg p-3">
                  <Share2 className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Compartilhamentos</p>
                  <p className="text-2xl font-bold text-gray-900">-</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-3">
                <div className="bg-cyan-100 rounded-lg p-3">
                  <MessageSquare className="h-6 w-6 text-cyan-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Comentários</p>
                  <p className="text-2xl font-bold text-gray-900">-</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center gap-3">
                <div className="bg-indigo-100 rounded-lg p-3">
                  <HistoryIcon className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Alterações</p>
                  <p className="text-2xl font-bold text-gray-900">-</p>
                </div>
              </div>
            </div>
          </div>

          {/* Comments Section */}
          {currentUserId && (
            <CommentThread
              investigationId={Number(id)}
              currentUserId={currentUserId}
            />
          )}

          {/* Change Log Section */}
          <ChangeLog investigationId={Number(id)} />
        </div>
      )}

      {/* Share Modal */}
      {investigation && (
        <ShareModal
          investigationId={investigation.id}
          investigationName={investigation.target_name}
          isOpen={shareModalOpen}
          onClose={() => setShareModalOpen(false)}
        />
      )}
    </div>
  )
}
