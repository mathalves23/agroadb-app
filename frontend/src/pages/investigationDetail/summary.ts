import type { LegalQueryEntry } from '@/services/legalService'

export type SummaryField = { label: string; keys: string[] }
export type SummarySource = {
  label: string
  result: Record<string, unknown> | null
  fields: SummaryField[]
}

export function formatSummaryValue(value: unknown): string {
  if (value === null || value === undefined) {
    return ''
  }
  if (typeof value === 'string') {
    return value
  }
  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }
  if (Array.isArray(value)) {
    const preview = value
      .slice(0, 3)
      .map((item) => formatSummaryValue(item))
      .filter(Boolean)
    return preview.length ? `${preview.join(' | ')}${value.length > 3 ? ' ...' : ''}` : ''
  }
  if (typeof value === 'object') {
    const keys = Object.keys(value as Record<string, unknown>)
    return keys.length ? `(${keys.slice(0, 4).join(', ')}${keys.length > 4 ? ', ...' : ''})` : ''
  }
  return String(value)
}

export function findValueByKeys(
  payload: unknown,
  keys: string[],
  depth = 0,
  visited = new Set<unknown>()
): unknown {
  if (!payload || typeof payload !== 'object') {
    return undefined
  }
  if (visited.has(payload)) {
    return undefined
  }
  visited.add(payload)
  const obj = payload as Record<string, unknown>
  const lowerKeys = Object.keys(obj).reduce<Record<string, string>>((acc, key) => {
    acc[key.toLowerCase()] = key
    return acc
  }, {})

  for (const key of keys) {
    const realKey = lowerKeys[key.toLowerCase()]
    if (realKey !== undefined) {
      return obj[realKey]
    }
  }

  if (depth > 4) {
    return undefined
  }

  for (const value of Object.values(obj)) {
    if (typeof value === 'object' && value !== null) {
      const found = findValueByKeys(value, keys, depth + 1, visited)
      if (found !== undefined) {
        return found
      }
    }
  }

  return undefined
}

export function buildSummaryFields(
  result: Record<string, unknown> | null,
  fields: SummaryField[]
): Array<{ label: string; value: string }> {
  if (!result) {
    return []
  }

  return fields
    .map((field) => {
      const value = findValueByKeys(result, field.keys)
      const formatted = formatSummaryValue(value)
      return formatted ? { label: field.label, value: formatted } : null
    })
    .filter(Boolean) as Array<{ label: string; value: string }>
}

export function createSummarySources(results: {
  dataJudResult: Record<string, unknown> | null
  cnpjResult: Record<string, unknown> | null
  cadinResult: Record<string, unknown> | null
  sncrResult: Record<string, unknown> | null
  sigefResult: Record<string, unknown> | null
  sigefGeoResult: Record<string, unknown> | null
  sicarResult: Record<string, unknown> | null
  cndResult: Record<string, unknown> | null
}): SummarySource[] {
  return [
    {
      label: 'DataJud',
      result: results.dataJudResult,
      fields: [
        { label: 'Processos', keys: ['hits', 'processos'] },
        { label: 'Total', keys: ['total'] },
      ],
    },
    {
      label: 'CNPJ (Conecta)',
      result: results.cnpjResult,
      fields: [
        { label: 'Razão social', keys: ['razaoSocial', 'razao_social', 'nomeEmpresarial', 'nome'] },
        { label: 'Nome fantasia', keys: ['nomeFantasia', 'nome_fantasia'] },
        { label: 'Situação', keys: ['situacao', 'situacaoCadastral', 'status'] },
        { label: 'Atividade', keys: ['atividadePrincipal', 'cnaePrincipal', 'cnae'] },
        { label: 'Endereço', keys: ['endereco', 'logradouro', 'enderecoCompleto'] },
        { label: 'Municipio/UF', keys: ['municipio', 'cidade', 'uf', 'estado'] },
      ],
    },
    {
      label: 'CADIN (Conecta)',
      result: results.cadinResult,
      fields: [
        { label: 'Situação', keys: ['situacao', 'status', 'possuiRestricao'] },
        { label: 'Órgão', keys: ['orgao', 'orgaoResponsavel'] },
        { label: 'Data', keys: ['data', 'dataRegistro', 'dataAtualizacao'] },
        { label: 'Descrição', keys: ['descricao', 'motivo'] },
      ],
    },
    {
      label: 'SNCR (Conecta)',
      result: results.sncrResult,
      fields: [
        { label: 'Código imóvel', keys: ['codigoImovel', 'codigo_imovel', 'imovel'] },
        { label: 'Nome imóvel', keys: ['nomeImovel', 'nome_imovel'] },
        { label: 'Situação', keys: ['situacao', 'status'] },
        { label: 'Área (ha)', keys: ['areaHa', 'area_ha', 'area'] },
        { label: 'Município/UF', keys: ['municipio', 'uf', 'estado'] },
      ],
    },
    {
      label: 'SIGEF Parcelas',
      result: results.sigefResult,
      fields: [
        { label: 'Resultado', keys: ['resultados', 'resultados_retornados'] },
        { label: 'Área (ha)', keys: ['area_ha', 'areaHa', 'area'] },
        { label: 'Matrícula', keys: ['matricula'] },
        { label: 'Detentor', keys: ['detentor', 'nome'] },
      ],
    },
    {
      label: 'SIGEF GEO (Conecta)',
      result: results.sigefGeoResult,
      fields: [
        { label: 'Código parcela', keys: ['parcelaCodigo', 'codigo_parcela'] },
        { label: 'Código imóvel', keys: ['codigoImovel', 'codigo_imovel'] },
        { label: 'Situação', keys: ['status', 'situacao'] },
        { label: 'Área (ha)', keys: ['areaHa', 'area_ha', 'area'] },
      ],
    },
    {
      label: 'SICAR (Conecta)',
      result: results.sicarResult,
      fields: [
        { label: 'Situação', keys: ['situacao', 'status'] },
        { label: 'Imóvel', keys: ['imovel', 'codigoImovel', 'codigo_imovel'] },
        { label: 'Município/UF', keys: ['municipio', 'uf', 'estado'] },
      ],
    },
    {
      label: 'CND (Conecta)',
      result: results.cndResult,
      fields: [
        { label: 'Situação', keys: ['situacao', 'status', 'resultado'] },
        { label: 'Validade', keys: ['validade', 'dataValidade'] },
        { label: 'Emitente', keys: ['orgao', 'emissor'] },
      ],
    },
  ]
}

export function buildLegalCharts(legalQueries: LegalQueryEntry[] | undefined) {
  const queries = legalQueries ?? []

  const groupedProviders: Record<string, { queries: number; results: number }> = {}
  const groupedDates: Record<string, number> = {}
  const pieGrouped: Record<string, number> = {}

  for (const query of queries) {
    if (!groupedProviders[query.provider]) {
      groupedProviders[query.provider] = { queries: 0, results: 0 }
    }
    groupedProviders[query.provider].queries += 1
    groupedProviders[query.provider].results += query.result_count || 0

    const day = new Date(query.created_at).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
    })
    groupedDates[day] = (groupedDates[day] || 0) + 1
    pieGrouped[query.provider] = (pieGrouped[query.provider] || 0) + 1
  }

  return {
    chartByProvider: Object.entries(groupedProviders).map(([provider, data]) => ({
      name: provider,
      consultas: data.queries,
      resultados: data.results,
    })),
    chartByDate: Object.entries(groupedDates)
      .slice(-14)
      .map(([date, count]) => ({ date, consultas: count })),
    pieData: Object.entries(pieGrouped).map(([name, value]) => ({ name, value })),
  }
}
