import {
  buildSnapshotKey,
  canPersistOfflineSnapshot,
  readOfflineSnapshot,
  saveOfflineSnapshot,
} from '@/lib/offlineSnapshot'

describe('offlineSnapshot', () => {
  it('builds deterministic keys with params', () => {
    expect(buildSnapshotKey('/notifications', { limit: 10 })).toContain('/notifications')
    expect(buildSnapshotKey('/notifications', { limit: 10 })).toContain('"limit":10')
  })

  it('saves and reads snapshot records', () => {
    const key = buildSnapshotKey('/dashboard', { org: 1 })
    saveOfflineSnapshot(key, { total: 3 })

    expect(readOfflineSnapshot<{ total: number }>(key)).toMatchObject({
      data: { total: 3 },
    })
  })

  it('returns null for malformed snapshots', () => {
    window.localStorage.setItem('agroadb:offline-snapshot:/broken', '{oops')

    expect(readOfflineSnapshot('agroadb:offline-snapshot:/broken')).toBeNull()
  })

  it('filters unsupported payloads for persistence', () => {
    expect(canPersistOfflineSnapshot('/investigations', 'GET', { ok: true })).toBe(true)
    expect(canPersistOfflineSnapshot('/auth/login', 'GET', { ok: true })).toBe(false)
    expect(canPersistOfflineSnapshot('/investigations', 'POST', { ok: true })).toBe(false)
    expect(canPersistOfflineSnapshot('/investigations', 'GET', new Blob())).toBe(false)
  })
})
