import { render, screen, act } from '@testing-library/react'
import ConnectionStatus from '@/components/ConnectionStatus'

const useBackendAvailabilityMock = jest.fn()
const useOfflineQueueMock = jest.fn()
const useNetworkStatusMock = jest.fn()

jest.mock('@/hooks/useBackendAvailability', () => ({
  useBackendAvailability: () => useBackendAvailabilityMock(),
}))

jest.mock('@/hooks/useOfflineQueue', () => ({
  useOfflineQueue: () => useOfflineQueueMock(),
}))

jest.mock('@/hooks/useNetworkStatus', () => ({
  useNetworkStatus: () => useNetworkStatusMock(),
}))

describe('ConnectionStatus', () => {
  beforeEach(() => {
    useNetworkStatusMock.mockReturnValue({
      isOnline: false,
      lastChangedAt: Date.now(),
    })
    useBackendAvailabilityMock.mockReturnValue({
      status: 'offline',
      checkedAt: Date.now(),
      retry: jest.fn(),
    })
    useOfflineQueueMock.mockReturnValue({
      pendingCount: 0,
      pendingByAction: {},
      isFlushing: false,
      lastFlushAt: null,
      lastFlushResult: 'idle',
      lastErrorMessage: null,
      flushedCount: 0,
      lastEnqueuedAt: null,
      retrySync: jest.fn(),
    })
  })

  it('shows offline message when browser goes offline', () => {
    render(<ConnectionStatus />)

    act(() => {
      Object.defineProperty(window.navigator, 'onLine', { value: false, configurable: true })
      window.dispatchEvent(new Event('offline'))
    })

    expect(screen.getByText(/você está offline/i)).toBeInTheDocument()
  })

  it('shows backend recovery state with pending sync actions', () => {
    useNetworkStatusMock.mockReturnValue({
      isOnline: true,
      lastChangedAt: Date.now(),
    })
    useBackendAvailabilityMock.mockReturnValue({
      status: 'reconnected',
      checkedAt: Date.now(),
      retry: jest.fn(),
    })
    useOfflineQueueMock.mockReturnValue({
      pendingCount: 3,
      pendingByAction: { 'comment.add': 2, 'notification.mark-read': 1 },
      isFlushing: true,
      lastFlushAt: Date.now(),
      lastFlushResult: 'idle',
      lastErrorMessage: null,
      flushedCount: 0,
      lastEnqueuedAt: Date.now(),
      retrySync: jest.fn(),
    })

    render(<ConnectionStatus />)

    expect(screen.getByText(/conexão restabelecida/i)).toBeInTheDocument()
    expect(screen.getByText(/sincronizando 3 ação/i)).toBeInTheDocument()
  })

  it('shows queued categories and manual sync when pending items need attention', () => {
    const retrySync = jest.fn()

    useNetworkStatusMock.mockReturnValue({
      isOnline: true,
      lastChangedAt: Date.now(),
    })
    useBackendAvailabilityMock.mockReturnValue({
      status: 'ready',
      checkedAt: Date.now(),
      retry: jest.fn(),
    })
    useOfflineQueueMock.mockReturnValue({
      pendingCount: 3,
      pendingByAction: { 'comment.add': 2, 'notification.mark-read': 1 },
      isFlushing: false,
      lastFlushAt: Date.now(),
      lastFlushResult: 'failed',
      lastErrorMessage: 'Não foi possível concluir toda a sincronização.',
      flushedCount: 0,
      lastEnqueuedAt: Date.now(),
      retrySync,
    })

    render(<ConnectionStatus />)

    expect(screen.getByText(/ações pendentes de sincronização/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sincronizar agora/i })).toBeInTheDocument()
    expect(screen.getByText(/não foi possível concluir toda a sincronização/i)).toBeInTheDocument()
  })

  it('shows successful sync feedback after flush completes', () => {
    useNetworkStatusMock.mockReturnValue({
      isOnline: true,
      lastChangedAt: Date.now(),
    })
    useBackendAvailabilityMock.mockReturnValue({
      status: 'ready',
      checkedAt: Date.now(),
      retry: jest.fn(),
    })
    useOfflineQueueMock.mockReturnValue({
      pendingCount: 0,
      pendingByAction: {},
      isFlushing: false,
      lastFlushAt: Date.now(),
      lastFlushResult: 'success',
      lastErrorMessage: null,
      flushedCount: 4,
      lastEnqueuedAt: null,
      retrySync: jest.fn(),
    })

    render(<ConnectionStatus />)

    expect(screen.getByText(/sincronização concluída/i)).toBeInTheDocument()
    expect(screen.getByText(/4 ação\(ões\) local\(is\) foram sincronizadas/i)).toBeInTheDocument()
  })

  it('shows retry button when backend is unavailable', () => {
    useNetworkStatusMock.mockReturnValue({
      isOnline: true,
      lastChangedAt: Date.now(),
    })
    const retry = jest.fn()
    useBackendAvailabilityMock.mockReturnValue({
      status: 'unavailable',
      checkedAt: Date.now(),
      retry,
    })
    useOfflineQueueMock.mockReturnValue({
      pendingCount: 0,
      pendingByAction: {},
      isFlushing: false,
      lastFlushAt: null,
      lastFlushResult: 'idle',
      lastErrorMessage: null,
      flushedCount: 0,
      lastEnqueuedAt: null,
      retrySync: jest.fn(),
    })

    render(<ConnectionStatus />)

    expect(screen.getByText(/backend indisponível/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /tentar de novo/i })).toBeInTheDocument()
  })
})
