import { useState, useCallback } from 'react'

/**
 * Hook para infinite scroll com cursor opcional.
 */
export function useInfiniteScroll<T>(
  fetchFn: (cursor?: string) => Promise<{ items: T[]; nextCursor?: string; hasMore: boolean }>,
  options?: { initialCursor?: string },
) {
  const [items, setItems] = useState<T[]>([])
  const [cursor, setCursor] = useState<string | undefined>(options?.initialCursor)
  const [hasMore, setHasMore] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const loadMore = useCallback(async () => {
    if (isLoading || !hasMore) return

    try {
      setIsLoading(true)
      setError(null)

      const result = await fetchFn(cursor)

      setItems((prev) => [...prev, ...result.items])
      setCursor(result.nextCursor)
      setHasMore(result.hasMore)
    } catch (err) {
      setError(err as Error)
    } finally {
      setIsLoading(false)
    }
  }, [cursor, hasMore, isLoading, fetchFn])

  const reset = useCallback(() => {
    setItems([])
    setCursor(options?.initialCursor)
    setHasMore(true)
    setError(null)
  }, [options?.initialCursor])

  return {
    items,
    isLoading,
    hasMore,
    error,
    loadMore,
    reset,
  }
}
