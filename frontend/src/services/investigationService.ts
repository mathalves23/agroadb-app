import { api } from '@/lib/axios'
import type {
  Investigation,
  InvestigationCreate,
  InvestigationListResponse,
  Property,
  LeaseContract,
  Company,
  DashboardStatistics,
} from '@/types/api'

export const investigationService = {
  async create(data: InvestigationCreate): Promise<Investigation> {
    const response = await api.post<Investigation>('/investigations', data)
    return response.data
  },

  async list(page: number = 1, pageSize: number = 20): Promise<InvestigationListResponse> {
    const response = await api.get<InvestigationListResponse>('/investigations', {
      params: { page, page_size: pageSize },
    })
    return response.data
  },

  async getDashboardStatistics(): Promise<DashboardStatistics> {
    const response = await api.get<DashboardStatistics>('/investigations/dashboard-statistics')
    return response.data
  },

  async get(id: number): Promise<Investigation> {
    const response = await api.get<Investigation>(`/investigations/${id}`)
    return response.data
  },

  async acknowledgeRiskScoreReview(id: number): Promise<Investigation> {
    const response = await api.post<Investigation>(`/investigations/${id}/risk-score-review`)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/investigations/${id}`)
  },

  async getProperties(id: number): Promise<Property[]> {
    const response = await api.get<Property[]>(`/investigations/${id}/properties`)
    return response.data
  },

  async getLeaseContracts(id: number): Promise<LeaseContract[]> {
    const response = await api.get<LeaseContract[]>(`/investigations/${id}/lease-contracts`)
    return response.data
  },

  async getCompanies(id: number): Promise<Company[]> {
    const response = await api.get<Company[]>(`/investigations/${id}/companies`)
    return response.data
  },

  async enrich(id: number): Promise<Investigation> {
    const response = await api.post<Investigation>(`/investigations/${id}/enrich`)
    return response.data
  },

  async update(id: number, data: Partial<Investigation>): Promise<Investigation> {
    const response = await api.patch<Investigation>(`/investigations/${id}`, data)
    return response.data
  },

  async listCursor(params?: { cursor?: string; limit?: number; status?: string; order?: string }): Promise<{
    items: Investigation[]
    next_cursor: string | null
    previous_cursor: string | null
    has_next: boolean
    has_previous: boolean
    page_size: number
    total_count: number | null
  }> {
    const response = await api.get('/investigations/cursor', { params })
    return response.data
  },

  async exportExcel(id: number): Promise<Blob> {
    const response = await api.get(`/investigations/${id}/export/excel`, {
      responseType: 'blob',
    })
    return response.data
  },

  async exportCSV(id: number): Promise<Blob> {
    const response = await api.get(`/investigations/${id}/export/csv`, {
      responseType: 'blob',
    })
    return response.data
  },

  async exportPDF(id: number): Promise<Blob> {
    const response = await api.get(`/investigations/${id}/export/pdf`, {
      responseType: 'blob',
    })
    return response.data
  },

  /** ZIP: PDF + manifest.json + README (pacote de evidência / RFPs). */
  async exportTrustBundle(id: number): Promise<Blob> {
    const response = await api.get(`/investigations/${id}/export/trust-bundle`, {
      responseType: 'blob',
    })
    return response.data
  },

  // Machine Learning (payload dinâmico conforme modelo)
  async getRiskScore(id: number): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>(`/investigations/${id}/risk-score`)
    return response.data
  },

  async getPatterns(id: number): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>(`/investigations/${id}/patterns`)
    return response.data
  },

  async getNetworkAnalysis(id: number): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>(`/investigations/${id}/network`)
    return response.data
  },

  async getComprehensiveAnalysis(id: number): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>(`/investigations/${id}/comprehensive-analysis`)
    return response.data
  },

  /** Leitura pública via token (sem JWT). */
  async getGuestInvestigation(token: string): Promise<Record<string, unknown>> {
    const response = await api.get<Record<string, unknown>>('/public/guest/investigation', {
      params: { token },
    })
    return response.data
  },

  async exportGuestInvestigationPdf(token: string): Promise<Blob> {
    const response = await api.get('/public/guest/investigation/export/pdf', {
      params: { token },
      responseType: 'blob',
    })
    return response.data
  },

  async createGuestLink(
    investigationId: number,
    body: { expires_at?: string | null; label?: string | null; allow_downloads?: boolean }
  ): Promise<{ token: string; link: Record<string, unknown>; guest_view_path: string }> {
    const response = await api.post(`/investigations/${investigationId}/guest-links`, body)
    return response.data
  },

  async listGuestLinks(investigationId: number): Promise<{ items: GuestLinkPublic[] }> {
    const response = await api.get<{ items: GuestLinkPublic[] }>(
      `/investigations/${investigationId}/guest-links`
    )
    return response.data
  },

  async revokeGuestLink(investigationId: number, linkId: number): Promise<void> {
    await api.delete(`/investigations/${investigationId}/guest-links/${linkId}`)
  },
}

export type GuestLinkPublic = {
  id: number
  investigation_id: number
  label: string | null
  expires_at: string | null
  revoked_at: string | null
  allow_downloads: boolean
  access_count: number
  last_access_at: string | null
  created_at: string | null
}
