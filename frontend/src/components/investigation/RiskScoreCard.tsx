import { useState } from 'react'
import {
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Shield,
  Clock,
  Scale,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  UserCheck,
  Loader2,
} from 'lucide-react'

interface RiskIndicator {
  name: string
  value: number
  weight: number
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
}

export type RiskGovernanceInfo = {
  engine_version?: string
  weights_version?: string
  methodology_summary_pt?: string
  human_review_required?: boolean
  human_review_basis?: string | null
  governance_reference_url?: string | null
  legal_notice_pt?: string
  organization_id?: number | null
  calibration?: Record<string, unknown>
  indicator_weights?: Record<string, number>
  app_release_version?: string
}

interface RiskScoreCardProps {
  totalScore: number
  riskLevel: 'very_low' | 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  indicators: RiskIndicator[]
  patternsDetected: string[]
  recommendations: string[]
  timestamp?: string
  governance?: RiskGovernanceInfo | null
  riskReviewRecordedAt?: string | null
  riskReviewerName?: string | null
  canAcknowledgeRiskReview?: boolean
  riskReviewSubmitting?: boolean
  onAcknowledgeRiskReview?: () => void
}

export function RiskScoreCard({
  totalScore,
  riskLevel,
  confidence,
  indicators,
  patternsDetected,
  recommendations,
  timestamp,
  governance,
  riskReviewRecordedAt,
  riskReviewerName,
  canAcknowledgeRiskReview = false,
  riskReviewSubmitting = false,
  onAcknowledgeRiskReview,
}: RiskScoreCardProps) {
  const [govOpen, setGovOpen] = useState(false)
  // Cores e ícones por nível de risco
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'very_low':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'low':
        return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'high':
        return 'text-orange-600 bg-orange-50 border-orange-200'
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getRiskLabel = (level: string) => {
    switch (level) {
      case 'very_low':
        return 'Muito Baixo'
      case 'low':
        return 'Baixo'
      case 'medium':
        return 'Médio'
      case 'high':
        return 'Alto'
      case 'critical':
        return 'Crítico'
      default:
        return 'Desconhecido'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low':
        return 'bg-green-100 text-green-700'
      case 'medium':
        return 'bg-yellow-100 text-yellow-700'
      case 'high':
        return 'bg-orange-100 text-orange-700'
      case 'critical':
        return 'bg-red-100 text-red-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  // Score visual (0-100)
  const scorePercentage = Math.min(100, Math.max(0, totalScore))
  const scoreColor =
    scorePercentage >= 80
      ? 'text-red-600'
      : scorePercentage >= 60
      ? 'text-orange-600'
      : scorePercentage >= 40
      ? 'text-yellow-600'
      : scorePercentage >= 20
      ? 'text-blue-600'
      : 'text-green-600'

  return (
    <div className="space-y-6">
      {riskReviewRecordedAt ? (
        <div
          className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-950"
          role="status"
        >
          <div className="flex items-start gap-3">
            <UserCheck className="h-5 w-5 shrink-0 text-emerald-700 mt-0.5" aria-hidden />
            <div>
              <p className="text-sm font-semibold">Revisão humana do score registada</p>
              <p className="text-xs mt-1 text-emerald-900/90">
                {riskReviewerName ? <span>{riskReviewerName} · </span> : null}
                <time dateTime={riskReviewRecordedAt}>
                  {new Date(riskReviewRecordedAt).toLocaleString('pt-BR')}
                </time>
              </p>
            </div>
          </div>
        </div>
      ) : null}

      {governance?.human_review_required && !riskReviewRecordedAt ? (
        <div
          className="rounded-xl border border-amber-300 bg-amber-50 p-4 text-amber-950"
          role="status"
        >
          <div className="flex items-start gap-3">
            <Scale className="h-5 w-5 shrink-0 text-amber-700 mt-0.5" aria-hidden />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold">Revisão humana obrigatória (política da organização)</p>
              <p className="text-xs mt-1 text-amber-900/90 leading-relaxed">
                {governance.human_review_basis ||
                  'Valide este output automatizado antes de decisões de crédito, diligência final ou efeitos jurídicos, em linha com boas práticas da ANPD e documentação interna (RIPD/DPIA).'}
              </p>
              {governance.governance_reference_url ? (
                <a
                  href={governance.governance_reference_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs font-medium text-amber-900 underline mt-2"
                >
                  Referência de governança / RIPD
                  <ExternalLink className="h-3 w-3" />
                </a>
              ) : null}
              {!riskReviewRecordedAt && canAcknowledgeRiskReview && onAcknowledgeRiskReview ? (
                <button
                  type="button"
                  onClick={onAcknowledgeRiskReview}
                  disabled={riskReviewSubmitting}
                  className="mt-3 inline-flex items-center gap-2 rounded-lg bg-amber-800 px-3 py-2 text-xs font-semibold text-white hover:bg-amber-900 disabled:opacity-60"
                >
                  {riskReviewSubmitting ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden />
                  ) : (
                    <UserCheck className="h-3.5 w-3.5" aria-hidden />
                  )}
                  Registar revisão do score
                </button>
              ) : null}
              {!riskReviewRecordedAt && governance.human_review_required && !canAcknowledgeRiskReview ? (
                <p className="text-xs mt-2 text-amber-800/90">
                  Apenas o dono da investigação ou utilizadores com permissão de edição podem registar a
                  revisão na plataforma.
                </p>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      {!riskReviewRecordedAt &&
      canAcknowledgeRiskReview &&
      onAcknowledgeRiskReview &&
      !governance?.human_review_required ? (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-slate-800">
          <p className="text-xs text-slate-600 mb-2">
            Registo opcional: confirme na plataforma que reviu o score automatizado (trilho de auditoria
            interna).
          </p>
          <button
            type="button"
            onClick={onAcknowledgeRiskReview}
            disabled={riskReviewSubmitting}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-800 hover:bg-slate-100 disabled:opacity-60"
          >
            {riskReviewSubmitting ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden />
            ) : (
              <UserCheck className="h-3.5 w-3.5" aria-hidden />
            )}
            Registar revisão do score
          </button>
        </div>
      ) : null}

      {/* Score Principal */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div
              className={`w-24 h-24 rounded-full flex items-center justify-center ${getRiskColor(
                riskLevel
              ).replace('text-', 'bg-').replace('bg-', 'bg-opacity-20 bg-')}`}
            >
              <div className={`text-3xl font-bold ${scoreColor}`}>{Math.round(scorePercentage)}</div>
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">Score de Risco</h3>
              <div className="flex items-center gap-2 mt-1">
                <span
                  className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(
                    riskLevel
                  )}`}
                >
                  {getRiskLabel(riskLevel)}
                </span>
                <div className="flex items-center gap-1 text-sm text-gray-500">
                  <Shield className="h-4 w-4" />
                  <span>Confiança: {Math.round(confidence * 100)}%</span>
                </div>
              </div>
            </div>
          </div>

          {timestamp && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Clock className="h-4 w-4" />
              <span>{new Date(timestamp).toLocaleString('pt-BR')}</span>
            </div>
          )}
        </div>

        {/* Barra de progresso */}
        <div className="mt-6">
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${scoreColor.replace(
                'text-',
                'bg-'
              )}`}
              style={{ width: `${scorePercentage}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span>0 - Muito Baixo</span>
            <span>20 - Baixo</span>
            <span>40 - Médio</span>
            <span>60 - Alto</span>
            <span>80 - Crítico</span>
          </div>
        </div>
      </div>

      {governance && (
        <div className="bg-slate-50 rounded-xl border border-slate-200 overflow-hidden">
          <button
            type="button"
            onClick={() => setGovOpen(!govOpen)}
            className="w-full flex items-center justify-between px-4 py-3 text-left text-sm font-semibold text-slate-800 hover:bg-slate-100/80 transition"
          >
            <span className="flex items-center gap-2">
              <Scale className="h-4 w-4 text-slate-600" />
              Transparência e governança do modelo
            </span>
            {govOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
          {govOpen && (
            <div className="px-4 pb-4 space-y-3 text-xs text-slate-700 border-t border-slate-200 pt-3">
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div>
                  <dt className="text-slate-500">Versão do motor de risco</dt>
                  <dd className="font-mono font-medium">{governance.engine_version ?? '—'}</dd>
                </div>
                <div>
                  <dt className="text-slate-500">Versão dos pesos</dt>
                  <dd className="font-mono font-medium">{governance.weights_version ?? '—'}</dd>
                </div>
                <div>
                  <dt className="text-slate-500">Versão da aplicação</dt>
                  <dd className="font-mono font-medium">{governance.app_release_version ?? '—'}</dd>
                </div>
                <div>
                  <dt className="text-slate-500">Impressão digital da calibração</dt>
                  <dd className="font-mono font-medium">
                    {String((governance.calibration as Record<string, unknown> | undefined)?.config_fingerprint_sha256_16 ?? '—')}
                  </dd>
                </div>
              </dl>
              {governance.methodology_summary_pt ? (
                <p className="leading-relaxed text-slate-600">{governance.methodology_summary_pt}</p>
              ) : null}
              {governance.legal_notice_pt ? (
                <p className="text-slate-500 italic leading-relaxed">{governance.legal_notice_pt}</p>
              ) : null}
            </div>
          )}
        </div>
      )}

      {/* Indicadores de Risco */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-indigo-600" />
          Indicadores de Risco
        </h4>
        <div className="space-y-3">
          {indicators.map((indicator, idx) => (
            <div key={idx} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">
                    {indicator.description}
                  </span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-medium ${getSeverityColor(
                      indicator.severity
                    )}`}
                  >
                    {indicator.severity}
                  </span>
                </div>
                <span className="text-sm font-semibold text-gray-700">
                  {Math.round(indicator.value)}/100
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full transition-all ${getSeverityColor(
                      indicator.severity
                    ).replace('text-', 'bg-')}`}
                    style={{ width: `${indicator.value}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500 w-16 text-right">
                  Peso: {Math.round(indicator.weight * 100)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Padrões Detectados */}
      {patternsDetected.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            Padrões Detectados ({patternsDetected.length})
          </h4>
          <div className="space-y-2">
            {patternsDetected.map((pattern, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2 text-sm text-gray-700 bg-amber-50 border border-amber-200 rounded-lg p-3"
              >
                <span className="text-amber-600 font-bold">⚠️</span>
                <span>{pattern}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recomendações */}
      {recommendations.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            Recomendações ({recommendations.length})
          </h4>
          <div className="space-y-2">
            {recommendations.map((rec, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2 text-sm text-gray-700 bg-blue-50 border border-blue-200 rounded-lg p-3"
              >
                <span className="text-blue-600 font-bold">💡</span>
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
