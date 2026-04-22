import {
  createInvestigationItems,
  createNavigationItems,
  filterCommandPaletteItems,
} from '@/lib/commandPalette'

describe('command palette helpers', () => {
  it('creates default navigation entries', () => {
    const items = createNavigationItems()
    expect(items.some((item) => item.href === '/notifications')).toBe(true)
    expect(items.some((item) => item.href === '/guide')).toBe(true)
    expect(items[0].section).toBe('shortcuts')
  })

  it('maps investigations into searchable command items', () => {
    const items = createInvestigationItems([
      {
        id: 12,
        user_id: 1,
        target_name: 'Fazenda Horizonte',
        target_cpf_cnpj: '12345678901',
        target_description: 'Caso prioritário',
        status: 'in_progress',
        priority: 1,
        properties_found: 0,
        lease_contracts_found: 0,
        companies_found: 0,
        created_at: '2026-04-22T00:00:00Z',
        updated_at: '2026-04-22T00:00:00Z',
      },
    ])

    expect(items[0]).toMatchObject({
      href: '/investigations/12',
      title: 'Fazenda Horizonte',
      section: 'investigations',
    })
  })

  it('filters using titles, subtitles and keywords', () => {
    const items = [
      ...createNavigationItems(),
      ...createInvestigationItems([
        {
          id: 3,
          user_id: 1,
          target_name: 'Operação Verde',
          target_cpf_cnpj: '99999999999',
          target_description: 'Monitoramento rural',
          status: 'pending',
          priority: 2,
          properties_found: 0,
          lease_contracts_found: 0,
          companies_found: 0,
          created_at: '2026-04-22T00:00:00Z',
          updated_at: '2026-04-22T00:00:00Z',
        },
      ]),
    ]

    expect(filterCommandPaletteItems(items, 'manual')).toHaveLength(1)
    expect(filterCommandPaletteItems(items, 'verde')[0].href).toBe('/investigations/3')
  })

  it('prioritizes exact and high-value shortcut matches first', () => {
    const items = [
      ...createNavigationItems(),
      ...createInvestigationItems([
        {
          id: 9,
          user_id: 1,
          target_name: 'Dashboard Rural',
          target_cpf_cnpj: '11111111111',
          target_description: 'Caso relacionado',
          status: 'pending',
          priority: 1,
          properties_found: 0,
          lease_contracts_found: 0,
          companies_found: 0,
          created_at: '2026-04-22T00:00:00Z',
          updated_at: '2026-04-22T00:00:00Z',
        },
      ]),
    ]

    expect(filterCommandPaletteItems(items, 'dashboard')[0].href).toBe('/dashboard')
  })
})
