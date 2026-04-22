import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import NotificationDropdown from '@/components/NotificationDropdown'

jest.mock('@/services/notificationService', () => ({
  notificationService: {
    getUnreadCount: jest.fn().mockResolvedValue(2),
    list: jest.fn().mockResolvedValue([
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
    ]),
    markAsRead: jest.fn().mockResolvedValue(undefined),
    markAllAsRead: jest.fn().mockResolvedValue(undefined),
    delete: jest.fn().mockResolvedValue(undefined),
  },
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
