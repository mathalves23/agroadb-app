import { describe, it, expect, vi, beforeEach } from '@jest/globals'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import DashboardPage from '@/pages/DashboardPage'
import { useAuthStore } from '@/stores/authStore'
import * as investigationService from '@/services/investigationService'

// Mock modules
jest.mock('@/stores/authStore', () => ({
  useAuthStore: jest.fn(),
}))

jest.mock('@/services/investigationService', () => ({
  investigationService: {
    list: jest.fn(),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
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

describe('DashboardPage Component', () => {
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

  it('should render dashboard header', async () => {
    jest.mocked(investigationService.investigationService.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 10,
      total_pages: 0,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText(/visão geral das suas investigações/i)).toBeInTheDocument()
  })

  it('should show "Nova Investigação" button', async () => {
    jest.mocked(investigationService.investigationService.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 10,
      total_pages: 0,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })

    const newInvestigationButton = screen.getByText('Nova Investigação')
    expect(newInvestigationButton).toBeInTheDocument()
  })

  it('should display statistics cards', async () => {
    jest.mocked(investigationService.investigationService.list).mockResolvedValue({
      items: [
        {
          id: 1,
          user_id: 1,
          target_name: 'Test',
          status: 'in_progress',
          priority: 3,
          properties_found: 5,
          lease_contracts_found: 2,
          companies_found: 3,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      total: 1,
      page: 1,
      page_size: 10,
      total_pages: 1,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('Investigações Ativas')).toBeInTheDocument()
      expect(screen.getByText('Propriedades Encontradas')).toBeInTheDocument()
      expect(screen.getByText('Empresas Identificadas')).toBeInTheDocument()
    })
  })

  it('should show loading state', () => {
    jest.mocked(investigationService.investigationService.list).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    render(<DashboardPage />, { wrapper: createWrapper() })

    expect(screen.getByText(/carregando/i)).toBeInTheDocument()
  })

  it('should show empty state when no investigations', async () => {
    jest.mocked(investigationService.investigationService.list).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 10,
      total_pages: 0,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText(/nenhuma investigação encontrada/i)).toBeInTheDocument()
    })
  })

  it('should display recent investigations', async () => {
    jest.mocked(investigationService.investigationService.list).mockResolvedValue({
      items: [
        {
          id: 1,
          user_id: 1,
          target_name: 'João Silva',
          target_cpf_cnpj: '123.456.789-00',
          status: 'completed',
          priority: 3,
          properties_found: 5,
          lease_contracts_found: 2,
          companies_found: 3,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 2,
          user_id: 1,
          target_name: 'Maria Santos',
          status: 'in_progress',
          priority: 5,
          properties_found: 0,
          lease_contracts_found: 0,
          companies_found: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      total: 2,
      page: 1,
      page_size: 10,
      total_pages: 1,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('João Silva')).toBeInTheDocument()
      expect(screen.getByText('Maria Santos')).toBeInTheDocument()
    })
  })

  it('should show correct status badges', async () => {
    jest.mocked(investigationService.investigationService.list).mockResolvedValue({
      items: [
        {
          id: 1,
          user_id: 1,
          target_name: 'Test',
          status: 'completed',
          priority: 3,
          properties_found: 0,
          lease_contracts_found: 0,
          companies_found: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      total: 1,
      page: 1,
      page_size: 10,
      total_pages: 1,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('Concluída')).toBeInTheDocument()
    })
  })
})
