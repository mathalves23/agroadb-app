/**
 * Error Boundary - Captura e Exibe Erros de Forma Elegante
 *
 * Componente que captura erros em tempo de execução e exibe UI amigável.
 * Sem dependência externa (framer-motion removida).
 */
import type { ErrorInfo, ReactNode } from 'react';
import React, { Component } from 'react'
import { ErrorState } from '@/components/feedback'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ error, errorInfo })
    this.props.onError?.(error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback

      return (
        <ErrorState
          onRetry={this.handleReset}
          onGoHome={() => {
            window.location.href = '/'
          }}
          details={
            process.env.NODE_ENV !== 'production' && this.state.error
              ? `${this.state.error.toString()}\n\n${this.state.errorInfo?.componentStack || ''}`
              : undefined
          }
        />
      )
    }

    return this.props.children
  }
}

export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null)
  React.useEffect(() => {
    if (error) throw error
  }, [error])
  return setError
}

export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) {
  return function WithErrorBoundary(props: P) {
    return (
      <ErrorBoundary {...errorBoundaryProps}>
        <WrappedComponent {...props} />
      </ErrorBoundary>
    )
  }
}
