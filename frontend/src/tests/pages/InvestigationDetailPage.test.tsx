import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import InvestigationDetailPage from '@/pages/InvestigationDetailPage'

jest.mock('@/stores/authStore', () => ({
  useAuthStore: (selector: (state: { user: { id: number; is_superuser: boolean } }) => unknown) =>
    selector({ user: { id: 1, is_superuser: false } }),
}))

jest.mock('@/services/investigationService', () => ({
  investigationService: {
    get: jest.fn(),
    getProperties: jest.fn().mockResolvedValue([]),
    getCompanies: jest.fn().mockResolvedValue([]),
    getRiskScore: jest.fn().mockResolvedValue(null),
    getPatterns: jest.fn().mockResolvedValue([]),
    getNetworkAnalysis: jest.fn().mockResolvedValue({ nodes: [], edges: [] }),
    acknowledgeRiskScoreReview: jest.fn().mockResolvedValue({}),
    enrich: jest.fn().mockResolvedValue({}),
    exportPDF: jest.fn(),
    exportExcel: jest.fn(),
    exportCSV: jest.fn(),
    exportTrustBundle: jest.fn(),
  },
}))

jest.mock('@/services/legalService', () => ({
  legalService: {
    listLegalQueries: jest.fn().mockResolvedValue([]),
    getIntegrationStatus: jest.fn().mockResolvedValue({
      datajud: { configured: true, api_url: '' },
      sigef_parcelas: { configured: true, api_url: '' },
      conecta: {},
    }),
  },
}))

jest.mock('@/components/ShareModal', () => ({
  __esModule: true,
  default: () => null,
}))

jest.mock('@/components/CommentThread', () => ({
  __esModule: true,
  default: () => <div>Comentários</div>,
}))

jest.mock('@/components/ChangeLog', () => ({
  __esModule: true,
  default: () => <div>Histórico de mudanças</div>,
}))

jest.mock('@/components/investigation', () => ({
  InvestigationHeader: () => <div>Header da investigação</div>,
  EnrichedDataCard: () => <div>Dados enriquecidos</div>,
  QuickScanPanel: () => <div>Painel de varredura</div>,
  KpiCards: () => <div>KPIs</div>,
  DossierSummary: () => <div>Dossiê</div>,
  QueryCharts: () => <div>Gráficos</div>,
  PropertiesList: () => <div>Propriedades</div>,
  CompaniesList: () => <div>Empresas</div>,
  NetworkGraph: () => <div>Rede</div>,
  RiskScoreCard: () => <div>Score de risco</div>,
  PatternDetectionCard: () => <div>Padrões</div>,
}))

const { investigationService } = jest.requireMock('@/services/investigationService')

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/investigations/1']}>
        <Routes>
          <Route path="/investigations/:id" element={<InvestigationDetailPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('InvestigationDetailPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders empty state when investigation is missing', async () => {
    investigationService.get.mockResolvedValue(null)
    renderPage()

    await waitFor(() => {
      expect(screen.getByText(/investigação não encontrada/i)).toBeInTheDocument()
    })
  })

  it('renders tabs and summary content', async () => {
    investigationService.get.mockResolvedValue({
      id: 1,
      user_id: 1,
      target_name: 'Joao Teste',
      target_cpf_cnpj: '12345678900',
      target_description: 'Resumo inicial',
      status: 'pending',
      priority: 3,
      properties_found: 0,
      lease_contracts_found: 0,
      companies_found: 0,
      created_at: '2026-04-22T10:00:00Z',
      updated_at: '2026-04-22T10:00:00Z',
      can_acknowledge_risk_score_review: false,
    })

    renderPage()

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /resumo/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /consultas legais/i })).toBeInTheDocument()
      expect(screen.getByText(/nenhum dado encontrado ainda/i)).toBeInTheDocument()
    })
  })
})
