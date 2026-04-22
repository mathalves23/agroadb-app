import {
  extractNetworkGraph,
  normalizePatterns,
  normalizeRiskScore,
} from '@/pages/investigationDetail/analysis'

describe('investigationDetail analysis helpers', () => {
  it('normalizes pattern payloads from nested responses', () => {
    const patterns = normalizePatterns({
      patterns: [
        {
          type: 'shell_company',
          confidence: '0.82',
          description: 'Relacionamento suspeito',
          severity: 'high',
          entities: [1, 2],
          evidence: { source: 'graph' },
        },
      ],
    })

    expect(patterns).toEqual([
      {
        type: 'shell_company',
        confidence: 0.82,
        description: 'Relacionamento suspeito',
        severity: 'high',
        entities: [1, 2],
        evidence: { source: 'graph' },
      },
    ])
  })

  it('normalizes risk score values into card-friendly shape', () => {
    const riskScore = normalizeRiskScore({
      total_score: '78',
      risk_level: 'high',
      confidence: '0.91',
      indicators: [{ name: 'exposure', value: 10, weight: 2, description: 'x', severity: 'medium' }],
      patterns_detected: ['shell_company'],
      recommendations: ['review'],
      timestamp: '2026-04-22T12:00:00Z',
    })

    expect(riskScore).toMatchObject({
      totalScore: 78,
      riskLevel: 'high',
      confidence: 0.91,
      patternsDetected: ['shell_company'],
      recommendations: ['review'],
      timestamp: '2026-04-22T12:00:00Z',
    })
  })

  it('extracts graph data from graph_data fallback structure', () => {
    const graph = extractNetworkGraph({
      graph_data: {
        nodes: [{ id: '1', label: 'A', type: 'company', attributes: {} }],
        edges: [{ source: '1', target: '2', type: 'owns', weight: 1, attributes: {} }],
      },
      num_nodes: 1,
      num_edges: 1,
      density: 0.5,
      is_connected: true,
    })

    expect(graph.nodes).toHaveLength(1)
    expect(graph.edges).toHaveLength(1)
    expect(graph.metadata).toEqual({
      num_nodes: 1,
      num_edges: 1,
      density: 0.5,
      is_connected: true,
    })
  })
})
