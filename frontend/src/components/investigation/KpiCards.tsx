import {
  MapPin,
  Building2,
  FileText,
  Database,
  Activity,
  Layers,
} from 'lucide-react'

interface KpiCardsProps {
  propertiesFound: number
  leaseContractsFound: number
  companiesFound: number
  totalQueries: number
  sourcesWithDataCount: number
  totalResults: number
}

export function KpiCards({
  propertiesFound,
  leaseContractsFound,
  companiesFound,
  totalQueries,
  sourcesWithDataCount,
  totalResults,
}: KpiCardsProps) {
  const kpis = [
    { label: 'Propriedades', value: propertiesFound, icon: MapPin, color: 'bg-emerald-500' },
    { label: 'Contratos', value: leaseContractsFound, icon: FileText, color: 'bg-blue-500' },
    { label: 'Empresas', value: companiesFound, icon: Building2, color: 'bg-purple-500' },
    { label: 'Consultas', value: totalQueries, icon: Database, color: 'bg-amber-500' },
    { label: 'Bases com dados', value: sourcesWithDataCount, icon: Activity, color: 'bg-teal-500' },
    { label: 'Resultados', value: totalResults, icon: Layers, color: 'bg-indigo-500' },
  ]

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6" role="group" aria-label="Indicadores da investigação">
      {kpis.map((kpi) => (
        <div key={kpi.label} className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className={`${kpi.color} rounded-lg p-2`}>
              <kpi.icon className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-xs text-gray-500">{kpi.label}</p>
              <p className="text-xl font-bold text-gray-900">{kpi.value}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
