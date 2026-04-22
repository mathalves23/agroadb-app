import { useQuery } from '@tanstack/react-query'

import { collaborationService } from '@/services/collaborationService'

export function useChangeLog(investigationId: number) {
  return useQuery({
    queryKey: ['investigation-changelog', investigationId],
    queryFn: () => collaborationService.listChangeLog(investigationId),
    enabled: investigationId > 0,
  })
}
