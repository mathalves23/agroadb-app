import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import {
  Bell,
  Check,
  CheckCheck,
  Trash2,
  FileText,
  Share2,
  MessageSquare,
  RefreshCw,
  FileCheck,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { PanelListLoader } from '@/components/Loading'
import { NoNotificationsEmpty } from '@/components/EmptyState'
import { useNotifications } from '@/hooks/useNotifications'
import type { NotificationItem } from '@/services/notificationService'

const iconMap: Record<string, LucideIcon> = {
  FileText: FileText,
  Share2: Share2,
  MessageSquare: MessageSquare,
  RefreshCw: RefreshCw,
  FileCheck: FileCheck,
  CheckCircle: CheckCircle,
  Bell: Bell,
  AlertTriangle: AlertTriangle
}

const colorMap: Record<string, string> = {
  blue: 'bg-blue-100 text-blue-600',
  purple: 'bg-purple-100 text-purple-600',
  green: 'bg-green-100 text-green-600',
  indigo: 'bg-indigo-100 text-indigo-600',
  emerald: 'bg-emerald-100 text-emerald-600',
  teal: 'bg-teal-100 text-teal-600',
  gray: 'bg-gray-100 text-gray-600',
  red: 'bg-red-100 text-red-600'
}

export default function NotificationDropdown() {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const {
    notifications,
    unreadCount,
    isLoading,
    refresh,
    markAsRead,
    markAllAsRead,
    deleteNotification,
  } = useNotifications({
    limit: 10,
    includeRead: true,
    pollUnreadCount: true,
  })

  useEffect(() => {
    if (isOpen) {
      refresh()
    }
  }, [isOpen, refresh])

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const getIcon = (notification: NotificationItem) => {
    const IconComponent = iconMap[notification.icon || 'Bell']
    return IconComponent || Bell
  }

  const getColorClass = (notification: NotificationItem) => {
    return colorMap[notification.color || 'gray'] || colorMap.gray
  }

  const handleNotificationClick = (notification: NotificationItem) => {
    if (!notification.is_read) {
      void markAsRead(notification.id)
    }
    if (notification.action_url) {
      setIsOpen(false)
    }
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-[600px] flex flex-col">
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Notificações</h3>
              {unreadCount > 0 && (
                <p className="text-xs text-gray-500">{unreadCount} não lida(s)</p>
              )}
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-xs text-indigo-600 hover:text-indigo-700 font-medium flex items-center gap-1"
              >
                <CheckCheck className="h-3.5 w-3.5" />
                Marcar todas
              </button>
            )}
          </div>

          {/* Notifications List */}
          <div className="overflow-y-auto flex-1">
            {isLoading ? (
              <div className="p-6">
                <PanelListLoader message="Carregando..." />
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-2">
                <NoNotificationsEmpty embedded />
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {notifications.map((notification) => {
                  const Icon = getIcon(notification)
                  const colorClass = getColorClass(notification)

                  return (
                    <div
                      key={notification.id}
                      className={`p-4 hover:bg-gray-50 transition group ${
                        !notification.is_read ? 'bg-indigo-50/30' : ''
                      }`}
                    >
                      <div className="flex gap-3">
                        {/* Icon */}
                        <div className={`shrink-0 w-10 h-10 rounded-lg ${colorClass} flex items-center justify-center`}>
                          <Icon className="h-5 w-5" />
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          {notification.action_url ? (
                            <Link
                              to={notification.action_url}
                              onClick={() => handleNotificationClick(notification)}
                              className="block"
                            >
                              <div className="flex items-start justify-between gap-2">
                                <h4 className="text-sm font-semibold text-gray-900 group-hover:text-indigo-600 transition">
                                  {notification.title}
                                  {!notification.is_read && (
                                    <span className="ml-2 w-2 h-2 bg-indigo-600 rounded-full inline-block"></span>
                                  )}
                                </h4>
                              </div>
                              <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                                {notification.message}
                              </p>
                              <p className="text-xs text-gray-400 mt-1">
                                {formatDistanceToNow(new Date(notification.created_at), {
                                  addSuffix: true,
                                  locale: ptBR
                                })}
                              </p>
                            </Link>
                          ) : (
                            <>
                              <div className="flex items-start justify-between gap-2">
                                <h4 className="text-sm font-semibold text-gray-900">
                                  {notification.title}
                                  {!notification.is_read && (
                                    <span className="ml-2 w-2 h-2 bg-indigo-600 rounded-full inline-block"></span>
                                  )}
                                </h4>
                              </div>
                              <p className="text-xs text-gray-600 mt-1">
                                {notification.message}
                              </p>
                              <p className="text-xs text-gray-400 mt-1">
                                {formatDistanceToNow(new Date(notification.created_at), {
                                  addSuffix: true,
                                  locale: ptBR
                                })}
                              </p>
                            </>
                          )}

                          {/* Actions */}
                          <div className="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition">
                            {!notification.is_read && (
                              <button
                                onClick={(e) => {
                                  e.preventDefault()
                                  void markAsRead(notification.id)
                                }}
                                className="text-xs text-gray-500 hover:text-indigo-600 flex items-center gap-1"
                                title="Marcar como lida"
                              >
                                <Check className="h-3 w-3" />
                              </button>
                            )}
                            <button
                              onClick={(e) => {
                                e.preventDefault()
                                void deleteNotification(notification.id)
                              }}
                              className="text-xs text-gray-500 hover:text-red-600 flex items-center gap-1"
                              title="Deletar"
                            >
                              <Trash2 className="h-3 w-3" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
              <Link
                to="/notifications"
                onClick={() => setIsOpen(false)}
                className="text-xs text-indigo-600 hover:text-indigo-700 font-medium text-center block"
              >
                Ver todas as notificações
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
