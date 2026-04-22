import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { collaborationService } from '@/services/collaborationService'
import { investigationService } from '@/services/investigationService'

export function useInvestigationSharing(
  investigationId: number,
  canManageGuestLinks: boolean,
  enabled = true
) {
  const queryClient = useQueryClient()

  const sharedUsersQuery = useQuery({
    queryKey: ['investigation-shares', investigationId],
    queryFn: () => collaborationService.listShares(investigationId),
    enabled: enabled && investigationId > 0,
  })

  const guestLinksQuery = useQuery({
    queryKey: ['investigation-guest-links', investigationId],
    queryFn: async () => {
      const data = await investigationService.listGuestLinks(investigationId)
      return data.items
    },
    enabled: enabled && canManageGuestLinks && investigationId > 0,
  })

  const invalidate = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['investigation-shares', investigationId] }),
      queryClient.invalidateQueries({ queryKey: ['investigation-guest-links', investigationId] }),
    ])
  }

  const shareMutation = useMutation({
    mutationFn: (payload: { email: string; permission: 'view' | 'comment' | 'edit' | 'admin' }) =>
      collaborationService.shareInvestigation(investigationId, payload),
    onSuccess: () => void invalidate(),
  })

  const revokeShareMutation = useMutation({
    mutationFn: (sharedWithId: number) =>
      collaborationService.revokeShare(investigationId, sharedWithId),
    onSuccess: () => void invalidate(),
  })

  const createGuestLinkMutation = useMutation({
    mutationFn: (payload: {
      label?: string | null
      expires_at?: string | null
      allow_downloads?: boolean
    }) => collaborationService.createGuestLink(investigationId, payload),
    onSuccess: () => void invalidate(),
  })

  const revokeGuestLinkMutation = useMutation({
    mutationFn: (linkId: number) =>
      investigationService.revokeGuestLink(investigationId, linkId),
    onSuccess: () => void invalidate(),
  })

  return {
    sharedUsers: sharedUsersQuery.data ?? [],
    guestLinks: guestLinksQuery.data ?? [],
    isLoading:
      sharedUsersQuery.isLoading ||
      guestLinksQuery.isLoading ||
      shareMutation.isPending ||
      revokeShareMutation.isPending ||
      createGuestLinkMutation.isPending ||
      revokeGuestLinkMutation.isPending,
    shareInvestigation: shareMutation.mutateAsync,
    revokeShare: revokeShareMutation.mutateAsync,
    createGuestLink: createGuestLinkMutation.mutateAsync,
    revokeGuestLink: revokeGuestLinkMutation.mutateAsync,
    refresh: () => void invalidate(),
  }
}
