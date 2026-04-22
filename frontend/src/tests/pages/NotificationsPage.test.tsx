import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import NotificationsPage from '@/pages/NotificationsPage'

const useNotificationsMock = jest.fn()

jest.mock('@/hooks/useNotifications', () => ({
  useNotifications: (options: unknown) => useNotificationsMock(options),
}))

describe('NotificationsPage', () => {
  beforeEach(() => {
    useNotificationsMock.mockReset()
  })

  it('renders loading state', () => {
    useNotificationsMock.mockReturnValue({
      notifications: [],
      unreadCount: 0,
      isLoading: true,
      isRefreshing: false,
      refresh: jest.fn(),
      markAsRead: jest.fn(),
      markAllAsRead: jest.fn(),
      deleteNotification: jest.fn(),
    })

    render(
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    )

    expect(screen.getByText(/carregando/i)).toBeInTheDocument()
    expect(screen.getByText(/sincronizar com a api de notificações/i)).toBeInTheDocument()
  })

  it('renders empty state for unread filter', () => {
    useNotificationsMock.mockReturnValue({
      notifications: [],
      unreadCount: 0,
      isLoading: false,
      isRefreshing: false,
      refresh: jest.fn(),
      markAsRead: jest.fn(),
      markAllAsRead: jest.fn(),
      deleteNotification: jest.fn(),
    })

    render(
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    )

    fireEvent.click(screen.getByRole('button', { name: /não lidas/i }))

    expect(screen.getByText(/nenhuma notificação não lida/i)).toBeInTheDocument()
  })

  it('renders notifications and dispatches actions', () => {
    const refresh = jest.fn()
    const markAsRead = jest.fn()
    const markAllAsRead = jest.fn()
    const deleteNotification = jest.fn()

    useNotificationsMock.mockReturnValue({
      notifications: [
        {
          id: 1,
          title: 'Novo alerta',
          message: 'Investigação atualizada',
          created_at: '2026-04-22T10:00:00Z',
          is_read: false,
          color: 'indigo',
          action_url: '/investigations/1',
        },
      ],
      unreadCount: 1,
      isLoading: false,
      isRefreshing: false,
      refresh,
      markAsRead,
      markAllAsRead,
      deleteNotification,
    })

    render(
      <MemoryRouter>
        <NotificationsPage />
      </MemoryRouter>
    )

    expect(screen.getByText(/novo alerta/i)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /marcar todas como lidas/i }))
    fireEvent.click(screen.getByRole('button', { name: /marcar como lida/i }))
    fireEvent.click(screen.getByRole('button', { name: /deletar/i }))
    fireEvent.click(screen.getByTitle(/atualizar/i))

    expect(markAllAsRead).toHaveBeenCalled()
    expect(markAsRead).toHaveBeenCalledWith(1)
    expect(deleteNotification).toHaveBeenCalledWith(1)
    expect(refresh).toHaveBeenCalled()
  })
})
