import { memo } from 'react'
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
  Legend,
} from 'recharts'

const CHART_COLORS = ['#059669', '#2563eb', '#7c3aed', '#d97706', '#0d9488', '#4f46e5', '#dc2626']

interface ChartByProviderItem {
  name: string
  consultas: number
  resultados: number
}

interface PieDataItem {
  name: string
  value: number
}

interface ChartByDateItem {
  date: string
  consultas: number
}

interface QueryChartsProps {
  chartByProvider: ChartByProviderItem[]
  pieData: PieDataItem[]
  chartByDate: ChartByDateItem[]
}

export const QueryCharts = memo(function QueryCharts({ chartByProvider, pieData, chartByDate }: QueryChartsProps) {
  if (chartByProvider.length === 0 && pieData.length === 0) {
    return null
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      {/* Consultas por provedor (barras) */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 lg:col-span-2">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Consultas por Base</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartByProvider} barGap={4}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#9ca3af' }} />
            <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} />
            <Tooltip
              contentStyle={{
                borderRadius: '8px',
                border: '1px solid #e5e7eb',
                fontSize: '12px',
              }}
            />
            <Bar dataKey="consultas" fill="#6366f1" radius={[4, 4, 0, 0]} name="Consultas" />
            <Bar dataKey="resultados" fill="#059669" radius={[4, 4, 0, 0]} name="Resultados" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Distribuição por provedor (pizza) */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Distribuição</h3>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={70}
              paddingAngle={3}
              dataKey="value"
            >
              {pieData.map((_entry, index) => (
                <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '12px' }} />
            <Legend
              iconType="circle"
              iconSize={8}
              wrapperStyle={{ fontSize: '10px', color: '#6b7280' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Timeline de consultas */}
      {chartByDate.length > 1 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 lg:col-span-3">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">Consultas ao longo do tempo</h3>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={chartByDate}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#9ca3af' }} />
              <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} allowDecimals={false} />
              <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '12px' }} />
              <Bar dataKey="consultas" fill="#d97706" radius={[4, 4, 0, 0]} name="Consultas" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
})
