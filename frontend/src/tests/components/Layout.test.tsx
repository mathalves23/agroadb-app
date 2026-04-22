import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import Layout from '@/components/Layout'

jest.mock('@/components/NotificationDropdown', () => ({
  __esModule: true,
  default: () => <div data-testid="mock-notifications" />,
}))

jest.mock('@/components/IntegrationRetryBanner', () => ({
  __esModule: true,
  default: () => null,
}))

jest.mock('@/components/PwaUpdatePrompt', () => ({
  __esModule: true,
  default: () => null,
}))

jest.mock('@/components/GlobalCommandPalette', () => ({
  __esModule: true,
  default: () => null,
}))

jest.mock('@/components/SessionExpiryBanner', () => ({
  __esModule: true,
  default: () => null,
}))

describe('Layout', () => {
  it('expõe skip link, landmark principal e sidebar identificável', () => {
    render(
      <MemoryRouter
        initialEntries={['/dashboard']}
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <Routes>
          <Route element={<Layout />}>
            <Route path="dashboard" element={<div>Página</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    )

    expect(screen.getByRole('link', { name: /ir ao conteúdo principal/i })).toHaveAttribute(
      'href',
      '#app-main-content'
    )
    const main = screen.getByRole('main', { name: /conteúdo principal/i })
    expect(main).toHaveAttribute('id', 'app-main-content')
    expect(document.getElementById('app-sidebar')).toBeTruthy()
  })
})
