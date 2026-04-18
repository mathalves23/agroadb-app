/**
 * HOC para lazy-load de páginas/componentes com Suspense.
 * Mantido em ficheiro dedicado para react-refresh (apenas este export não-componente aqui).
 */
import React, { Suspense, lazy, type ComponentType } from 'react'
import { Loading } from '@/components/Loading'

export const lazyLoad = <T extends ComponentType<Record<string, unknown>>>(
  importFunc: () => Promise<{ default: T }>,
  fallback?: React.ReactNode,
) => {
  const LazyComponent = lazy(importFunc) as React.LazyExoticComponent<ComponentType<Record<string, unknown>>>

  return (props: React.ComponentProps<T>) => (
    <Suspense fallback={fallback || <Loading type="spinner" size="lg" fullScreen />}>
      <LazyComponent {...(props as Record<string, unknown>)} />
    </Suspense>
  )
}
