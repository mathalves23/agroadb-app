import { act, renderHook } from '@testing-library/react'
import { usePwaUpdatePrompt } from '@/hooks/usePwaUpdatePrompt'

const activateWaitingServiceWorkerMock = jest.fn()
const getPwaUpdateStateMock = jest.fn()
const subscribePwaUpdatesMock = jest.fn()

jest.mock('@/lib/pwa', () => ({
  activateWaitingServiceWorker: () => activateWaitingServiceWorkerMock(),
  getPwaUpdateState: () => getPwaUpdateStateMock(),
  subscribePwaUpdates: (listener: (state: { needRefresh: boolean }) => void) =>
    subscribePwaUpdatesMock(listener),
}))

describe('usePwaUpdatePrompt', () => {
  beforeEach(() => {
    window.sessionStorage.clear()
    getPwaUpdateStateMock.mockReturnValue({ needRefresh: false })
    subscribePwaUpdatesMock.mockImplementation((listener: (state: { needRefresh: boolean }) => void) => {
      listener({ needRefresh: false })
      return () => undefined
    })
    activateWaitingServiceWorkerMock.mockReset()
  })

  it('clears previous dismissal when there is no pending update anymore', () => {
    window.sessionStorage.setItem('agroadb:pwa-update-dismissed', '1')

    const { result } = renderHook(() => usePwaUpdatePrompt())

    expect(result.current.visible).toBe(false)
    expect(window.sessionStorage.getItem('agroadb:pwa-update-dismissed')).toBeNull()
  })

  it('shows the prompt when a new update event arrives after a dismissal', () => {
    let listenerRef: ((state: { needRefresh: boolean }) => void) | null = null
    window.sessionStorage.setItem('agroadb:pwa-update-dismissed', '1')
    subscribePwaUpdatesMock.mockImplementation((listener: (state: { needRefresh: boolean }) => void) => {
      listenerRef = listener
      listener({ needRefresh: false })
      return () => undefined
    })

    const { result } = renderHook(() => usePwaUpdatePrompt())

    act(() => {
      listenerRef?.({ needRefresh: true })
    })

    expect(result.current.visible).toBe(true)
  })

  it('triggers activation when the user chooses to update now', async () => {
    getPwaUpdateStateMock.mockReturnValue({ needRefresh: true })
    subscribePwaUpdatesMock.mockImplementation((listener: (state: { needRefresh: boolean }) => void) => {
      listener({ needRefresh: true })
      return () => undefined
    })

    const { result } = renderHook(() => usePwaUpdatePrompt())

    await act(async () => {
      await result.current.update()
    })

    expect(activateWaitingServiceWorkerMock).toHaveBeenCalled()
  })
})
