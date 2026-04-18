import { api } from '@/lib/axios'

export type Organization = {
  id: number
  name: string
  slug: string
  description?: string | null
  risk_ai_human_review_required: boolean
  risk_ai_governance_reference_url?: string | null
}

export type OrganizationAIGovernancePatch = {
  risk_ai_human_review_required?: boolean
  risk_ai_governance_reference_url?: string | null
}

export const organizationService = {
  async listMine(): Promise<Organization[]> {
    const r = await api.get<Organization[]>('/organizations/me')
    return r.data
  },

  async patchAiGovernance(
    organizationId: number,
    body: OrganizationAIGovernancePatch
  ): Promise<Organization> {
    const r = await api.patch<Organization>(`/organizations/${organizationId}/ai-governance`, body)
    return r.data
  },
}
