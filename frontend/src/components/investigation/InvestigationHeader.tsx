import {
  User,
  CheckCircle2,
  XCircle,
  Activity,
  Clock,
} from 'lucide-react'
import { formatCPFCNPJ, formatDate } from '@/lib/utils'

interface Investigation {
  target_name: string
  target_cpf_cnpj?: string
  status: string
  created_at: string
  completed_at?: string
  priority: number
}

interface InvestigationHeaderProps {
  investigation: Investigation
  onBack?: () => void
}

export function InvestigationHeader({ investigation }: InvestigationHeaderProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:justify-between sm:items-start">
        <div className="flex items-start gap-4">
          <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-3 shrink-0 shadow-sm">
            <User className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900" role="heading" aria-level={1}>{investigation.target_name}</h1>
            {investigation.target_cpf_cnpj && (
              <p className="mt-0.5 font-mono text-sm text-gray-500">
                {formatCPFCNPJ(investigation.target_cpf_cnpj)}
              </p>
            )}
          </div>
        </div>

        <div className="flex flex-col items-end gap-2 shrink-0">
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${
              investigation.status === 'completed'
                ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200'
                : investigation.status === 'in_progress'
                ? 'bg-blue-50 text-blue-700 ring-1 ring-blue-200'
                : investigation.status === 'failed'
                ? 'bg-red-50 text-red-700 ring-1 ring-red-200'
                : 'bg-gray-50 text-gray-600 ring-1 ring-gray-200'
            }`}
            aria-label={`Status: ${
              investigation.status === 'completed'
                ? 'Concluída'
                : investigation.status === 'in_progress'
                ? 'Em Andamento'
                : investigation.status === 'failed'
                ? 'Falhou'
                : 'Pendente'
            }`}
          >
            {investigation.status === 'completed' && <CheckCircle2 className="h-3.5 w-3.5" />}
            {investigation.status === 'in_progress' && <Activity className="h-3.5 w-3.5" />}
            {investigation.status === 'failed' && <XCircle className="h-3.5 w-3.5" />}
            {investigation.status === 'pending' && <Clock className="h-3.5 w-3.5" />}
            {investigation.status === 'completed'
              ? 'Concluída'
              : investigation.status === 'in_progress'
              ? 'Em Andamento'
              : investigation.status === 'failed'
              ? 'Falhou'
              : 'Pendente'}
          </span>
          <div className="text-xs text-gray-400 text-right">
            <span>Criada em {formatDate(investigation.created_at)}</span>
            {investigation.completed_at && (
              <span className="ml-2">• Concluída em {formatDate(investigation.completed_at)}</span>
            )}
          </div>
          <div className="flex items-center gap-1.5">
            {[1, 2, 3, 4, 5].map((level) => (
              <div
                key={level}
                className={`h-1.5 w-4 rounded-full ${
                  level <= investigation.priority ? 'bg-amber-400' : 'bg-gray-200'
                }`}
              />
            ))}
            <span className="text-[10px] text-gray-400 ml-1">P{investigation.priority}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
