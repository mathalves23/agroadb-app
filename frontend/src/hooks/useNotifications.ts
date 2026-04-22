import { useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import logger from '@/lib/logger'
import {
  notificationService,
  type NotificationItem,
} from '@/services/notificationService'

type NotificationFilter = 'all' | 'unread' | 'read'

export function useNotifications(options?: {
  limit?: number
  includeRead?: boolean
  pollUnreadCount?: boolean
  filter?: NotificationFilter
}) {
  const queryClient = useQueryClient()
  const filter = options?.filter ?? 'all'
  const includeRead = options?.includeRead ?? filter !== 'unread'
  const limit = options?.limit ?? 50

  const notificationsQuery = useQuery({
    queryKey: ['notifications', { limit, includeRead }],
    queryFn: () => notificationService.list({ limit, includeRead }),
  })

  const unreadCountQuery = useQuery({
    queryKey: ['notifications', 'unread-count'],
    queryFn: () => notificationService.getUnreadCount(),
    refetchInterval: options?.pollUnreadCount ? 30_000 : false,
  })

  const invalidateNotifications = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['notifications'] }),
      queryClient.invalidateQueries({ queryKey: ['notifications', 'unread-count'] }),
    ])
  }

  const markAsReadMutation = useMutation({
    mutationFn: (notificationId: number) => notificationService.markAsRead(notificationId),
    onSuccess: () => void invalidateNotifications(),
    onError: (error) => {
      logger.warn('Falha ao marcar notificacao como lida', error, 'useNotifications')
    },
  })

  const markAllAsReadMutation = useMutation({
    mutationFn: () => notificationService.markAllAsRead(),
    onSuccess: () => void invalidateNotifications(),
    onError: (error) => {
      logger.warn('Falha ao marcar todas notificacoes como lidas', error, 'useNotifications')
    },
  })

  const deleteNotificationMutation = useMutation({
    mutationFn: (notificationId: number) => notificationService.delete(notificationId),
    onSuccess: () => void invalidateNotifications(),
    onError: (error) => {
      logger.warn('Falha ao deletar notificacao', error, 'useNotifications')
    },
  })

  const notifications = useMemo(() => {
    const items = notificationsQuery.data ?? []
    if (filter === 'read') {
      return items.filter((item) => item.is_read)
    }
    if (filter === 'unread') {
      return items.filter((item) => !item.is_read)
    }
    return items
  }, [filter, notificationsQuery.data])

  const unreadCount = useMemo(() => {
    if (typeof unreadCountQuery.data === 'number') {
      return unreadCountQuery.data
    }
    return notifications.filter((notification) => !notification.is_read).length
  }, [notifications, unreadCountQuery.data])

  const syncNotificationList = (
    updater: (current: NotificationItem[]) => NotificationItem[]
  ) => {
    queryClient.setQueriesData<NotificationItem[]>(
      { queryKey: ['notifications'] },
      (current) => updater(current ?? [])
    )
  }

  return {
    notifications,
    unreadCount,
    isLoading: notificationsQuery.isLoading,
    isRefreshing:
      notificationsQuery.isFetching ||
      unreadCountQuery.isFetching ||
      markAsReadMutation.isPending ||
      markAllAsReadMutation.isPending ||
      deleteNotificationMutation.isPending,
    refresh: () => void invalidateNotifications(),
    markAsRead: async (notificationId: number) => {
      await markAsReadMutation.mutateAsync(notificationId)
      syncNotificationList((current) =>
        current.map((notification) =>
          notification.id === notificationId ? { ...notification, is_read: true } : notification
        )
      )
    },
    markAllAsRead: async () => {
      await markAllAsReadMutation.mutateAsync()
      syncNotificationList((current) =>
        current.map((notification) => ({ ...notification, is_read: true }))
      )
    },
    deleteNotification: async (notificationId: number) => {
      await deleteNotificationMutation.mutateAsync(notificationId)
      syncNotificationList((current) =>
        current.filter((notification) => notification.id !== notificationId)
      )
    },
  }
}
