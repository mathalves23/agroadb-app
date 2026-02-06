import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Navbar from '@/components/Navbar'
import { useAuthStore } from '@/stores/authStore'

// Mock zustand store
jest.mock('@/stores/authStore', () => ({
  useAuthStore: jest.fn(),
}))

describe('Navbar Component', () => {
  it('should render logo and app name', () => {
    jest.mocked(useAuthStore).mockReturnValue({
      user: {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        organization: 'Test Org',
        is_active: true,
        is_superuser: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      accessToken: 'token',
      refreshToken: 'refresh',
      isAuthenticated: true,
      setAuth: jest.fn(),
      logout: jest.fn(),
    })

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    expect(screen.getByText('AgroADB')).toBeInTheDocument()
  })

  it('should display user information', () => {
    jest.mocked(useAuthStore).mockReturnValue({
      user: {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        organization: 'Test Organization',
        is_active: true,
        is_superuser: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      accessToken: 'token',
      refreshToken: 'refresh',
      isAuthenticated: true,
      setAuth: jest.fn(),
      logout: jest.fn(),
    })

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    expect(screen.getByText('Test User')).toBeInTheDocument()
    expect(screen.getByText('Test Organization')).toBeInTheDocument()
  })

  it('should have logout button', () => {
    const mockLogout = jest.fn()

    jest.mocked(useAuthStore).mockReturnValue({
      user: {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        is_active: true,
        is_superuser: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      accessToken: 'token',
      refreshToken: 'refresh',
      isAuthenticated: true,
      setAuth: jest.fn(),
      logout: mockLogout,
    })

    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    )

    const logoutButton = screen.getByText('Sair')
    expect(logoutButton).toBeInTheDocument()
  })
})
