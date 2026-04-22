import { AlertTriangle, Home, RefreshCcw } from 'lucide-react'

interface ErrorStateProps {
  title?: string
  description?: string
  onRetry?: () => void
  onGoHome?: () => void
  details?: string
}

export function ErrorState({
  title = 'Ops! Algo deu errado',
  description = 'Ocorreu um erro inesperado. Tente recarregar a página.',
  onRetry,
  onGoHome,
  details,
}: ErrorStateProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-white p-4">
      <div className="max-w-md w-full rounded-2xl border border-gray-200 bg-white p-8 shadow-lg">
        <div className="mb-4 flex justify-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-rose-50">
            <AlertTriangle className="h-8 w-8 text-rose-500" />
          </div>
        </div>

        <h2 className="text-center text-xl font-bold text-gray-900">{title}</h2>
        <p className="mt-2 text-center text-sm text-gray-500">{description}</p>

        {details && (
          <details className="mt-6">
            <summary className="cursor-pointer text-xs text-gray-400 hover:text-gray-600">
              Detalhes (dev)
            </summary>
            <div className="mt-2 max-h-48 overflow-auto rounded-lg border border-gray-100 bg-gray-50 p-3 font-mono text-[10px] text-rose-600">
              <pre className="whitespace-pre-wrap">{details}</pre>
            </div>
          </details>
        )}

        <div className="mt-6 flex gap-3">
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-emerald-700"
            >
              <RefreshCcw className="h-4 w-4" />
              Tentar novamente
            </button>
          )}
          {onGoHome && (
            <button
              type="button"
              onClick={onGoHome}
              className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-200"
            >
              <Home className="h-4 w-4" />
              Ir para início
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
