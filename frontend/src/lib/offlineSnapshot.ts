const SNAPSHOT_PREFIX = 'agroadb:offline-snapshot:'
const MAX_SNAPSHOT_BYTES = 500_000

type SnapshotRecord<T = unknown> = {
  cachedAt: number
  data: T
}

function isStorageAvailable() {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined'
}

export function buildSnapshotKey(url: string, params?: unknown) {
  const suffix = params ? `?${JSON.stringify(params)}` : ''
  return `${SNAPSHOT_PREFIX}${url}${suffix}`
}

export function saveOfflineSnapshot<T>(key: string, data: T) {
  if (!isStorageAvailable()) return

  const record: SnapshotRecord<T> = {
    cachedAt: Date.now(),
    data,
  }

  const raw = JSON.stringify(record)
  if (raw.length > MAX_SNAPSHOT_BYTES) return
  window.localStorage.setItem(key, raw)
}

export function readOfflineSnapshot<T>(key: string): SnapshotRecord<T> | null {
  if (!isStorageAvailable()) return null

  const raw = window.localStorage.getItem(key)
  if (!raw) return null

  try {
    return JSON.parse(raw) as SnapshotRecord<T>
  } catch {
    return null
  }
}

export function canPersistOfflineSnapshot(url?: string, method?: string, data?: unknown) {
  if (!url || method?.toUpperCase() !== 'GET') return false
  if (!url.startsWith('/')) return false
  if (url.includes('/auth/login') || url.includes('/auth/refresh')) return false
  if (data instanceof Blob || data instanceof ArrayBuffer) return false
  return true
}
