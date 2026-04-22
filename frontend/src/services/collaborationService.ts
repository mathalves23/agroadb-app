import { api } from '@/lib/axios'
import { runOfflineCapableMutation } from '@/lib/offlineQueue'
import type { GuestLinkPublic } from '@/services/investigationService'

export interface InvestigationComment {
  id: number
  user_id: number
  user_name: string
  content: string
  is_internal: boolean
  is_edited: boolean
  parent_id?: number
  created_at: string
  updated_at: string
}

export interface SharedInvestigationUser {
  id: number
  shared_with_id: number
  shared_with_email: string
  shared_with_name: string
  permission: 'view' | 'comment' | 'edit' | 'admin'
  created_at: string
}

export interface ChangeLogEntry {
  id: number
  user_id: number
  user_name: string
  user_email?: string
  action: string
  field_changed?: string
  old_value?: unknown
  new_value?: unknown
  description?: string
  timestamp: string
}

type ListCommentsResponse = {
  total: number
  comments: InvestigationComment[]
}

type SaveCommentPayload = {
  content: string
  is_internal: boolean
  parent_id?: number
}

type ListSharesResponse = {
  shares: SharedInvestigationUser[]
}

type ListChangeLogResponse = {
  changelog: ChangeLogEntry[]
}

export const collaborationService = {
  async listComments(investigationId: number) {
    const response = await api.get<ListCommentsResponse>(
      `/collaboration/investigations/${investigationId}/comments`
    )
    return response.data.comments
  },

  async addComment(investigationId: number, payload: SaveCommentPayload) {
    return runOfflineCapableMutation(
      'comment.add',
      { investigationId, ...payload },
      async () => {
        const response = await api.post<{ comment: InvestigationComment }>(
          `/collaboration/investigations/${investigationId}/comments`,
          payload
        )
        return response.data.comment
      }
    )
  },

  async updateComment(commentId: number, content: string) {
    return runOfflineCapableMutation(
      'comment.update',
      { commentId, content },
      async () => {
        const response = await api.put<{ comment: InvestigationComment }>(
          `/collaboration/comments/${commentId}`,
          { content }
        )
        return response.data.comment
      }
    )
  },

  async deleteComment(commentId: number) {
    return runOfflineCapableMutation(
      'comment.delete',
      { commentId },
      async () => {
        await api.delete(`/collaboration/comments/${commentId}`)
      }
    )
  },

  async listShares(investigationId: number) {
    const response = await api.get<ListSharesResponse>(
      `/collaboration/investigations/${investigationId}/shares`
    )
    return response.data.shares
  },

  async shareInvestigation(
    investigationId: number,
    payload: { email: string; permission: 'view' | 'comment' | 'edit' | 'admin' }
  ) {
    const response = await api.post(
      `/collaboration/investigations/${investigationId}/share`,
      payload
    )
    return response.data
  },

  async revokeShare(investigationId: number, sharedWithId: number) {
    await api.delete(`/collaboration/investigations/${investigationId}/shares/${sharedWithId}`)
  },

  async listChangeLog(investigationId: number) {
    const response = await api.get<ListChangeLogResponse>(
      `/collaboration/investigations/${investigationId}/changelog`
    )
    return response.data.changelog
  },

  buildAbsoluteGuestUrl(guestViewPath: string): string {
    const base = (import.meta.env.BASE_URL || '/').replace(/\/+/g, '/')
    const prefix =
      base === '/' || base === '' ? '' : base.endsWith('/') ? base.slice(0, -1) : base
    const path = guestViewPath.startsWith('/') ? guestViewPath : `/${guestViewPath}`
    return `${window.location.origin}${prefix}${path}`
  },

  async createGuestLink(
    investigationId: number,
    payload: { label?: string | null; expires_at?: string | null; allow_downloads?: boolean }
  ) {
    return api
      .post<{ token: string; link: GuestLinkPublic; guest_view_path: string }>(
        `/investigations/${investigationId}/guest-links`,
        payload
      )
      .then((response) => response.data)
  },
}
