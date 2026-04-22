import type { Investigation } from '@/types/api'

export type CommandPaletteItem = {
  id: string
  title: string
  subtitle?: string
  href: string
  section: 'shortcuts' | 'investigations'
  keywords: string[]
  priority?: number
}

export function createNavigationItems(): CommandPaletteItem[] {
  return [
    {
      id: 'nav-dashboard',
      title: 'Dashboard',
      subtitle: 'Visão geral da operação',
      href: '/dashboard',
      section: 'shortcuts',
      keywords: ['painel', 'home', 'overview'],
      priority: 100,
    },
    {
      id: 'nav-investigations',
      title: 'Investigações',
      subtitle: 'Lista de investigações',
      href: '/investigations',
      section: 'shortcuts',
      keywords: ['casos', 'busca', 'investigation'],
      priority: 98,
    },
    {
      id: 'nav-new-investigation',
      title: 'Nova Investigação',
      subtitle: 'Criar um novo caso',
      href: '/investigations/new',
      section: 'shortcuts',
      keywords: ['novo', 'criar', 'case'],
      priority: 99,
    },
    {
      id: 'nav-notifications',
      title: 'Notificações',
      subtitle: 'Alertas e atualizações',
      href: '/notifications',
      section: 'shortcuts',
      keywords: ['alertas', 'updates', 'inbox'],
      priority: 96,
    },
    {
      id: 'nav-guide',
      title: 'Manual do utilizador',
      subtitle: 'Guias e orientações de uso',
      href: '/guide',
      section: 'shortcuts',
      keywords: ['ajuda', 'guia', 'docs', 'documentação'],
      priority: 94,
    },
    {
      id: 'nav-settings',
      title: 'Integrações e credenciais',
      subtitle: 'Configuração, conectores e governança',
      href: '/settings',
      section: 'shortcuts',
      keywords: ['configurações', 'settings', 'api', 'credenciais'],
      priority: 93,
    },
    {
      id: 'nav-profile',
      title: 'Perfil e segurança',
      subtitle: 'Conta, sessão e preferências',
      href: '/profile',
      section: 'shortcuts',
      keywords: ['usuário', 'conta', 'perfil'],
      priority: 92,
    },
    {
      id: 'nav-dashboard-kpis',
      title: 'KPIs e métricas do dashboard',
      subtitle: 'Indicadores e visão operacional',
      href: '/dashboard',
      section: 'shortcuts',
      keywords: ['kpi', 'métricas', 'analytics', 'estatísticas'],
      priority: 88,
    },
    {
      id: 'nav-guide-onboarding',
      title: 'Ajuda e onboarding',
      subtitle: 'Fluxos principais e material de apoio',
      href: '/guide',
      section: 'shortcuts',
      keywords: ['tutorial', 'tour', 'onboarding', 'apoio'],
      priority: 87,
    },
  ]
}

export function createInvestigationItems(investigations: Investigation[]): CommandPaletteItem[] {
  return investigations.map((investigation) => ({
    id: `investigation-${investigation.id}`,
    title: investigation.target_name || `Investigação ${investigation.id}`,
    subtitle:
      investigation.target_cpf_cnpj ||
      investigation.target_description ||
      `Status: ${investigation.status}`,
    href: `/investigations/${investigation.id}`,
    section: 'investigations',
    keywords: [
      investigation.target_name,
      investigation.target_cpf_cnpj,
      investigation.target_description,
      investigation.status,
    ]
      .filter(Boolean)
      .map((value) => String(value).toLowerCase()),
    priority: 80,
  }))
}

function getMatchScore(item: CommandPaletteItem, query: string) {
  if (!query) {
    return item.priority ?? 0
  }

  const normalizedTitle = item.title.toLowerCase()
  const normalizedSubtitle = item.subtitle?.toLowerCase() ?? ''
  const haystack = [item.title, item.subtitle, item.href, ...item.keywords]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()

  let score = item.priority ?? 0
  if (normalizedTitle === query) score += 120
  else if (normalizedTitle.startsWith(query)) score += 80
  else if (normalizedTitle.includes(query)) score += 50

  if (normalizedSubtitle.startsWith(query)) score += 25
  if (haystack.includes(query)) score += 10
  if (item.section === 'shortcuts') score += 5

  return score
}

export function filterCommandPaletteItems(
  items: CommandPaletteItem[],
  query: string
): CommandPaletteItem[] {
  const normalizedQuery = query.trim().toLowerCase()
  if (!normalizedQuery) {
    return [...items].sort((a, b) => (b.priority ?? 0) - (a.priority ?? 0))
  }

  return items
    .filter((item) => {
      const haystack = [item.title, item.subtitle, item.href, ...item.keywords]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      return haystack.includes(normalizedQuery)
    })
    .sort((a, b) => getMatchScore(b, normalizedQuery) - getMatchScore(a, normalizedQuery))
}
