import { integrations } from '@/pages/settings/catalog'
import {
  buildIntegrationCounts,
  filterIntegrationsByCategory,
  getIntegrationStatusLabel,
} from '@/pages/settings/utils'

describe('settings utils', () => {
  it('builds category counts from integration catalog', () => {
    const counts = buildIntegrationCounts(integrations)
    expect(counts.all).toBe(integrations.length)
    expect(counts.free).toBeGreaterThan(0)
    expect(counts.conecta).toBeGreaterThan(0)
  })

  it('filters integrations by category', () => {
    const items = filterIntegrationsByCategory(integrations, 'key')
    expect(items.every((item) => item.category === 'key')).toBe(true)
  })

  it('resolves conecta status using nested flags', () => {
    expect(
      getIntegrationStatusLabel(
        {
          datajud: { configured: true, api_url: '' },
          sigef_parcelas: { configured: false, api_url: '' },
          conecta: { sncr: true, sigef: false, sicar: false, sigef_geo: false, sncci: false, cnpj: false, cnd: false, cadin: false },
        },
        'SNCR (Conecta)'
      )
    ).toBe('active')
  })
})
