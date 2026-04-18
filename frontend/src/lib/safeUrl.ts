/**
 * Evita javascript:/data: em links renderizados a partir de conteúdo externo (ex.: markdown).
 */
export function isSafeHttpUrl(href: string | undefined): boolean {
  if (!href || href.trim() === '') return false
  const trimmed = href.trim()
  const lower = trimmed.toLowerCase()
  if (lower.startsWith('javascript:') || lower.startsWith('data:') || lower.startsWith('vbscript:')) {
    return false
  }
  try {
    const u = new URL(trimmed, typeof window !== 'undefined' ? window.location.origin : 'https://example.org')
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
}
