import { formatDate } from '@/lib/utils'
import { buildSummaryFields, type SummarySource } from '@/pages/investigationDetail/summary'
import type { LegalQueryEntry } from '@/services/legalService'

type Props = {
  defaultCpfCnpj: string
  latestQuery: LegalQueryEntry | null
  onApplyCpfCnpj: () => void
  summaryCpfCnpj: string
  summarySources: SummarySource[]
  summarySourcesWithDataCount: number
  totalQueries: number
  totalResults: number
}

export function LegalSummaryOverview({
  defaultCpfCnpj,
  latestQuery,
  onApplyCpfCnpj,
  summaryCpfCnpj,
  summarySources,
  summarySourcesWithDataCount,
  totalQueries,
  totalResults,
}: Props) {
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-lg font-medium text-gray-900">Resumo do CPF/CNPJ</h2>
          <p className="text-sm text-gray-500">Consolidação das bases consultadas para o documento pesquisado.</p>
        </div>
        <div className="flex flex-col items-start gap-2 text-sm text-gray-700 md:items-end">
          <div>
            <span className="text-gray-500">Documento:</span>
            <span className="ml-2 font-medium">{summaryCpfCnpj || 'Não informado'}</span>
          </div>
          <button
            onClick={onApplyCpfCnpj}
            disabled={!defaultCpfCnpj}
            className={`rounded-md px-3 py-1 text-xs ${
              defaultCpfCnpj ? 'bg-emerald-600 text-white hover:bg-emerald-700' : 'cursor-not-allowed bg-gray-200 text-gray-500'
            }`}
          >
            Usar CPF/CNPJ da investigação
          </button>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-4">
        <MetricCard label="Consultas registradas" value={totalQueries} />
        <MetricCard label="Bases com dados" value={summarySourcesWithDataCount} />
        <MetricCard label="Resultados totais" value={totalResults} />
        <div className="rounded-lg bg-gray-50 p-4">
          <p className="text-xs text-gray-500">Última consulta</p>
          <p className="text-sm font-medium text-gray-900">{latestQuery ? formatDate(latestQuery.created_at) : '—'}</p>
          {latestQuery && <p className="text-xs text-gray-500">{latestQuery.provider} • {latestQuery.query_type}</p>}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {summarySources.map((source) => (
          <span
            key={source.label}
            className={`rounded-full px-3 py-1 text-xs ${source.result ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'}`}
          >
            {source.label}
          </span>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {summarySources.map((source) => {
          const fields = buildSummaryFields(source.result, source.fields)
          return (
            <div key={source.label} className="rounded-lg border border-gray-200 p-4 transition hover:shadow-sm">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-gray-900">{source.label}</h3>
                <span
                  className={`rounded-full px-2 py-1 text-xs ${
                    source.result ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                  }`}
                >
                  {source.result ? 'Com dados' : 'Sem dados'}
                </span>
              </div>
              {source.result ? (
                fields.length ? (
                  <div className="mt-3 space-y-2">
                    {fields.map((field) => (
                      <div key={`${source.label}-${field.label}`} className="text-xs text-gray-700">
                        <span className="text-gray-500">{field.label}:</span>
                        <span className="ml-2 font-medium text-gray-900">{field.value}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="mt-3 text-xs text-gray-500">Dados retornados. Veja o JSON completo abaixo.</div>
                )
              ) : (
                <div className="mt-3 text-xs text-gray-500">Nenhum retorno registrado para esta base.</div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-gray-50 p-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-2xl font-semibold text-gray-900">{value}</p>
    </div>
  )
}
