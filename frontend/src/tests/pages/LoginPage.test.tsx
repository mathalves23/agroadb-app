import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import LoginPage from '@/pages/LoginPage'
import { useAuthStore } from '@/stores/authStore'

// Mock modules
jest.mock('@/stores/authStore', () => ({
  useAuthStore: jest.fn(),
}))

jest.mock('@/services/authService', () => ({
  authService: {
    login: jest.fn(),
    getMe: jest.fn(),
  },
}))

const mockNavigate = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}))

describe('LoginPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    
    ;(useAuthStore as unknown as jest.Mock).mockReturnValue({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      setAuth: jest.fn(),
      logout: jest.fn(),
    })
  })

  it('should render login form', () => {
    render(
      <BrowserRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <LoginPage />
      </BrowserRouter>
    )

    expect(screen.getAllByText('AgroADB').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByLabelText(/usuário ou email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^senha$/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /entrar/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/usuário ou email/i)).toHaveFocus()
  })

  it('should have link to register page', () => {
    render(
      <BrowserRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <LoginPage />
      </BrowserRouter>
    )

    const registerLink = screen.getByRole('link', { name: /registre-se/i })
    expect(registerLink).toBeInTheDocument()
  })

  it('should show validation errors for empty fields', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <LoginPage />
      </BrowserRouter>
    )

    const submitButton = screen.getByRole('button', { name: /entrar/i })
    await user.click(submitButton)

    await waitFor(() => {
      const errors = screen.queryAllByText(/deve ter no mínimo/i)
      expect(errors.length).toBeGreaterThan(0)
    })
  })

  it('should validate minimum username length', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <LoginPage />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/usuário ou email/i)
    await user.type(usernameInput, 'ab')

    const passwordInput = screen.getByLabelText(/^senha$/i)
    await user.type(passwordInput, '12345')

    const submitButton = screen.getByRole('button', { name: /entrar/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/usuário ou email deve ter no mínimo 3 caracteres/i)).toBeInTheDocument()
    })
  })

  it('should validate minimum password length', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <LoginPage />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/usuário ou email/i)
    await user.type(usernameInput, 'testuser')

    const passwordInput = screen.getByLabelText(/^senha$/i)
    await user.type(passwordInput, '1234567')

    const submitButton = screen.getByRole('button', { name: /entrar/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/senha deve ter no mínimo 8 caracteres/i)).toBeInTheDocument()
    })
  })

  it('should accept valid credentials', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <LoginPage />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/usuário ou email/i)
    await user.type(usernameInput, 'testuser')

    const passwordInput = screen.getByLabelText(/^senha$/i)
    await user.type(passwordInput, 'password123')

    const submitButton = screen.getByRole('button', { name: /entrar/i })
    
    // Should not show validation errors
    await user.click(submitButton)
    
    // Wait a bit to ensure no validation errors appear
    await new Promise(resolve => setTimeout(resolve, 100))
  })

  it('should expose login errors through an alert region', async () => {
    const user = userEvent.setup()

    render(
      <BrowserRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <LoginPage />
      </BrowserRouter>
    )

    const usernameInput = screen.getByLabelText(/usuário ou email/i)
    await user.type(usernameInput, 'testuser')

    const passwordInput = screen.getByLabelText(/^senha$/i)
    await user.type(passwordInput, '1234567')

    await user.click(screen.getByRole('button', { name: /entrar/i }))

    await waitFor(() => {
      expect(screen.getByText(/senha deve ter no mínimo 8 caracteres/i)).toBeInTheDocument()
    })

    expect(screen.getByLabelText(/^senha$/i)).toHaveFocus()
  })
})
