import { ArrowLeft, RefreshCw, Settings } from 'lucide-react'

type Props = {
  integrationCount: number
  isLoading: boolean
  onBack: () => void
  onRefresh: () => void
}

export function SettingsHeader({ integrationCount, isLoading, onBack, onRefresh }: Props) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-4">
        <button onClick={onBack} className="flex items-center gap-2 text-gray-500 transition hover:text-gray-900">
          <ArrowLeft className="h-5 w-5" />
          <span className="text-sm">Voltar</span>
        </button>
        <div>
          <h1 className="flex items-center gap-3 text-2xl font-bold text-gray-900">
            <Settings className="h-6 w-6 text-emerald-600" />
            Integrações
          </h1>
          <p className="mt-0.5 text-sm text-gray-500">{integrationCount} bases de dados configuradas</p>
        </div>
      </div>
      <button
        onClick={onRefresh}
        disabled={isLoading}
        className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
      >
        <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
        Atualizar Status
      </button>
    </div>
  )
}
