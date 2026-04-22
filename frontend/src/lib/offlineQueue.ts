import axios from 'axios'

export type OfflineActionType =
  | 'notification.mark-read'
  | 'notification.mark-all-read'
  | 'notification.delete'
  | 'comment.add'
  | 'comment.update'
  | 'comment.delete'

export interface OfflineQueueItem<TPayload = Record<string, unknown>> {
  id: string
  action: OfflineActionType
  payload: TPayload
  createdAt: number
  attempts: number
}

type QueueState = {
  pendingCount: number
  pendingByAction: Partial<Record<OfflineActionType, number>>
  isFlushing: boolean
  lastFlushAt: number | null
  lastFlushResult: 'idle' | 'success' | 'partial' | 'failed'
  lastErrorMessage: string | null
  flushedCount: number
  lastEnqueuedAt: number | null
}

type OfflineProcessor = (payload: Record<string, unknown>) => Promise<void>

const STORAGE_KEY = 'agroadb:offline-queue'
const SYNC_TAG = 'agroadb-sync'
const STATE_EVENT = 'agroadb:offline-queue-state'
const processors = new Map<OfflineActionType, OfflineProcessor>()

let state: QueueState = {
  pendingCount: 0,
  pendingByAction: {},
  isFlushing: false,
  lastFlushAt: null,
  lastFlushResult: 'idle',
  lastErrorMessage: null,
  flushedCount: 0,
  lastEnqueuedAt: null,
}
let initialized = false

function emitState() {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(STATE_EVENT, { detail: state }))
}

function updateState(partial: Partial<QueueState>) {
  state = { ...state, ...partial }
  emitState()
}

function readItems(): OfflineQueueItem[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as OfflineQueueItem[]) : []
  } catch {
    return []
  }
}

function writeItems(items: OfflineQueueItem[]) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
}

function buildPendingByAction(items: OfflineQueueItem[]) {
  return items.reduce<Partial<Record<OfflineActionType, number>>>((acc, item) => {
    acc[item.action] = (acc[item.action] ?? 0) + 1
    return acc
  }, {})
}

function shouldQueueError(error: unknown) {
  if (!axios.isAxiosError(error)) return false
  if (!error.response) return true
  return [408, 425, 429, 500, 502, 503, 504].includes(error.response.status)
}

function refreshCount() {
  const items = readItems()
  updateState({
    pendingCount: items.length,
    pendingByAction: buildPendingByAction(items),
    lastEnqueuedAt: items.length > 0 ? Math.max(...items.map((item) => item.createdAt)) : null,
  })
}

async function requestBackgroundSync() {
  if (typeof navigator === 'undefined' || !('serviceWorker' in navigator)) return
  try {
    const registration = await navigator.serviceWorker.ready
    const syncRegistration = registration as ServiceWorkerRegistration & {
      sync?: { register: (tag: string) => Promise<void> }
    }
    await syncRegistration.sync?.register(SYNC_TAG)
  } catch {
    // Unsupported browser or registration not available.
  }
}

export async function enqueueOfflineAction<TPayload extends Record<string, unknown>>(
  action: OfflineActionType,
  payload: TPayload
) {
  const items = readItems()
  const item: OfflineQueueItem<TPayload> = {
    id: `${action}:${Date.now()}:${Math.random().toString(36).slice(2, 8)}`,
    action,
    payload,
    createdAt: Date.now(),
    attempts: 0,
  }
  items.push(item as OfflineQueueItem)
  writeItems(items)
  refreshCount()
  updateState({ lastFlushResult: 'idle', lastErrorMessage: null })
  await requestBackgroundSync()
  return item
}

export async function runOfflineCapableMutation<T>(
  action: OfflineActionType,
  payload: Record<string, unknown>,
  request: () => Promise<T>
): Promise<{ queued: boolean; data?: T }> {
  if (typeof navigator !== 'undefined' && !navigator.onLine) {
    await enqueueOfflineAction(action, payload)
    return { queued: true }
  }

  try {
    const data = await request()
    return { queued: false, data }
  } catch (error) {
    if (!shouldQueueError(error)) {
      throw error
    }
    await enqueueOfflineAction(action, payload)
    return { queued: true }
  }
}

