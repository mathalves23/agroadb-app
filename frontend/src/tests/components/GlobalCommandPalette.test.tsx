import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'

import GlobalCommandPalette from '@/components/GlobalCommandPalette'

const navigateMock = jest.fn()

jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => navigateMock,
  }
})

jest.mock('@/services/investigationService', () => ({
  investigationService: {
    listCursor: jest.fn().mockResolvedValue({
      items: [
        {
          id: 7,
          user_id: 1,
          target_name: 'Fazenda Aurora',
          target_cpf_cnpj: '12345678901',
          target_description: 'Teste',
          status: 'in_progress',
          priority: 1,
          properties_found: 0,
          lease_contracts_found: 0,
          companies_found: 0,
          created_at: '2026-04-22T00:00:00Z',
          updated_at: '2026-04-22T00:00:00Z',
        },
      ],
    }),
  },
}))

function renderPalette() {
  const client = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <GlobalCommandPalette />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('GlobalCommandPalette', () => {
  beforeEach(() => {
    navigateMock.mockReset()
  })

  it('opens with Ctrl+K and shows navigation items', async () => {
    renderPalette()

    fireEvent.keyDown(document, { key: 'k', ctrlKey: true })

    expect(await screen.findByLabelText(/pesquisar comandos/i)).toBeInTheDocument()
    expect(screen.getByText('Notificações')).toBeInTheDocument()
    expect(screen.getByText(/áreas principais/i)).toBeInTheDocument()
    expect(screen.getByRole('dialog', { name: /palette de comandos global/i })).toBeInTheDocument()
  })

  it('filters and navigates to investigation results', async () => {
    renderPalette()

    fireEvent.keyDown(document, { key: 'k', ctrlKey: true })
    const input = await screen.findByLabelText(/pesquisar comandos/i)
    fireEvent.change(input, { target: { value: 'Aurora' } })

    await waitFor(() => expect(screen.getByText(/fazenda aurora/i)).toBeInTheDocument())
    fireEvent.keyDown(document, { key: 'Enter' })

    expect(navigateMock).toHaveBeenCalledWith('/investigations/7')
  })

  it('exposes combobox and listbox semantics', async () => {
    renderPalette()

    fireEvent.keyDown(document, { key: 'k', ctrlKey: true })

    const input = await screen.findByRole('combobox', { name: /pesquisar comandos/i })
    expect(input).toHaveAttribute('aria-controls', 'command-palette-listbox')
    expect(screen.getByRole('listbox', { name: /resultados da palette de comandos/i })).toBeInTheDocument()
  })
})
