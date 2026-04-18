import { useState, useEffect, useRef } from 'react'

/**
 * Hook para detectar se elemento está visível (IntersectionObserver).
 */
export function useInView(options?: IntersectionObserverInit) {
  const [isInView, setIsInView] = useState(false)
  const ref = useRef<HTMLElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => setIsInView(entry.isIntersecting), options)

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => observer.disconnect()
  }, [options])

  return [ref, isInView] as const
}
