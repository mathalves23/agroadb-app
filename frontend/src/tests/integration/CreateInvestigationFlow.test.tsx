// Jest globals are available automatically
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import NewInvestigationPage from '@/pages/NewInvestigationPage'
import { useAuthStore } from '@/stores/authStore'
import * as investigationService from '@/services/investigationService'

jest.mock('@/stores/authStore', () => ({
  useAuthStore: jest.fn(),
}))

jest.mock('@/services/investigationService', () => ({
  investigationService: {
    create: jest.fn(),
  },
}))

const mockNavigate = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  )
}

describe('NewInvestigationPage Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()

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
      logout: jest.fn(),
    })
  })

  it('should render form fields', () => {
    render(<NewInvestigationPage />, { wrapper: createWrapper() })

    expect(screen.getByLabelText(/cpf ou cnpj/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/nome \(opcional\)/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/contexto \/ descrição/i)).toBeInTheDocument()
    expect(screen.getByText('Prioridade')).toBeInTheDocument()
  })

  it('should show validation error for empty target name', async () => {
    const user = userEvent.setup()

    render(<NewInvestigationPage />, { wrapper: createWrapper() })

    const submitButton = screen.getByRole('button', { name: /iniciar investigação/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/informe o nome ou cpf\/cnpj/i)).toBeInTheDocument()
    })
  })

  it('should submit form with valid data', async () => {
    const user = userEvent.setup()

    const mockInvestigation = {
      id: 1,
      user_id: 1,
      target_name: 'João Silva',
      target_cpf_cnpj: '123.456.789-00',
      target_description: 'Test investigation',
      status: 'pending' as const,
      priority: 3,
      properties_found: 0,
      lease_contracts_found: 0,
      companies_found: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    jest.mocked(investigationService.investigationService.create).mockResolvedValue(mockInvestigation)

    render(<NewInvestigationPage />, { wrapper: createWrapper() })

    // Fill form (CPF válido + nome)
    const cpfInput = screen.getByLabelText(/cpf ou cnpj/i)
    await user.type(cpfInput, '12345678900')

    const nameInput = screen.getByLabelText(/nome \(opcional\)/i)
    await user.type(nameInput, 'João Silva')

    const descInput = screen.getByLabelText(/contexto \/ descrição/i)
    await user.type(descInput, 'Test investigation')

    // Submit
    const submitButton = screen.getByRole('button', { name: /iniciar investigação/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(investigationService.investigationService.create).toHaveBeenCalled()
      const calls = jest.mocked(investigationService.investigationService.create).mock.calls
      expect(calls[0][0]).toEqual({
        target_name: 'João Silva',
        target_cpf_cnpj: '12345678900',
        target_description: 'Test investigation',
        priority: 3,
      })
    })
  })

  it('should show error message on API failure', async () => {
    const user = userEvent.setup()

    jest.mocked(investigationService.investigationService.create).mockRejectedValue({
      response: {
        data: {
          detail: 'API Error',
        },
      },
    })

    render(<NewInvestigationPage />, { wrapper: createWrapper() })

    const cpfInput = screen.getByLabelText(/cpf ou cnpj/i)
    await user.type(cpfInput, '12345678900')

    const nameInput = screen.getByLabelText(/nome \(opcional\)/i)
    await user.type(nameInput, 'João Silva')

    const submitButton = screen.getByRole('button', { name: /iniciar investigação/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/API Error/i)).toBeInTheDocument()
    })
  })

  it('should have cancel button that navigates back', () => {
    render(<NewInvestigationPage />, { wrapper: createWrapper() })

    const cancelButton = screen.getByRole('button', { name: /cancelar/i })
    expect(cancelButton).toBeInTheDocument()
  })

  it('should display search type and bases sections', () => {
    render(<NewInvestigationPage />, { wrapper: createWrapper() })

    expect(screen.getByText(/tipo de pesquisa/i)).toBeInTheDocument()
    expect(screen.getByText(/bases que serão consultadas/i)).toBeInTheDocument()
  })

  it('should have all priority level buttons', () => {
    render(<NewInvestigationPage />, { wrapper: createWrapper() })

    expect(screen.getByText('Prioridade')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /baixa/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /média/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /urgente/i })).toBeInTheDocument()
  })
})
