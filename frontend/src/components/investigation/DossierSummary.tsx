import {
  User,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Clock,
} from 'lucide-react'
import { formatCPFCNPJ, formatDateTime } from '@/lib/utils'

interface SummaryField {
  label: string
  value: string
}

interface SummarySource {
  label: string
  result: Record<string, unknown> | null
  fields: Array<{ label: string; keys: string[] }>
}

interface DossierSummaryProps {
  summaryCpfCnpj: string
  defaultCpfCnpj: string
  targetName: string
  summarySources: SummarySource[]
  latestQuery: { created_at: string; provider: string; query_type: string } | null
  onApplyCpfCnpj: () => void
  buildSummaryFields: (
    result: Record<string, unknown> | null,
    fields: Array<{ label: string; keys: string[] }>
  ) => SummaryField[]
}

export function DossierSummary({
  summaryCpfCnpj,
  defaultCpfCnpj,
  targetName,
  summarySources,
  latestQuery,
  onApplyCpfCnpj,
  buildSummaryFields,
}: DossierSummaryProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-emerald-50 rounded-lg p-2">
            <User className="h-5 w-5 text-emerald-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Dossiê do CPF/CNPJ</h2>
            <p className="text-sm text-gray-500">
              {summaryCpfCnpj || defaultCpfCnpj ? formatCPFCNPJ(defaultCpfCnpj) : 'Documento não informado'}
              {targetName && <span className="ml-2 text-gray-400">({targetName})</span>}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onApplyCpfCnpj}
            disabled={!defaultCpfCnpj}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
              defaultCpfCnpj
                ? 'bg-emerald-600 text-white hover:bg-emerald-700'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
            }`}
          >
            <RefreshCw className="h-3 w-3" />
            Preencher formulários
          </button>
        </div>
      </div>

      {/* Status das bases */}
      <div className="mt-5 flex flex-wrap gap-2">
        {summarySources.map((source) => (
          <span
            key={source.label}
            className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${
              source.result
                ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200'
                : 'bg-gray-50 text-gray-400 ring-1 ring-gray-200'
            }`}
          >
            {source.result ? (
              <CheckCircle2 className="h-3 w-3" />
            ) : (
              <XCircle className="h-3 w-3" />
            )}
            {source.label}
          </span>
        ))}
      </div>

      {/* Cards das bases com dados extraídos */}
      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {summarySources.map((source) => {
          const fields = buildSummaryFields(source.result, source.fields)
          const hasData = !!source.result
          return (
            <div
              key={source.label}
              className={`rounded-xl border p-4 transition-all ${
                hasData
                  ? 'border-emerald-200 bg-emerald-50/30 hover:shadow-md'
                  : 'border-gray-100 bg-gray-50/50'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-gray-900">{source.label}</h3>
                <span
                  className={`text-[10px] uppercase tracking-wide font-bold px-2 py-0.5 rounded ${
                    hasData ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  {hasData ? 'Encontrado' : 'Sem dados'}
                </span>
              </div>
              {hasData ? (
                fields.length > 0 ? (
                  <dl className="space-y-1.5">
                    {fields.map((field) => (
                      <div key={`${source.label}-${field.label}`} className="flex justify-between gap-2">
                        <dt className="text-xs text-gray-500 shrink-0">{field.label}</dt>
                        <dd className="text-xs font-medium text-gray-900 text-right truncate" title={field.value}>
                          {field.value}
                        </dd>
                      </div>
                    ))}
                  </dl>
                ) : (
                  <p className="text-xs text-gray-500">Dados retornados. Consulte os detalhes na aba Consultas Legais.</p>
                )
              ) : (
                <p className="text-xs text-gray-400">
                  Consulte esta base na aba Consultas Legais.
                </p>
              )}
            </div>
          )
        })}
      </div>

      {latestQuery && (
        <div className="mt-4 flex items-center gap-2 text-xs text-gray-400">
          <Clock className="h-3 w-3" />
          Última consulta: {formatDateTime(latestQuery.created_at)} — {latestQuery.provider} / {latestQuery.query_type}
        </div>
      )}
    </div>
  )
}
