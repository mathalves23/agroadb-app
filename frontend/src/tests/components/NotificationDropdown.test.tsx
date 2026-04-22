import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import NotificationDropdown from '@/components/NotificationDropdown'

jest.mock('@/hooks/useNotifications', () => ({
  useNotifications: () => ({
    notifications: [
      {
        id: 1,
        type: 'system',
        title: 'Atualizacao',
        message: 'Nova sincronizacao disponivel',
        priority: 'normal',
        is_read: false,
        created_at: '2026-04-22T10:00:00Z',
        action_url: '/notifications',
      },
    ],
    unreadCount: 2,
    isLoading: false,
    refresh: jest.fn(),
    markAsRead: jest.fn(),
    markAllAsRead: jest.fn(),
    deleteNotification: jest.fn(),
  }),
}))

describe('NotificationDropdown', () => {
  it('loads unread count and notification list when opened', async () => {
    render(
      <MemoryRouter>
        <NotificationDropdown />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button'))

    await waitFor(() => {
      expect(screen.getByText('Atualizacao')).toBeInTheDocument()
      expect(screen.getByText(/nova sincronizacao disponivel/i)).toBeInTheDocument()
    })
  })
})
