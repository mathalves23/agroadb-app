import { useEffect, useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'

import { investigationService } from '@/services/investigationService'
import {
  createInvestigationItems,
  createNavigationItems,
  filterCommandPaletteItems,
  type CommandPaletteItem,
} from '@/lib/commandPalette'

function sectionLabel(section: CommandPaletteItem['section']) {
  return section === 'shortcuts' ? 'Áreas principais' : 'Investigações recentes'
}

function itemBadgeLabel(section: CommandPaletteItem['section']) {
  return section === 'shortcuts' ? 'Abrir' : 'Caso'
}

export default function GlobalCommandPalette() {
  const navigate = useNavigate()
  const location = useLocation()
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)

  const { data: recentInvestigations } = useQuery({
    queryKey: ['command-palette-investigations'],
    queryFn: async () => {
      const response = await investigationService.listCursor({ limit: 8, order: 'updated_at_desc' })
      return response.items
    },
    enabled: isOpen,
    staleTime: 60_000,
  })

  const items = useMemo(() => {
    return [
      ...createNavigationItems(),
      ...createInvestigationItems(recentInvestigations ?? []),
    ]
  }, [recentInvestigations])

  const filteredItems = useMemo(() => filterCommandPaletteItems(items, query), [items, query])
  const groupedItems = useMemo(() => {
    return filteredItems.reduce<Array<{ section: CommandPaletteItem['section']; items: CommandPaletteItem[] }>>(
      (groups, item) => {
        const current = groups[groups.length - 1]
        if (current?.section === item.section) {
          current.items.push(item)
          return groups
        }
        groups.push({ section: item.section, items: [item] })
        return groups
      },
      []
    )
  }, [filteredItems])

  useEffect(() => {
    setIsOpen(false)
    setQuery('')
    setSelectedIndex(0)
  }, [location.pathname])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const isShortcut = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k'
      if (isShortcut) {
        event.preventDefault()
        previousFocusRef.current = document.activeElement as HTMLElement | null
        setIsOpen((current) => !current)
        return
      }

      if (!isOpen) {
        return
      }

      if (event.key === 'Escape') {
        event.preventDefault()
        setIsOpen(false)
        return
      }

      if (event.key === 'ArrowDown') {
        event.preventDefault()
        setSelectedIndex((current) => Math.min(current + 1, Math.max(filteredItems.length - 1, 0)))
      }

      if (event.key === 'ArrowUp') {
        event.preventDefault()
        setSelectedIndex((current) => Math.max(current - 1, 0))
      }

      if (event.key === 'Enter') {
        const selectedItem = filteredItems[selectedIndex]
        if (!selectedItem) {
          return
        }
        event.preventDefault()
        navigate(selectedItem.href)
        setIsOpen(false)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [filteredItems, isOpen, navigate, selectedIndex])

  useEffect(() => {
    if (!isOpen) {
      previousFocusRef.current?.focus()
      return
    }
    const frame = window.requestAnimationFrame(() => {
      inputRef.current?.focus()
    })
    return () => window.cancelAnimationFrame(frame)
  }, [isOpen])

  useEffect(() => {
    setSelectedIndex(0)
  }, [query])

  useEffect(() => {
    if (!isOpen || !listRef.current) return
    const selected = listRef.current.querySelector<HTMLElement>(`[data-command-index="${selectedIndex}"]`)
    if (selected && typeof selected.scrollIntoView === 'function') {
      selected.scrollIntoView({ block: 'nearest' })
    }
  }, [isOpen, selectedIndex])

  if (!isOpen) {
    return null
  }

  return (
    <div className="fixed inset-0 z-[90]">
      <button
        type="button"
        className="absolute inset-0 bg-slate-950/45 backdrop-blur-[2px]"
        aria-label="Fechar palette de comandos"
        onClick={() => setIsOpen(false)}
      />
      <div
        className="absolute left-1/2 top-[12vh] w-[min(92vw,760px)] -translate-x-1/2 overflow-hidden rounded-2xl border border-white/70 bg-white shadow-2xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="global-command-palette-title"
      >
        <h2 id="global-command-palette-title" className="sr-only">
          Palette de comandos global
        </h2>
        <div className="flex items-center gap-3 border-b border-gray-100 px-4 py-3">
          <Search className="h-4 w-4 text-gray-400" />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Pesquisar páginas, notificações, guias e investigações..."
            className="w-full border-0 bg-transparent text-sm text-gray-900 outline-none placeholder:text-gray-400"
            aria-label="Pesquisar comandos"
            role="combobox"
            aria-expanded="true"
            aria-controls="command-palette-listbox"
            aria-activedescendant={filteredItems[selectedIndex] ? `command-item-${filteredItems[selectedIndex].id}` : undefined}
          />
          <span className="hidden rounded-md bg-gray-100 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-gray-500 sm:inline">
            Esc
          </span>
        </div>

        <div ref={listRef} id="command-palette-listbox" className="max-h-[60vh] overflow-y-auto p-2" role="listbox" aria-label="Resultados da palette de comandos">
          {filteredItems.length === 0 ? (
            <div className="rounded-xl px-4 py-8 text-center text-sm text-gray-500">
              Nenhum resultado encontrado para essa busca.
            </div>
          ) : (
            groupedItems.map((group) => (
              <div key={group.section} className="mb-2 last:mb-0">
                <div className="px-3 pb-2 pt-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-gray-400">
                  {sectionLabel(group.section)}
                </div>
                {group.items.map((item) => {
                  const index = filteredItems.findIndex((candidate) => candidate.id === item.id)
                  return (
                    <button
                      key={item.id}
                      type="button"
                      id={`command-item-${item.id}`}
                      data-command-index={index}
                      onClick={() => {
                        navigate(item.href)
                        setIsOpen(false)
                      }}
                      role="option"
                      aria-selected={index === selectedIndex}
                      className={`flex w-full items-start gap-3 rounded-xl px-4 py-3 text-left transition ${
                        index === selectedIndex ? 'bg-emerald-50 text-emerald-900' : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="mt-0.5 rounded-lg bg-gray-100 px-2 py-1 text-[10px] font-semibold uppercase tracking-wide text-gray-500">
                        {itemBadgeLabel(item.section)}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="truncate text-sm font-medium text-gray-900">{item.title}</div>
                        {item.subtitle && <div className="truncate text-xs text-gray-500">{item.subtitle}</div>}
                      </div>
                    </button>
                  )
                })}
              </div>
            ))
          )}
        </div>

        <div className="flex items-center justify-between border-t border-gray-100 px-4 py-3 text-[11px] text-gray-500">
          <span>Cmd/Ctrl + K para abrir rapidamente</span>
          <span>Setas para navegar, Enter para abrir</span>
        </div>
      </div>
    </div>
  )
}
