import { fireEvent, render, screen } from '@testing-library/react'
import PwaInstallBanner from '@/components/PwaInstallBanner'

const installMock = jest.fn()
const dismissMock = jest.fn()

jest.mock('@/hooks/usePwaInstallPrompt', () => ({
  usePwaInstallPrompt: () => ({
    canShowPrompt: true,
    isInstalled: false,
    install: installMock,
    dismiss: dismissMock,
  }),
}))

describe('PwaInstallBanner', () => {
  it('renders CTA and handles actions', () => {
    render(<PwaInstallBanner />)

    fireEvent.click(screen.getByRole('button', { name: /instalar app/i }))
    fireEvent.click(screen.getByRole('button', { name: /agora nao/i }))

    expect(installMock).toHaveBeenCalled()
    expect(dismissMock).toHaveBeenCalled()
  })
})
