import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Plus,
  Search,
  Filter,
  Trash2,
  CheckCircle2,
  Activity,
  XCircle,
  Clock,
  ChevronLeft,
  ChevronRight,
  MapPin,
  Building2,
  SlidersHorizontal,
  LayoutGrid,
  LayoutList,
} from 'lucide-react'
import { useState } from 'react'
import { investigationService } from '@/services/investigationService'
import { formatDate, formatCPFCNPJ } from '@/lib/utils'

export default function InvestigationsPage() {
  const [page, setPage] = useState(1)
  const pageSize = 20
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed' | 'failed'>('all')
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list')
  const [infiniteMode, setInfiniteMode] = useState(false)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['investigations', page, pageSize],
    queryFn: () => investigationService.list(page, pageSize),
    enabled: !infiniteMode,
  })

  const infiniteQuery = useInfiniteQuery({
    queryKey: ['investigations-infinite', statusFilter],
    queryFn: ({ pageParam }) => investigationService.listCursor({
      cursor: pageParam ?? undefined,
      limit: 20,
      status: statusFilter !== 'all' ? statusFilter : undefined,
    }),
    getNextPageParam: (lastPage) => lastPage.has_next ? lastPage.next_cursor : undefined,
    enabled: infiniteMode,
    initialPageParam: null as string | null,
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => investigationService.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['investigations'] }),
  })

  const handleDelete = (id: number, name: string) => {
    if (deleteMutation.isPending) return
    if (window.confirm(`Excluir "${name}"?`)) deleteMutation.mutate(id)
  }

  const items = infiniteMode
    ? (infiniteQuery.data?.pages.flatMap(p => p.items) ?? [])
    : (data?.items ?? [])
  const filteredItems = items.filter((item) => {
    const q = search.toLowerCase()
    const matchesSearch =
      item.target_name.toLowerCase().includes(q) ||
      (item.target_cpf_cnpj || '').replace(/\D/g, '').includes(search.replace(/\D/g, ''))
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const statusColor = (s: string) => {
    switch (s) {
      case 'completed': return 'bg-emerald-50 text-emerald-700 ring-emerald-200'
      case 'in_progress': return 'bg-blue-50 text-blue-700 ring-blue-200'
      case 'failed': return 'bg-red-50 text-red-700 ring-red-200'
      default: return 'bg-gray-50 text-gray-600 ring-gray-200'
    }
  }
  const statusLabel = (s: string) => {
    switch (s) {
      case 'completed': return 'Concluída'
      case 'in_progress': return 'Em Andamento'
      case 'failed': return 'Falhou'
      default: return 'Pendente'
    }
  }
  const statusIcon = (s: string) => {
    switch (s) {
      case 'completed': return <CheckCircle2 className="h-3 w-3" />
      case 'in_progress': return <Activity className="h-3 w-3" />
      case 'failed': return <XCircle className="h-3 w-3" />
      default: return <Clock className="h-3 w-3" />
    }
  }

  const priorityBar = (p: number) => (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((l) => (
        <div key={l} className={`h-1 w-3 rounded-full ${l <= p ? 'bg-amber-400' : 'bg-gray-200'}`} />
      ))}
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Investigações</h1>
          <p className="mt-0.5 text-sm text-gray-500">
            {infiniteMode
              ? `${infiniteQuery.data?.pages[0]?.total_count ?? items.length} investigações cadastradas`
              : `${data?.total ?? 0} investigações cadastradas`}
          </p>
        </div>
        <Link
          to="/investigations/new"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-600 text-white text-sm font-medium rounded-xl hover:bg-emerald-700 transition shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Nova Investigação
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200/60">
        <div className="px-5 py-3.5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-gray-100">
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar por nome, CPF ou CNPJ..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 bg-white text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition"
            />
          </div>
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="w-4 h-4 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as typeof statusFilter)}
              className="rounded-lg border border-gray-200 bg-white text-gray-700 px-3 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-gray-900"
            >
              <option value="all">Todos os status</option>
              <option value="pending">Pendente</option>
              <option value="in_progress">Em andamento</option>
              <option value="completed">Concluída</option>
              <option value="failed">Falhou</option>
            </select>
            <button
              onClick={() => setInfiniteMode((v) => !v)}
              className={`px-3 py-1.5 rounded-lg text-[11px] font-medium border transition ${
                infiniteMode
                  ? 'bg-emerald-600 text-white border-emerald-600'
                  : 'border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {infiniteMode ? 'Scroll infinito' : 'Paginado'}
            </button>
            <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('list')}
                className={`p-1.5 rounded ${viewMode === 'list' ? 'bg-emerald-600 text-white' : 'text-gray-400 hover:text-gray-600'}`}
              >
                <LayoutList className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded ${viewMode === 'grid' ? 'bg-emerald-600 text-white' : 'text-gray-400 hover:text-gray-600'}`}
              >
                <LayoutGrid className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>

        {(infiniteMode ? infiniteQuery.isLoading : isLoading) ? (
          <div className="p-12 text-center text-gray-400 text-sm">Carregando...</div>
        ) : filteredItems.length === 0 ? (
          <div className="p-12 text-center">
            <Search className="mx-auto h-8 w-8 text-gray-300" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhum resultado</h3>
            <p className="mt-1 text-xs text-gray-500">{search ? 'Tente outro termo.' : 'Comece criando uma nova investigação.'}</p>
          </div>
        ) : viewMode === 'list' ? (
          <div className="divide-y divide-gray-50">
            {filteredItems.map((inv) => (
              <div key={inv.id} className="px-5 py-3.5 flex items-center gap-4 hover:bg-gray-50/50 transition">
                <div className="bg-gray-100 rounded-lg p-2 shrink-0">
                  <Search className="h-3.5 w-3.5 text-gray-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Link to={`/investigations/${inv.id}`} className="text-sm font-medium text-gray-900 hover:text-gray-700 truncate">
                      {inv.target_name}
                    </Link>
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ring-1 ${statusColor(inv.status)}`}>
                      {statusIcon(inv.status)} {statusLabel(inv.status)}
                    </span>
                    {priorityBar(inv.priority)}
                  </div>
                  <div className="mt-0.5 flex items-center gap-3 text-[11px] text-gray-400 flex-wrap">
                    {inv.target_cpf_cnpj && <span className="font-mono">{formatCPFCNPJ(inv.target_cpf_cnpj)}</span>}
                    <span className="inline-flex items-center gap-0.5"><MapPin className="h-2.5 w-2.5" /> {inv.properties_found}</span>
                    <span className="inline-flex items-center gap-0.5"><Building2 className="h-2.5 w-2.5" /> {inv.companies_found}</span>
                    <span>{formatDate(inv.created_at)}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Link to={`/investigations/${inv.id}`} className="px-3 py-1.5 rounded-lg text-[11px] font-medium text-gray-600 border border-gray-200 hover:bg-gray-50 transition">
                    Detalhes
                  </Link>
                  <button onClick={() => handleDelete(inv.id, inv.target_name)} className="p-1.5 rounded-lg border border-gray-200 text-gray-400 hover:text-red-600 hover:border-red-200 hover:bg-red-50 transition" title="Excluir">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredItems.map((inv) => (
              <Link key={inv.id} to={`/investigations/${inv.id}`} className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition group">
                <div className="flex items-center justify-between mb-3">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ring-1 ${statusColor(inv.status)}`}>
                    {statusIcon(inv.status)} {statusLabel(inv.status)}
                  </span>
                  {priorityBar(inv.priority)}
                </div>
                <h3 className="text-sm font-semibold text-gray-900 group-hover:text-gray-700 truncate">{inv.target_name}</h3>
                {inv.target_cpf_cnpj && <p className="text-[11px] font-mono text-gray-400 mt-0.5">{formatCPFCNPJ(inv.target_cpf_cnpj)}</p>}
                <div className="mt-3 flex items-center gap-3 text-[11px] text-gray-400">
                  <span className="inline-flex items-center gap-0.5"><MapPin className="h-2.5 w-2.5" /> {inv.properties_found} prop.</span>
                  <span className="inline-flex items-center gap-0.5"><Building2 className="h-2.5 w-2.5" /> {inv.companies_found} emp.</span>
                </div>
                <p className="mt-2 text-[10px] text-gray-400">{formatDate(inv.created_at)}</p>
                <div className="mt-3 flex justify-between items-center">
                  <span className="text-[11px] font-medium text-gray-500 group-hover:text-gray-900 transition">Ver detalhes &rarr;</span>
                  <button
                    onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleDelete(inv.id, inv.target_name) }}
                    className="p-1 rounded-md text-gray-300 hover:text-red-500 hover:bg-red-50 transition"
                    title="Excluir"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </Link>
            ))}
          </div>
        )}

        {/* Load more (infinite scroll mode) */}
        {infiniteMode && infiniteQuery.hasNextPage && (
          <div className="p-4 text-center">
            <button
              onClick={() => infiniteQuery.fetchNextPage()}
              disabled={infiniteQuery.isFetchingNextPage}
              className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm hover:bg-emerald-700 disabled:opacity-50"
            >
              {infiniteQuery.isFetchingNextPage ? 'Carregando...' : 'Carregar mais'}
            </button>
          </div>
        )}

        {/* Pagination (page mode) */}
        {!infiniteMode && data && data.total_pages > 1 && (
          <div className="px-5 py-3 border-t border-gray-100 flex items-center justify-between">
            <p className="text-[11px] text-gray-500">
              {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, data.total)} de {data.total}
            </p>
            <div className="flex items-center gap-1">
              <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="p-1.5 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-30 transition">
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <span className="px-3 py-1 text-[11px] font-medium text-gray-700">{page}/{data.total_pages}</span>
              <button onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))} disabled={page === data.total_pages} className="p-1.5 rounded-lg border border-gray-200 text-gray-500 hover:bg-gray-50 disabled:opacity-30 transition">
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
