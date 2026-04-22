import type { IntegrationStatus } from '@/services/legalService'
import type { IntegrationInfo } from '@/pages/settings/catalog'

const statusMap: Record<string, string> = {
  BrasilAPI: 'brasilapi',
  IBGE: 'ibge',
  'Banco Central': 'bcb',
  'TSE (Dados Abertos)': 'tse',
  'CVM (Dados Abertos)': 'cvm',
  'dados.gov.br': 'dados_gov',
  'REDESIM / ReceitaWS': 'redesim',
  'Receita Federal (CPF)': 'receita_cpf',
  'Receita Federal (CNPJ)': 'receita_cnpj',
  TJMG: 'tjmg',
  'BNMP / CNJ': 'bnmp_cnj',
  'SEEU / CNJ': 'seeu_cnj',
  'SICAR Público': 'sicar_publico',
  'SIGEF Público': 'sigef_publico',
  'Antecedentes MG': 'antecedentes_mg',
  'Caixa FGTS / CRF': 'caixa_fgts',
  'Portal da Transparência (CGU)': 'portal_transparencia',
  'DataJud (CNJ)': 'datajud',
  'SNCR (Conecta)': 'conecta_sncr',
  'SIGEF (Conecta)': 'conecta_sigef',
  'SICAR (Conecta)': 'conecta_sicar',
  'SIGEF GEO (Conecta)': 'conecta_sigef_geo',
  'SNCCI (Conecta)': 'conecta_sncci',
  'CNPJ / RFB (Conecta)': 'conecta_cnpj',
  'CND / RFB (Conecta)': 'conecta_cnd',
  'CADIN (Conecta)': 'conecta_cadin',
}

function resolveStatusEntry(
  integrationStatus: IntegrationStatus | undefined,
  name: string
): { configured?: boolean; auth_required?: boolean } | undefined {
  if (!integrationStatus) {
    return undefined
  }
  const key = statusMap[name]
  if (!key) {
    return undefined
  }

  if (key.startsWith('conecta_')) {
    const conecta = integrationStatus.conecta ?? {}
    const nestedKey = key.replace('conecta_', '') as keyof typeof conecta
    return { configured: Boolean(conecta[nestedKey]), auth_required: true }
  }

  return (integrationStatus as Record<string, { configured?: boolean; auth_required?: boolean } | undefined>)[key]
}

export function getIntegrationStatusLabel(
  integrationStatus: IntegrationStatus | undefined,
  name: string
): 'active' | 'inactive' | 'partial' {
  const entry = resolveStatusEntry(integrationStatus, name)
  if (!entry) {
    return 'active'
  }
  if (entry.configured === true) {
    return 'active'
  }
  if (entry.configured === false && entry.auth_required === false) {
    return 'active'
  }
  return 'inactive'
}

export function buildIntegrationCounts(items: IntegrationInfo[]) {
  return {
    all: items.length,
    free: items.filter((item) => item.category === 'free').length,
    key: items.filter((item) => item.category === 'key').length,
    conecta: items.filter((item) => item.category === 'conecta').length,
  }
}

export function filterIntegrationsByCategory(
  items: IntegrationInfo[],
  category: 'all' | 'free' | 'key' | 'conecta'
) {
  return category === 'all' ? items : items.filter((item) => item.category === category)
}
