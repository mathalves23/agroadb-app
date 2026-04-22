import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { organizationService } from '@/services/organizationService'
import { legalService } from '@/services/legalService'
import { integrations } from '@/pages/settings/catalog'
import {
  buildIntegrationCounts,
  filterIntegrationsByCategory,
  getIntegrationStatusLabel,
} from '@/pages/settings/utils'

export function useIntegrationSettings() {
  const queryClient = useQueryClient()
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'free' | 'key' | 'conecta'>('all')
  const [govOrgId, setGovOrgId] = useState<number | null>(null)
  const [govHumanReview, setGovHumanReview] = useState(false)
  const [govRefUrl, setGovRefUrl] = useState('')

  const { data: orgs = [] } = useQuery({
    queryKey: ['organizations-me'],
    queryFn: () => organizationService.listMine(),
  })

  useEffect(() => {
    if (!orgs.length) {
      setGovOrgId(null)
      return
    }

    const target = orgs.find((org) => org.id === govOrgId) ?? orgs[0]
    if (target.id !== govOrgId) {
      setGovOrgId(target.id)
    }
    setGovHumanReview(target.risk_ai_human_review_required)
    setGovRefUrl(target.risk_ai_governance_reference_url ?? '')
  }, [govOrgId, orgs])

  const govMutation = useMutation({
    mutationFn: () =>
      organizationService.patchAiGovernance(govOrgId!, {
        risk_ai_human_review_required: govHumanReview,
        risk_ai_governance_reference_url: govRefUrl.trim() || null,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['organizations-me'] })
    },
  })

  const integrationQuery = useQuery({
    queryKey: ['integration-status'],
    queryFn: () => legalService.getIntegrationStatus(),
    staleTime: 60_000,
  })

  const counts = useMemo(() => buildIntegrationCounts(integrations), [])
  const filteredIntegrations = useMemo(
    () => filterIntegrationsByCategory(integrations, selectedCategory),
    [selectedCategory]
  )

  return {
    counts,
    filteredIntegrations,
    getStatus: (name: string) => getIntegrationStatusLabel(integrationQuery.data, name),
    govHumanReview,
    govMutation,
    govOrgId,
    govRefUrl,
    integrationQuery,
    orgs,
    selectedCategory,
    setGovHumanReview,
    setGovOrgId,
    setGovRefUrl,
    setSelectedCategory,
  }
}
