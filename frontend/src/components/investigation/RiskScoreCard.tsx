import { AlertTriangle, CheckCircle, TrendingUp, Shield, Clock } from 'lucide-react'

interface RiskIndicator {
  name: string
  value: number
  weight: number
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
}

interface RiskScoreCardProps {
  totalScore: number
  riskLevel: 'very_low' | 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  indicators: RiskIndicator[]
  patternsDetected: string[]
  recommendations: string[]
  timestamp?: string
}

export function RiskScoreCard({
  totalScore,
  riskLevel,
  confidence,
  indicators,
  patternsDetected,
  recommendations,
  timestamp,
}: RiskScoreCardProps) {
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
