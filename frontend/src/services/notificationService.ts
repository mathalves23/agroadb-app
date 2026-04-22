import { api } from '@/lib/axios'

export interface NotificationItem {
  id: number
  type: string
  title: string
  message: string
  priority: string
  action_url?: string
  icon?: string
  color?: string
  investigation_id?: number
  is_read: boolean
  is_archived?: boolean
  read_at?: string
  created_at: string
}

export const notificationService = {
  async list(params?: {
    includeRead?: boolean
    includeArchived?: boolean
    limit?: number
    offset?: number
  }): Promise<NotificationItem[]> {
    const response = await api.get<NotificationItem[]>('/notifications/', {
      params: {
        include_read: params?.includeRead ?? true,
        include_archived: params?.includeArchived ?? false,
        limit: params?.limit ?? 50,
        offset: params?.offset ?? 0,
      },
    })
    return response.data
  },

  async getUnreadCount(): Promise<number> {
    const response = await api.get<{ count: number }>('/notifications/unread/count')
    return response.data.count
  },

  async markAsRead(notificationId: number): Promise<void> {
    await api.patch(`/notifications/${notificationId}/read`)
  },

  async markAllAsRead(): Promise<void> {
    await api.post('/notifications/read-all')
  },

  async delete(notificationId: number): Promise<void> {
    await api.delete(`/notifications/${notificationId}`)
  },
}
