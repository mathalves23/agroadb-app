import {
  enqueueOfflineAction,
  flushOfflineQueue,
  getOfflineActionLabel,
  getOfflineQueueState,
  registerOfflineProcessor,
  resetOfflineQueueStateForTests,
} from '@/lib/offlineQueue'

describe('offlineQueue', () => {
  beforeEach(() => {
    resetOfflineQueueStateForTests()
    Object.defineProperty(window.navigator, 'onLine', {
      configurable: true,
      value: true,
    })
  })

  it('tracks pending actions by category when enqueueing offline work', async () => {
    await enqueueOfflineAction('comment.add', {
      investigationId: 1,
      content: 'Comentário pendente',
    })
    await enqueueOfflineAction('notification.mark-read', {
      notificationId: 5,
    })

    expect(getOfflineQueueState()).toMatchObject({
      pendingCount: 2,
      pendingByAction: {
        'comment.add': 1,
        'notification.mark-read': 1,
      },
      lastFlushResult: 'idle',
    })
  })

  it('records successful flush metadata after syncing pending items', async () => {
    registerOfflineProcessor('comment.add', jest.fn().mockResolvedValue(undefined))

    await enqueueOfflineAction('comment.add', {
      investigationId: 1,
      content: 'Comentário pendente',
    })

    await flushOfflineQueue()

    expect(getOfflineQueueState()).toMatchObject({
      pendingCount: 0,
      lastFlushResult: 'success',
      flushedCount: 1,
      lastErrorMessage: null,
    })
  })

  it('keeps pending items and stores an error message when sync fails', async () => {
    registerOfflineProcessor(
      'notification.delete',
      jest.fn().mockRejectedValue({ isAxiosError: true, response: { status: 503 } })
    )

    await enqueueOfflineAction('notification.delete', {
      notificationId: 12,
    })

    await flushOfflineQueue()

    expect(getOfflineQueueState()).toMatchObject({
      pendingCount: 1,
      lastFlushResult: 'failed',
      flushedCount: 0,
    })
    expect(getOfflineQueueState().lastErrorMessage).toMatch(/não foi possível concluir/i)
  })

  it('maps action labels to user-friendly groups', () => {
    expect(getOfflineActionLabel('comment.add')).toBe('comentários')
    expect(getOfflineActionLabel('notification.mark-all-read')).toBe('notificações')
  })
})
