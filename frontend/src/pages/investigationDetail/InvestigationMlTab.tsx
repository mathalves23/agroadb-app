import { PatternDetectionCard, RiskScoreCard } from '@/components/investigation'
import type { Investigation } from '@/types/api'
import { normalizePatterns, normalizeRiskScore } from '@/pages/investigationDetail/analysis'

type Props = {
  investigation: Investigation
  isLoadingPatterns: boolean
  isLoadingRisk: boolean
  onAcknowledgeRiskReview: () => void
  patterns: unknown
  riskReviewSubmitting: boolean
  riskScore: unknown
}

export function InvestigationMlTab({
  investigation,
  isLoadingPatterns,
  isLoadingRisk,
  onAcknowledgeRiskReview,
  patterns,
  riskReviewSubmitting,
  riskScore,
}: Props) {
  if (isLoadingRisk || isLoadingPatterns) {
    return (
      <div className="rounded-xl border border-gray-100 bg-white p-12 text-center text-gray-500">
        A carregar análise ML…
      </div>
    )
  }

  const normalizedRiskScore = normalizeRiskScore(riskScore)
  const normalizedPatterns = normalizePatterns(patterns)

  return (
    <div className="space-y-6">
      {normalizedRiskScore && (
        <RiskScoreCard
          totalScore={normalizedRiskScore.totalScore}
          riskLevel={normalizedRiskScore.riskLevel}
          confidence={normalizedRiskScore.confidence}
          indicators={normalizedRiskScore.indicators}
          patternsDetected={normalizedRiskScore.patternsDetected}
          recommendations={normalizedRiskScore.recommendations}
          timestamp={normalizedRiskScore.timestamp}
          governance={normalizedRiskScore.governance}
          riskReviewRecordedAt={investigation.risk_score_reviewed_at ?? null}
          riskReviewerName={investigation.risk_score_reviewer_name ?? null}
          canAcknowledgeRiskReview={investigation.can_acknowledge_risk_score_review === true}
          riskReviewSubmitting={riskReviewSubmitting}
          onAcknowledgeRiskReview={onAcknowledgeRiskReview}
        />
      )}

      <PatternDetectionCard
        patterns={normalizedPatterns}
        totalPatterns={normalizedPatterns.length}
        criticalPatterns={normalizedPatterns.filter((pattern) => pattern.severity === 'critical').length}
      />

      {!normalizedRiskScore && normalizedPatterns.length === 0 && (
        <div className="rounded-xl border border-gray-100 bg-white p-12 text-center text-gray-500">
          Sem dados de ML para esta investigação. Execute análises no backend ou tente mais tarde.
        </div>
      )}
    </div>
  )
}
