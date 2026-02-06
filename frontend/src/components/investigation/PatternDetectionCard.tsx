import { AlertCircle, Search, Zap, Users } from 'lucide-react'

interface Pattern {
  type: string
  confidence: number
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  entities: number[]
  evidence: Record<string, any>
}

interface PatternDetectionCardProps {
  patterns: Pattern[]
  totalPatterns: number
  criticalPatterns: number
}

export function PatternDetectionCard({
  patterns,
  totalPatterns,
  criticalPatterns,
}: PatternDetectionCardProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low':
        return 'bg-blue-100 text-blue-700 border-blue-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'high':
        return 'bg-orange-100 text-orange-700 border-orange-200'
      case 'critical':
        return 'bg-red-100 text-red-700 border-red-200'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '🔴'
      case 'high':
        return '🟠'
      case 'medium':
        return '🟡'
      case 'low':
        return '🔵'
      default:
        return '⚪'
    }
  }

  const getPatternTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      laranja_same_address: 'Empresas no mesmo endereço (Laranja)',
      laranja_low_capital: 'Capital social muito baixo',
      laranja_rapid_creation: 'Criação rápida de empresas',
      suspicious_network_inactive: 'Alta taxa de empresas inativas',
      suspicious_network_same_activity: 'Empresas com mesma atividade',
      circular_transactions: 'Transações circulares',
      abnormal_concentration_geographic: 'Concentração geográfica anormal',
      abnormal_concentration_size: 'Propriedades com área atípica',
      temporal_anomaly_weekend: 'Empresas abertas em fins de semana',
      temporal_anomaly_same_day: 'Empresas abertas no mesmo dia',
    }
    return labels[type] || type
  }

  // Agrupar por severidade
  const criticalPatternsFiltered = patterns.filter((p) => p.severity === 'critical')
  const highPatternsFiltered = patterns.filter((p) => p.severity === 'high')
  const mediumPatternsFiltered = patterns.filter((p) => p.severity === 'medium')
  const lowPatternsFiltered = patterns.filter((p) => p.severity === 'low')

  return (
    <div className="space-y-6">
      {/* Resumo */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-100 rounded-lg p-2">
              <Search className="h-4 w-4 text-indigo-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Total de Padrões</p>
              <p className="text-2xl font-semibold text-gray-900">{totalPatterns}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-red-200 p-4">
          <div className="flex items-center gap-2">
            <div className="bg-red-100 rounded-lg p-2">
              <AlertCircle className="h-4 w-4 text-red-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Críticos</p>
              <p className="text-2xl font-semibold text-red-600">{criticalPatternsFiltered.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-orange-200 p-4">
          <div className="flex items-center gap-2">
            <div className="bg-orange-100 rounded-lg p-2">
              <Zap className="h-4 w-4 text-orange-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Alta Severidade</p>
              <p className="text-2xl font-semibold text-orange-600">{highPatternsFiltered.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center gap-2">
            <div className="bg-gray-100 rounded-lg p-2">
              <Users className="h-4 w-4 text-gray-600" />
            </div>
            <div>
              <p className="text-xs text-gray-500">Média/Baixa</p>
              <p className="text-2xl font-semibold text-gray-600">
                {mediumPatternsFiltered.length + lowPatternsFiltered.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Padrões por Severidade */}
      {patterns.length === 0 ? (
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-12 text-center">
          <Search className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-4 text-base font-medium text-gray-900">
            Nenhum padrão suspeito detectado
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            A análise não identificou padrões suspeitos nesta investigação.
          </p>
        </div>
      ) : (
        <>
          {/* Críticos */}
          {criticalPatternsFiltered.length > 0 && (
            <div className="bg-white rounded-xl border border-red-200 p-6">
              <h4 className="text-lg font-semibold text-red-900 mb-4 flex items-center gap-2">
                🔴 Padrões Críticos ({criticalPatternsFiltered.length})
              </h4>
              <div className="space-y-3">
                {criticalPatternsFiltered.map((pattern, idx) => (
                  <PatternCard key={idx} pattern={pattern} />
                ))}
              </div>
            </div>
          )}

          {/* Alta Severidade */}
          {highPatternsFiltered.length > 0 && (
            <div className="bg-white rounded-xl border border-orange-200 p-6">
              <h4 className="text-lg font-semibold text-orange-900 mb-4 flex items-center gap-2">
                🟠 Alta Severidade ({highPatternsFiltered.length})
              </h4>
              <div className="space-y-3">
                {highPatternsFiltered.map((pattern, idx) => (
                  <PatternCard key={idx} pattern={pattern} />
                ))}
              </div>
            </div>
          )}

          {/* Média Severidade */}
          {mediumPatternsFiltered.length > 0 && (
            <div className="bg-white rounded-xl border border-yellow-200 p-6">
              <h4 className="text-lg font-semibold text-yellow-900 mb-4 flex items-center gap-2">
                🟡 Média Severidade ({mediumPatternsFiltered.length})
              </h4>
              <div className="space-y-3">
                {mediumPatternsFiltered.map((pattern, idx) => (
                  <PatternCard key={idx} pattern={pattern} />
                ))}
              </div>
            </div>
          )}

          {/* Baixa Severidade */}
          {lowPatternsFiltered.length > 0 && (
            <div className="bg-white rounded-xl border border-blue-200 p-6">
              <h4 className="text-lg font-semibold text-blue-900 mb-4 flex items-center gap-2">
                🔵 Baixa Severidade ({lowPatternsFiltered.length})
              </h4>
              <div className="space-y-3">
                {lowPatternsFiltered.map((pattern, idx) => (
                  <PatternCard key={idx} pattern={pattern} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

function PatternCard({ pattern }: { pattern: Pattern }) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low':
        return 'bg-blue-100 text-blue-700 border-blue-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'high':
        return 'bg-orange-100 text-orange-700 border-orange-200'
      case 'critical':
        return 'bg-red-100 text-red-700 border-red-200'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '🔴'
      case 'high':
        return '🟠'
      case 'medium':
        return '🟡'
      case 'low':
        return '🔵'
      default:
        return '⚪'
    }
  }

  const getPatternTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      laranja_same_address: 'Empresas no mesmo endereço (Laranja)',
      laranja_low_capital: 'Capital social muito baixo',
      laranja_rapid_creation: 'Criação rápida de empresas',
      suspicious_network_inactive: 'Alta taxa de empresas inativas',
      suspicious_network_same_activity: 'Empresas com mesma atividade',
      circular_transactions: 'Transações circulares',
      abnormal_concentration_geographic: 'Concentração geográfica anormal',
      abnormal_concentration_size: 'Propriedades com área atípica',
      temporal_anomaly_weekend: 'Empresas abertas em fins de semana',
      temporal_anomaly_same_day: 'Empresas abertas no mesmo dia',
    }
    return labels[type] || type
  }

  return (
    <div className={`border rounded-lg p-4 ${getSeverityColor(pattern.severity)}`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">{getSeverityIcon(pattern.severity)}</span>
          <div>
            <h5 className="text-sm font-semibold">{getPatternTypeLabel(pattern.type)}</h5>
            <p className="text-sm mt-1">{pattern.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className={`px-2 py-1 rounded-full font-medium ${getSeverityColor(pattern.severity)}`}>
            Confiança: {Math.round(pattern.confidence * 100)}%
          </span>
        </div>
      </div>

      {/* Evidências */}
      {pattern.evidence && Object.keys(pattern.evidence).length > 0 && (
        <div className="mt-3 pt-3 border-t border-current border-opacity-20">
          <p className="text-xs font-semibold mb-2">Evidências:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {Object.entries(pattern.evidence)
              .filter(([key]) => !['companies', 'sequences', 'cycles'].includes(key))
              .map(([key, value]) => (
                <div key={key} className="text-xs">
                  <span className="opacity-70 capitalize">{key.replace(/_/g, ' ')}: </span>
                  <span className="font-medium">
                    {typeof value === 'number' && value > 1000
                      ? value.toLocaleString('pt-BR')
                      : String(value)}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Entidades envolvidas */}
      {pattern.entities && pattern.entities.length > 0 && (
        <div className="mt-2 text-xs opacity-70">
          <span>Entidades envolvidas: {pattern.entities.length}</span>
        </div>
      )}
    </div>
  )
}
