import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Plus,
  Search,
  Building2,
  Trash2,
  MapPin,
  Activity,
  Database,
  Scale,
  CheckCircle2,
  Clock,
  XCircle,
  Zap,
  TrendingUp,
  AlertTriangle,
  ArrowUpRight,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { useMemo } from 'react'
import { investigationService } from '@/services/investigationService'
import { legalService } from '@/services/legalService'
import { formatDate, formatCPFCNPJ } from '@/lib/utils'

const PIE_COLORS = ['#059669', '#2563eb', '#7c3aed', '#d97706', '#0d9488', '#dc2626']

export default function DashboardPage() {
  const queryClient = useQueryClient()
  const { data: investigations, isLoading } = useQuery({
    queryKey: ['investigations', 1, 20],
    queryFn: () => investigationService.list(1, 20),
  })
  const { data: legalSummary } = useQuery({
    queryKey: ['legal-summary'],
    queryFn: () => legalService.getLegalSummary(),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => investigationService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['investigations'] })
    },
  })

  const handleDelete = (id: number, name: string) => {
    if (deleteMutation.isPending) return
    if (window.confirm(`Excluir "${name}"?`)) deleteMutation.mutate(id)
  }

  const items = investigations?.items ?? []
  const activeCount = items.filter((i) => i.status === 'in_progress').length
  const completedCount = items.filter((i) => i.status === 'completed').length
  const failedCount = items.filter((i) => i.status === 'failed').length
  const propertiesTotal = items.reduce((s, i) => s + i.properties_found, 0)
  const companiesTotal = items.reduce((s, i) => s + i.companies_found, 0)
  const datajudTotal = legalSummary?.summary?.datajud?.total ?? 0
  const sigefParcelasTotal = legalSummary?.summary?.sigef_parcelas?.total ?? 0
  const hasLegalData = datajudTotal > 0 || sigefParcelasTotal > 0

  const statusData = useMemo(
    () => [
      { name: 'Em andamento', value: activeCount },
      { name: 'Concluídas', value: completedCount },
      { name: 'Pendentes', value: items.filter((i) => i.status === 'pending').length },
      { name: 'Falhas', value: failedCount },
    ].filter((d) => d.value > 0),
    [activeCount, completedCount, failedCount, items]
  )

  const topInvestigations = useMemo(
    () =>
      [...items]
        .sort((a, b) => a.properties_found + a.companies_found > b.properties_found + b.companies_found ? -1 : 1)
        .slice(0, 5)
        .map((inv) => ({
          name: inv.target_name.length > 18 ? inv.target_name.slice(0, 18) + '...' : inv.target_name,
          resultados: inv.properties_found + inv.companies_found,
        })),
    [items]
  )

  const statusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-emerald-50 text-emerald-700 ring-emerald-200'
      case 'in_progress': return 'bg-blue-50 text-blue-700 ring-blue-200'
      case 'failed': return 'bg-red-50 text-red-700 ring-red-200'
      default: return 'bg-gray-50 text-gray-600 ring-gray-200'
    }
  }
  const statusLabel = (status: string) => {
    switch (status) {
      case 'completed': return 'Concluída'
      case 'in_progress': return 'Em Andamento'
      case 'failed': return 'Falhou'
      default: return 'Pendente'
    }
  }
  const statusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="h-3 w-3" />
      case 'in_progress': return <Activity className="h-3 w-3" />
      case 'failed': return <XCircle className="h-3 w-3" />
      default: return <Clock className="h-3 w-3" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-0.5 text-sm text-gray-500">Visão geral da plataforma de inteligência patrimonial</p>
        </div>
        <Link
          to="/investigations/new"
          data-tour="new-investigation"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-600 text-white text-sm font-medium rounded-xl hover:bg-emerald-700 transition shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Nova Investigação
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-7" data-tour="dashboard-kpis">
        {[
          { label: 'Investigações', value: items.length, icon: Search, bg: 'bg-gray-50', iconColor: 'text-gray-600', border: 'border-gray-200/60' },
          { label: 'Em andamento', value: activeCount, icon: Activity, bg: 'bg-blue-50', iconColor: 'text-blue-600', border: 'border-blue-100' },
          { label: 'Concluídas', value: completedCount, icon: CheckCircle2, bg: 'bg-emerald-50', iconColor: 'text-emerald-600', border: 'border-emerald-100' },
          { label: 'Propriedades', value: propertiesTotal, icon: MapPin, bg: 'bg-green-50', iconColor: 'text-green-600', border: 'border-green-100' },
          { label: 'Empresas', value: companiesTotal, icon: Building2, bg: 'bg-violet-50', iconColor: 'text-violet-600', border: 'border-violet-100' },
          { label: 'DataJud', value: datajudTotal, icon: Scale, bg: 'bg-indigo-50', iconColor: 'text-indigo-600', border: 'border-indigo-100' },
          { label: 'SIGEF', value: sigefParcelasTotal, icon: Database, bg: 'bg-amber-50', iconColor: 'text-amber-600', border: 'border-amber-100' },
        ].map((stat) => (
          <div key={stat.label} className={`bg-white rounded-xl border ${stat.border} p-4 hover:shadow-sm transition-shadow`}>
            <div className="flex items-center gap-3">
              <div className={`${stat.bg} rounded-lg p-2`}>
                <stat.icon className={`h-4 w-4 ${stat.iconColor}`} />
              </div>
              <div>
                <p className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">{stat.label}</p>
                <p className="text-xl font-bold text-gray-800">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Top investigações */}
        {topInvestigations.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200/60 p-5 lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-700">Top Investigações por resultados</h3>
              <TrendingUp className="h-4 w-4 text-gray-300" />
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={topInvestigations} layout="vertical" barSize={16}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} width={120} />
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                <Bar dataKey="resultados" fill="#059669" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Status Pie */}
        {statusData.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200/60 p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Status das investigações</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={statusData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={4} dataKey="value">
                  {statusData.map((_e, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-2 flex flex-wrap justify-center gap-3">
              {statusData.map((d, i) => (
                <span key={d.name} className="flex items-center gap-1.5 text-[10px] text-gray-500">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }} />
                  {d.name} ({d.value})
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Alertas */}
      {failedCount > 0 && (
        <div className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-xl p-4">
          <AlertTriangle className="h-5 w-5 text-red-500 shrink-0" />
          <div>
            <p className="text-sm font-medium text-red-800">{failedCount} investigação(ões) com falha</p>
            <p className="text-xs text-red-600">Verifique a configuração das APIs ou tente novamente.</p>
          </div>
        </div>
      )}

      {/* Recent Investigations */}
      <div className="bg-white rounded-xl border border-gray-200/60" data-tour="recent-investigations">
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-emerald-50 rounded-lg p-2">
              <Search className="h-4 w-4 text-emerald-600" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-gray-700">Investigações Recentes</h2>
              <p className="text-[10px] text-gray-400">{items.length} total</p>
            </div>
          </div>
          <Link to="/investigations" className="inline-flex items-center gap-1 text-xs font-medium text-gray-500 hover:text-gray-900 transition">
            Ver todas <ArrowUpRight className="w-3 h-3" />
          </Link>
        </div>

        {isLoading ? (
          <div className="p-12 text-center text-gray-400 text-sm">Carregando...</div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center">
            <Search className="mx-auto h-8 w-8 text-gray-300" />
            <p className="mt-2 text-sm text-gray-500">Nenhuma investigação encontrada</p>
            <Link to="/investigations/new" className="mt-3 inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white text-xs rounded-lg hover:bg-emerald-700 transition">
              <Plus className="h-3.5 w-3.5" /> Nova Investigação
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {items.slice(0, 8).map((inv) => (
              <div key={inv.id} className="px-6 py-3.5 flex items-center gap-4 hover:bg-gray-50/50 transition">
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
                  </div>
                  <div className="mt-0.5 flex items-center gap-3 text-[11px] text-gray-400">
                    {inv.target_cpf_cnpj && <span className="font-mono">{formatCPFCNPJ(inv.target_cpf_cnpj)}</span>}
                    <span>{inv.properties_found} prop.</span>
                    <span>{inv.companies_found} emp.</span>
                    <span>{formatDate(inv.created_at)}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Link to={`/investigations/${inv.id}`} className="px-3 py-1.5 rounded-lg text-[11px] font-medium text-gray-600 border border-gray-200 hover:bg-gray-50 transition">
                    Detalhes
                  </Link>
                  <button
                    onClick={() => handleDelete(inv.id, inv.target_name)}
                    className="p-1.5 rounded-lg border border-gray-200 text-gray-400 hover:text-red-600 hover:border-red-200 hover:bg-red-50 transition"
                    title="Excluir"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Consultas legais: estado vazio com CTA Configurar integrações */}
      {!hasLegalData && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex items-center gap-3 shrink-0">
            <div className="bg-amber-100 rounded-lg p-2">
              <Scale className="h-5 w-5 text-amber-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-amber-800">Nenhum dado de consultas legais</p>
              <p className="text-xs text-amber-700">Configure as variáveis no .env do backend e use a aba Consultas Legais em uma investigação.</p>
            </div>
          </div>
          <Link
            to="/settings"
            className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 text-white text-sm font-medium rounded-lg hover:bg-amber-700 transition shrink-0"
          >
            Configurar integrações
          </Link>
        </div>
      )}

      {/* Bases integradas */}
      <div className="bg-white rounded-xl border border-gray-200/60 p-5">
        <div className="flex items-center gap-2 mb-3">
          <Zap className="h-4 w-4 text-amber-500" />
          <h2 className="text-sm font-semibold text-gray-700">Bases Integradas</h2>
        </div>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
          {[
            { name: 'SNCR/INCRA', free: false },
            { name: 'SIGEF', free: false },
            { name: 'SICAR', free: false },
            { name: 'DataJud/CNJ', free: true },
            { name: 'CNPJ/RFB', free: false },
            { name: 'CADIN', free: false },
            { name: 'CND', free: false },
            { name: 'SNCCI', free: false },
            { name: 'BrasilAPI', free: true },
            { name: 'Transparência/CGU', free: true },
            { name: 'ReceitaWS', free: true },
            { name: 'IBGE', free: true },
            { name: 'TSE', free: true },
            { name: 'CVM', free: true },
            { name: 'BCB', free: true },
            { name: 'dados.gov.br', free: true },
            { name: 'TJMG', free: true },
            { name: 'Antecedentes/MG', free: true },
            { name: 'SICAR/CAR', free: true },
            { name: 'Portal gov.br', free: false },
            { name: 'Serv. Estaduais', free: false },
            { name: 'Caixa FGTS/CRF', free: true },
            { name: 'BNMP/CNJ', free: true },
            { name: 'SEEU/CNJ', free: true },
            { name: 'SIGEF Público', free: true },
            { name: 'Receita Federal (CPF)', free: true },
            { name: 'Receita Federal (CNPJ)', free: true },
          ].map((base) => (
            <div key={base.name} className="flex items-center gap-2 bg-white rounded-lg px-3 py-2 border border-gray-100">
              <Database className={`h-3 w-3 shrink-0 ${base.free ? 'text-emerald-500' : 'text-amber-500'}`} />
              <span className="text-[11px] font-medium text-gray-700">{base.name}</span>
              {base.free && <span className="ml-auto text-[9px] font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">FREE</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
