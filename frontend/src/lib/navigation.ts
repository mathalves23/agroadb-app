/** Segmentos para breadcrumbs (pathname do React Router). */

export type Crumb = { to: string; label: string }

const INVESTIGATIONS = '/investigations'

export function getBreadcrumbs(pathname: string): Crumb[] {
  const path = pathname.replace(/\/+$/, '') || '/'

  if (path === '/' || path === '/dashboard') {
    return [{ to: '/dashboard', label: 'Dashboard' }]
  }

  const crumbs: Crumb[] = [{ to: '/dashboard', label: 'Início' }]

  if (path === INVESTIGATIONS) {
    crumbs.push({ to: INVESTIGATIONS, label: 'Investigações' })
    return crumbs
  }

  if (path === `${INVESTIGATIONS}/new`) {
    crumbs.push({ to: INVESTIGATIONS, label: 'Investigações' })
    crumbs.push({ to: `${INVESTIGATIONS}/new`, label: 'Nova investigação' })
    return crumbs
  }

  const detailMatch = path.match(new RegExp(`^${INVESTIGATIONS.replace(/\//g, '\\/')}\\/(\\d+)$`))
  if (detailMatch) {
    crumbs.push({ to: INVESTIGATIONS, label: 'Investigações' })
    crumbs.push({ to: path, label: `Investigação #${detailMatch[1]}` })
    return crumbs
  }

  if (path === '/settings') {
    crumbs.push({ to: '/settings', label: 'Integrações' })
    return crumbs
  }

  if (path === '/profile') {
    crumbs.push({ to: '/profile', label: 'Perfil' })
    return crumbs
  }

  if (path === '/notifications') {
    crumbs.push({ to: '/notifications', label: 'Notificações' })
    return crumbs
  }

  if (path === '/guide') {
    crumbs.push({ to: '/guide', label: 'Manual do utilizador' })
    return crumbs
  }

  crumbs.push({ to: path, label: 'Página' })
  return crumbs
}
