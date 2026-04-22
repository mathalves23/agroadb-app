import type { RiskGovernanceInfo } from '@/components/investigation'

export type NormalizedPattern = {
  type: string
  confidence: number
  description: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  entities: number[]
  evidence: Record<string, unknown>
}

export type NormalizedRiskScore = {
  totalScore: number
  riskLevel: 'very_low' | 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  indicators: Array<{
    name: string
    value: number
    weight: number
    description: string
    severity: 'low' | 'medium' | 'high' | 'critical'
  }>
  patternsDetected: string[]
  recommendations: string[]
  timestamp?: string
  governance?: RiskGovernanceInfo
}

export type NormalizedNetworkGraph = {
  nodes: Array<{
    id: string
    label: string
    type: 'company' | 'property' | 'person'
    attributes: Record<string, unknown>
  }>
  edges: Array<{
    source: string
    target: string
    type: string
    weight: number
    attributes: Record<string, unknown>
  }>
  metadata?: {
    num_nodes: number
    num_edges: number
    density: number
    is_connected: boolean
  }
}

export function normalizePatterns(patterns: unknown): NormalizedPattern[] {
  const raw = patterns as Record<string, unknown> | undefined
  const list = Array.isArray(raw)
    ? (raw as unknown[])
    : Array.isArray(raw?.patterns)
      ? (raw.patterns as unknown[])
      : []

  return list.map((pattern) => {
    const item = pattern as Record<string, unknown>
    return {
      type: String(item.type ?? ''),
      confidence: Number(item.confidence ?? 0),
      description: String(item.description ?? ''),
      severity: (item.severity as 'low' | 'medium' | 'high' | 'critical') ?? 'low',
      entities: Array.isArray(item.entities) ? (item.entities as number[]) : [],
      evidence: (item.evidence as Record<string, unknown>) ?? {},
    }
  })
}

export function normalizeRiskScore(riskScore: unknown): NormalizedRiskScore | null {
  if (!riskScore || typeof riskScore !== 'object') {
    return null
  }

  const item = riskScore as Record<string, unknown>
  return {
    totalScore: Number(item.total_score ?? 0),
    riskLevel:
      ((item.risk_level as 'very_low' | 'low' | 'medium' | 'high' | 'critical') ?? 'low'),
    confidence: Number(item.confidence ?? 0),
    indicators: (Array.isArray(item.indicators) ? item.indicators : []) as NormalizedRiskScore['indicators'],
    patternsDetected: (Array.isArray(item.patterns_detected) ? item.patterns_detected : []) as string[],
    recommendations: (Array.isArray(item.recommendations) ? item.recommendations : []) as string[],
    timestamp: item.timestamp as string | undefined,
    governance: item.governance as RiskGovernanceInfo | undefined,
  }
}

export function extractNetworkGraph(networkAnalysis: unknown): NormalizedNetworkGraph {
  const source = networkAnalysis as Record<string, unknown> | undefined
  const graphData = source?.graph_data as Record<string, unknown> | undefined
  const rawNodes = (Array.isArray(graphData?.nodes) ? graphData.nodes : source?.nodes) as
    | unknown[]
    | undefined
  const rawEdges = (Array.isArray(graphData?.edges) ? graphData.edges : source?.edges) as
    | unknown[]
    | undefined

  return {
    nodes: Array.isArray(rawNodes)
      ? (rawNodes as NormalizedNetworkGraph['nodes'])
      : [],
    edges: Array.isArray(rawEdges)
      ? (rawEdges as NormalizedNetworkGraph['edges'])
      : [],
    metadata: source
      ? {
          num_nodes: Number(source.num_nodes ?? 0),
          num_edges: Number(source.num_edges ?? 0),
          density: Number(source.density ?? 0),
          is_connected: Boolean(source.is_connected ?? false),
        }
      : undefined,
  }
}
