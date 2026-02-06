import { api } from '@/lib/axios'
import type {
  Investigation,
  InvestigationCreate,
  InvestigationListResponse,
  Property,
  LeaseContract,
  Company,
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

  async get(id: number): Promise<Investigation> {
    const response = await api.get<Investigation>(`/investigations/${id}`)
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

  // Machine Learning
  async getRiskScore(id: number): Promise<any> {
    const response = await api.get(`/investigations/${id}/risk-score`)
    return response.data
  },

  async getPatterns(id: number): Promise<any> {
    const response = await api.get(`/investigations/${id}/patterns`)
    return response.data
  },

  async getNetworkAnalysis(id: number): Promise<any> {
    const response = await api.get(`/investigations/${id}/network`)
    return response.data
  },

  async getComprehensiveAnalysis(id: number): Promise<any> {
    const response = await api.get(`/investigations/${id}/comprehensive-analysis`)
    return response.data
  },
}
