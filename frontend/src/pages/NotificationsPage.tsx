import { useState, useEffect, useCallback } from 'react'
import { Bell, Check, CheckCheck, Trash2, Filter, RefreshCw } from 'lucide-react'
import { Link } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { PanelListLoader } from '@/components/Loading'
import { EmptyState } from '@/components/EmptyState'
import logger from '@/lib/logger'
import {
  notificationService,
  type NotificationItem as Notification,
} from '@/services/notificationService'

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all')
  const [loading, setLoading] = useState(true)

  const loadNotifications = useCallback(async () => {
    setLoading(true)
    try {
      const includeRead = filter !== 'unread'
      const data = await notificationService.list({ limit: 100, includeRead })
      let filtered = data
      if (filter === 'read') {
        filtered = data.filter((n) => n.is_read)
      } else if (filter === 'unread') {
        filtered = data.filter((n) => !n.is_read)
      }
      setNotifications(filtered)
    } catch (error) {
      logger.warn('Falha ao carregar pagina de notificacoes', error, 'NotificationsPage')
    } finally {
      setLoading(false)
    }
  }, [filter])

  useEffect(() => {
    void loadNotifications()
  }, [loadNotifications])

  const markAsRead = async (id: number) => {
    try {
      await notificationService.markAsRead(id)
      await loadNotifications()
    } catch (error) {
      logger.warn('Falha ao marcar notificacao como lida', error, 'NotificationsPage')
    }
  }

  const markAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead()
      await loadNotifications()
    } catch (error) {
      logger.warn('Falha ao marcar todas notificacoes como lidas', error, 'NotificationsPage')
    }
  }

  const deleteNotification = async (id: number) => {
    try {
      await notificationService.delete(id)
      await loadNotifications()
    } catch (error) {
      logger.warn('Falha ao deletar notificacao', error, 'NotificationsPage')
    }
  }

  const getColorClass = (color: string) => {
    const colorMap: Record<string, string> = {
      blue: 'bg-blue-100 text-blue-600',
      purple: 'bg-purple-100 text-purple-600',
      green: 'bg-green-100 text-green-600',
      indigo: 'bg-indigo-100 text-indigo-600',
      emerald: 'bg-emerald-100 text-emerald-600',
      red: 'bg-red-100 text-red-600'
    }
    return colorMap[color] || 'bg-gray-100 text-gray-600'
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                <Bell className="h-7 w-7 text-indigo-600" />
                Notificações
              </h1>
              {unreadCount > 0 && (
                <p className="text-sm text-gray-600 mt-1">
                  Você tem {unreadCount} notificação(ões) não lida(s)
                </p>
              )}
            </div>

            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
                >
                  <CheckCheck className="h-4 w-4" />
                  Marcar todas como lidas
                </button>
              )}
              <button
                onClick={loadNotifications}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
                title="Atualizar"
              >
                <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2 mt-4">
            <Filter className="h-4 w-4 text-gray-400" />
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition ${
                filter === 'all'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Todas
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition ${
                filter === 'unread'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Não lidas
            </button>
            <button
              onClick={() => setFilter('read')}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition ${
                filter === 'read'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Lidas
            </button>
          </div>
        </div>

        {/* Notifications List */}
        {loading ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <PanelListLoader message="Carregando..." subMessage="A sincronizar com a API de notificações." />
          </div>
        ) : notifications.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200">
            <EmptyState
              variant="embedded"
              illustration="notification"
              title={filter === 'unread' ? 'Nenhuma notificação não lida' : 'Nenhuma notificação'}
              description={
                filter === 'unread'
                  ? 'Está em dia com as notificações não lidas.'
                  : 'Quando houver alertas importantes, aparecem aqui.'
              }
            />
          </div>
        ) : (
          <div className="space-y-2">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                className={`bg-white rounded-xl border shadow-sm hover:shadow-md transition group ${
                  !notification.is_read ? 'border-indigo-200 bg-indigo-50/30' : 'border-gray-200'
                }`}
              >
                <div className="p-4">
                  <div className="flex gap-4">
                    {/* Icon */}
                    <div
                      className={`shrink-0 w-12 h-12 rounded-xl ${getColorClass(
                        notification.color || 'gray'
                      )} flex items-center justify-center`}
                    >
                      <Bell className="h-6 w-6" />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      {notification.action_url ? (
                        <Link
                          to={notification.action_url}
                          onClick={() => !notification.is_read && void markAsRead(notification.id)}
                          className="block"
                        >
                          <h3 className="text-base font-semibold text-gray-900 group-hover:text-indigo-600 transition">
                            {notification.title}
                            {!notification.is_read && (
                              <span className="ml-2 w-2 h-2 bg-indigo-600 rounded-full inline-block"></span>
                            )}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                          <p className="text-xs text-gray-400 mt-2">
                            {formatDistanceToNow(new Date(notification.created_at), {
                              addSuffix: true,
                              locale: ptBR
                            })}
                          </p>
                        </Link>
                      ) : (
                        <>
                          <h3 className="text-base font-semibold text-gray-900">
                            {notification.title}
                            {!notification.is_read && (
                              <span className="ml-2 w-2 h-2 bg-indigo-600 rounded-full inline-block"></span>
                            )}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                          <p className="text-xs text-gray-400 mt-2">
                            {formatDistanceToNow(new Date(notification.created_at), {
                              addSuffix: true,
                              locale: ptBR
                            })}
                          </p>
                        </>
                      )}

                      {/* Actions */}
                      <div className="flex items-center gap-2 mt-3">
                        {!notification.is_read && (
                          <button
                              onClick={() => void markAsRead(notification.id)}
                            className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-indigo-600 hover:bg-indigo-50 rounded transition"
                          >
                            <Check className="h-3 w-3" />
                            Marcar como lida
                          </button>
                        )}
                        <button
                            onClick={() => void deleteNotification(notification.id)}
                          className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50 rounded transition"
                        >
                          <Trash2 className="h-3 w-3" />
                          Deletar
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
