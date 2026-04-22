import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import Breadcrumbs from '@/components/Breadcrumbs'

function renderAt(path: string) {
  return render(
    <MemoryRouter
      initialEntries={[path]}
      future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
    >
      <Routes>
        <Route path="*" element={<Breadcrumbs />} />
      </Routes>
    </MemoryRouter>
  )
}

describe('Breadcrumbs', () => {
  it('não renderiza na dashboard (um só nível)', () => {
    const { container } = renderAt('/dashboard')
    expect(container.querySelector('nav[aria-label="Trilha de navegação"]')).toBeNull()
  })

  it('mostra trilha em investigações', () => {
    renderAt('/investigations')
    expect(screen.getByRole('navigation', { name: /trilha de navegação/i })).toBeInTheDocument()
    expect(screen.getByText('Investigações')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /início/i })).toHaveAttribute('href', '/dashboard')
  })
})