export function registerOfflineProcessor(action: OfflineActionType, processor: OfflineProcessor) {
  processors.set(action, processor)
}

export async function flushOfflineQueue() {
  if (state.isFlushing) return
  if (typeof navigator !== 'undefined' && !navigator.onLine) return

  updateState({ isFlushing: true, lastErrorMessage: null })
  try {
    const nextItems = [...readItems()].sort((a, b) => a.createdAt - b.createdAt)
    const pendingItems: OfflineQueueItem[] = []
    let flushedCount = 0
    let lastErrorMessage: string | null = null

    for (const [index, item] of nextItems.entries()) {
      const processor = processors.get(item.action)
      if (!processor) {
        lastErrorMessage = 'Algumas ações ainda não têm sincronização automática disponível.'
        pendingItems.push(item)
        continue
      }

      try {
        await processor(item.payload)
        flushedCount += 1
      } catch (error) {
        if (shouldQueueError(error)) {
          lastErrorMessage =
            'Não foi possível concluir toda a sincronização. Tentaremos novamente quando a conexão estabilizar.'
          pendingItems.push({ ...item, attempts: item.attempts + 1 })
          pendingItems.push(...nextItems.slice(index + 1))
          break
        }
        lastErrorMessage = 'Uma ou mais ações pendentes exigem revisão manual.'
      }
    }

    writeItems(pendingItems)
    refreshCount()
    updateState({
      lastFlushAt: nextItems.length > 0 ? Date.now() : state.lastFlushAt,
      lastFlushResult:
        nextItems.length === 0
          ? state.lastFlushResult
          : pendingItems.length === 0
          ? 'success'
          : flushedCount > 0
          ? 'partial'
          : 'failed',
      lastErrorMessage,
      flushedCount,
    })
  } finally {
    updateState({ isFlushing: false })
  }
}

export function initializeOfflineQueueSync() {
  if (initialized || typeof window === 'undefined') return
  initialized = true
  refreshCount()

  const handleOnline = () => {
    void flushOfflineQueue()
  }
  const handleVisibility = () => {
    if (document.visibilityState === 'visible') {
      void flushOfflineQueue()
      refreshCount()
    }
  }
  const handleServiceWorkerMessage = (event: MessageEvent) => {
    if (event.data?.type === SYNC_TAG) {
      void flushOfflineQueue()
    }
  }

  window.addEventListener('online', handleOnline)
  document.addEventListener('visibilitychange', handleVisibility)
  navigator.serviceWorker?.addEventListener?.('message', handleServiceWorkerMessage)
}

export function subscribeOfflineQueueState(listener: (nextState: QueueState) => void) {
  if (typeof window === 'undefined') {
    return () => undefined
  }

  const handler = (event: Event) => {
    listener((event as CustomEvent<QueueState>).detail)
  }

  window.addEventListener(STATE_EVENT, handler)
  listener(state)
  return () => window.removeEventListener(STATE_EVENT, handler)
}

export function getOfflineQueueState() {
  return state
}

export function getOfflineActionLabel(action: OfflineActionType) {
  switch (action) {
    case 'notification.mark-read':
    case 'notification.mark-all-read':
    case 'notification.delete':
      return 'notificações'
    case 'comment.add':
    case 'comment.update':
    case 'comment.delete':
      return 'comentários'
    default:
      return 'ações'
  }
}

export function resetOfflineQueueStateForTests() {
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem(STORAGE_KEY)
  }
  processors.clear()
  state = {
    pendingCount: 0,
    pendingByAction: {},
    isFlushing: false,
    lastFlushAt: null,
    lastFlushResult: 'idle',
    lastErrorMessage: null,
    flushedCount: 0,
    lastEnqueuedAt: null,
  }
}
