import { Database } from 'lucide-react'

type Props = {
  warnings: string[]
}

export function LegalConfigWarning({ warnings }: Props) {
  if (warnings.length === 0) {
    return null
  }

  return (
    <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
      <div className="mt-0.5 shrink-0 rounded-lg bg-amber-100 p-1.5">
        <Database className="h-4 w-4 text-amber-600" />
      </div>
      <div>
        <p className="text-xs font-semibold text-amber-800">Bases sem credencial configurada</p>
        <div className="mt-1.5 flex flex-wrap gap-1.5">
          {warnings.map((warning) => (
            <span key={warning} className="rounded-md bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700">
              {warning}
            </span>
          ))}
        </div>
        <p className="mt-1.5 text-[10px] text-amber-600">
          Configure as API keys no arquivo .env do backend para habilitar essas bases.
        </p>
      </div>
    </div>
  )
}
