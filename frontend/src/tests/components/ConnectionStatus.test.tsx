import { render, screen, act } from '@testing-library/react'
import ConnectionStatus from '@/components/ConnectionStatus'

describe('ConnectionStatus', () => {
  it('shows offline message when browser goes offline', () => {
    render(<ConnectionStatus />)

    act(() => {
      Object.defineProperty(window.navigator, 'onLine', { value: false, configurable: true })
      window.dispatchEvent(new Event('offline'))
    })

    expect(screen.getByText(/voce esta offline/i)).toBeInTheDocument()
  })
})
