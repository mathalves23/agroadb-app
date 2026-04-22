import { act, renderHook } from '@testing-library/react'
import { useSessionGuard } from '@/hooks/useSessionGuard'

const navigateMock = jest.fn()
const refreshTokenMock = jest.fn()
const updateTokensMock = jest.fn()
const logoutMock = jest.fn()

let authState = {
  accessToken: '',
  refreshToken: 'refresh-token',
  updateTokens: updateTokensMock,
  logout: logoutMock,
  isAuthenticated: true,
}

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => navigateMock,
}))

jest.mock('@/services/authService', () => ({
  authService: {
    refreshToken: (...args: unknown[]) => refreshTokenMock(...args),
  },
}))

jest.mock('@/stores/authStore', () => ({
  useAuthStore: (selector: (state: typeof authState) => unknown) => selector(authState),
}))

function createTokenExpiresIn(secondsFromNow: number) {
  const payload = {
    exp: Math.floor((Date.now() + secondsFromNow * 1000) / 1000),
  }
  return `header.${window.btoa(JSON.stringify(payload))}.signature`
}

describe('useSessionGuard', () => {
  beforeEach(() => {
    jest.useFakeTimers()
    navigateMock.mockReset()
    refreshTokenMock.mockReset()
    updateTokensMock.mockReset()
    logoutMock.mockReset()
    window.localStorage.clear()
    authState = {
      accessToken: createTokenExpiresIn(4 * 60),
      refreshToken: 'refresh-token',
      updateTokens: updateTokensMock,
      logout: logoutMock,
      isAuthenticated: true,
    }
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('shows warning close to expiry and re-displays it after the snooze window', () => {
    const { result } = renderHook(() => useSessionGuard())

    expect(result.current.warningVisible).toBe(true)

    act(() => {
      result.current.dismissWarning()
    })

    expect(result.current.warningVisible).toBe(false)

    act(() => {
      jest.advanceTimersByTime(30_000)
    })
    expect(result.current.warningVisible).toBe(false)

    act(() => {
      jest.advanceTimersByTime(35_000)
    })
    expect(result.current.warningVisible).toBe(true)
  })

  it('renews the session and clears the warning state', async () => {
    refreshTokenMock.mockResolvedValue({
      access_token: createTokenExpiresIn(20 * 60),
      refresh_token: 'next-refresh-token',
    })

    const { result } = renderHook(() => useSessionGuard())

    await act(async () => {
      await result.current.renewSession()
    })

    expect(refreshTokenMock).toHaveBeenCalledWith('refresh-token')
    expect(updateTokensMock).toHaveBeenCalled()
    expect(result.current.renewing).toBe(false)
  })
})
