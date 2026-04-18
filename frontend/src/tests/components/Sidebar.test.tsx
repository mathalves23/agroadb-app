// Jest globals are available automatically
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Sidebar from '@/components/Sidebar'

describe('Sidebar Component', () => {
  it('should render navigation links', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    )

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Investigações')).toBeInTheDocument()
    expect(screen.getByText('Notificações')).toBeInTheDocument()
    expect(screen.getByText('Perfil')).toBeInTheDocument()
    expect(screen.getByText('Fontes públicas')).toBeInTheDocument()
  })

  it('should have correct href attributes', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    )

    const dashboardLink = screen.getByText('Dashboard').closest('a')
    const investigationsLink = screen.getByText('Investigações').closest('a')
    const notificationsLink = screen.getByText('Notificações').closest('a')

    expect(dashboardLink).toHaveAttribute('href', '/dashboard')
    expect(investigationsLink).toHaveAttribute('href', '/investigations')
    expect(notificationsLink).toHaveAttribute('href', '/notifications')
  })

  it('should display navigation icons', () => {
    const { container } = render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    )

    // Check for SVG icons
    const icons = container.querySelectorAll('svg')
    expect(icons.length).toBeGreaterThan(0)
  })
})
