import { getBreadcrumbs } from '@/lib/navigation'

describe('getBreadcrumbs', () => {
  it('retorna só Dashboard na home', () => {
    expect(getBreadcrumbs('/dashboard')).toEqual([{ to: '/dashboard', label: 'Dashboard' }])
    expect(getBreadcrumbs('/')).toEqual([{ to: '/dashboard', label: 'Dashboard' }])
  })

  it('monta trilha para investigações e detalhe', () => {
    expect(getBreadcrumbs('/investigations')).toEqual([
      { to: '/dashboard', label: 'Início' },
      { to: '/investigations', label: 'Investigações' },
    ])
    expect(getBreadcrumbs('/investigations/new')).toEqual([
      { to: '/dashboard', label: 'Início' },
      { to: '/investigations', label: 'Investigações' },
      { to: '/investigations/new', label: 'Nova investigação' },
    ])
    expect(getBreadcrumbs('/investigations/42')).toEqual([
      { to: '/dashboard', label: 'Início' },
      { to: '/investigations', label: 'Investigações' },
      { to: '/investigations/42', label: 'Investigação #42' },
    ])
  })

  it('cobre definições e conta', () => {
    expect(getBreadcrumbs('/settings').map((c) => c.label)).toEqual(['Início', 'Integrações'])
    expect(getBreadcrumbs('/profile').map((c) => c.label)).toEqual(['Início', 'Perfil'])
    expect(getBreadcrumbs('/notifications').map((c) => c.label)).toEqual(['Início', 'Notificações'])
  })
})
