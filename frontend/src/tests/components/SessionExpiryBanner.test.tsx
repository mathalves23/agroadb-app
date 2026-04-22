import { fireEvent, render, screen } from '@testing-library/react'
import SessionExpiryBanner from '@/components/SessionExpiryBanner'

const renewSessionMock = jest.fn()
const dismissWarningMock = jest.fn()

jest.mock('@/hooks/useSessionGuard', () => ({
  useSessionGuard: () => ({
    warningVisible: true,
    remainingText: '4 minutos',
    renewing: false,
    renewSession: renewSessionMock,
    dismissWarning: dismissWarningMock,
  }),
}))

describe('SessionExpiryBanner', () => {
  it('shows the remaining time and lets the user renew or dismiss', () => {
    render(<SessionExpiryBanner />)

    expect(screen.getByText(/sua sessão expira em 4 minutos/i)).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /renovar sessão/i }))
    fireEvent.click(screen.getByRole('button', { name: /fechar/i }))

    expect(renewSessionMock).toHaveBeenCalled()
    expect(dismissWarningMock).toHaveBeenCalled()
  })
})
