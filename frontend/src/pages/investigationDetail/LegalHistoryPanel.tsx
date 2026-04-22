import type { LegalQueryEntry } from '@/services/legalService'

type Props = {
  legalQueries?: LegalQueryEntry[]
}

export function LegalHistoryPanel({ legalQueries }: Props) {
  return (
    <div className="rounded-lg bg-white shadow">
      <div className="border-b border-gray-200 px-6 py-4">
        <h2 className="text-lg font-medium text-gray-900">Histórico de Consultas</h2>
      </div>
      <div className="divide-y divide-gray-200">
        {legalQueries && legalQueries.length > 0 ? (
          legalQueries.map((query) => (
            <div key={query.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {query.provider} • {query.query_type}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(query.created_at).toLocaleString('pt-BR')}
                  </p>
                </div>
                <span className="text-sm text-gray-600">{query.result_count} resultados</span>
              </div>
            </div>
          ))
        ) : (
          <div className="px-6 py-4 text-sm text-gray-500">Nenhuma consulta registrada para esta investigação.</div>
        )}
      </div>
    </div>
  )
}
