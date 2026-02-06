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
  })

  it('should have correct href attributes', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    )

    const dashboardLink = screen.getByText('Dashboard').closest('a')
    const investigationsLink = screen.getByText('Investigações').closest('a')

    expect(dashboardLink).toHaveAttribute('href', '/dashboard')
    expect(investigationsLink).toHaveAttribute('href', '/investigations')
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
