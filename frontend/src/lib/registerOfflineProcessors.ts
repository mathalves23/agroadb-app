import { api } from '@/lib/axios'
import { registerOfflineProcessor } from '@/lib/offlineQueue'

let registered = false

export function registerOfflineProcessors() {
  if (registered) return
  registered = true

  registerOfflineProcessor('notification.mark-read', async (payload) => {
    await api.patch(`/notifications/${payload.notificationId}/read`)
  })

  registerOfflineProcessor('notification.mark-all-read', async () => {
    await api.post('/notifications/read-all')
  })

  registerOfflineProcessor('notification.delete', async (payload) => {
    await api.delete(`/notifications/${payload.notificationId}`)
  })

  registerOfflineProcessor('comment.add', async (payload) => {
    await api.post(`/collaboration/investigations/${payload.investigationId}/comments`, {
      content: payload.content,
      is_internal: payload.is_internal,
      parent_id: payload.parent_id,
    })
  })

  registerOfflineProcessor('comment.update', async (payload) => {
    await api.put(`/collaboration/comments/${payload.commentId}`, {
      content: payload.content,
    })
  })

  registerOfflineProcessor('comment.delete', async (payload) => {
    await api.delete(`/collaboration/comments/${payload.commentId}`)
  })
}
