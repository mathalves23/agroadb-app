import {
  buildLegalCharts,
  buildSummaryFields,
  createSummarySources,
  findValueByKeys,
  formatSummaryValue,
} from '@/pages/investigationDetail/summary'

describe('investigation detail summary utils', () => {
  it('formats nested and array values safely', () => {
    expect(formatSummaryValue(['abc', 'def', 'ghi', 'jkl'])).toContain('...')
    expect(formatSummaryValue({ a: 1, b: 2 })).toContain('(a, b')
    expect(formatSummaryValue(null)).toBe('')
  })

  it('finds values recursively by possible keys', () => {
    const payload = { wrapper: { razao_social: 'Agro Teste' } }
    expect(findValueByKeys(payload, ['razaoSocial', 'razao_social'])).toBe('Agro Teste')
  })

  it('builds summary fields only for available values', () => {
    const result = { situacao: 'ATIVA', municipio: 'Ribeirao Preto' }
    expect(
      buildSummaryFields(result, [
        { label: 'Situação', keys: ['situacao'] },
        { label: 'Municipio', keys: ['municipio'] },
        { label: 'Fantasia', keys: ['nomeFantasia'] },
      ])
    ).toEqual([
      { label: 'Situação', value: 'ATIVA' },
      { label: 'Municipio', value: 'Ribeirao Preto' },
    ])
  })

  it('creates summary sources and legal charts', () => {
    const sources = createSummarySources({
      dataJudResult: { total: 2 },
      cnpjResult: null,
      cadinResult: null,
      sncrResult: null,
      sigefResult: null,
      sigefGeoResult: null,
      sicarResult: null,
      cndResult: null,
    })
    expect(sources[0].label).toBe('DataJud')
    expect(sources.filter((source) => source.result).length).toBe(1)

    const charts = buildLegalCharts([
      {
        id: 1,
        provider: 'datajud',
        query_type: 'search',
        query_params: {},
        result_count: 3,
        response: {},
        created_at: '2026-04-22T12:00:00Z',
      },
      {
        id: 2,
        provider: 'datajud',
        query_type: 'search',
        query_params: {},
        result_count: 1,
        response: {},
        created_at: '2026-04-22T13:00:00Z',
      },
    ])

    expect(charts.chartByProvider).toEqual([
      { name: 'datajud', consultas: 2, resultados: 4 },
    ])
    expect(charts.pieData).toEqual([{ name: 'datajud', value: 2 }])
  })
})
