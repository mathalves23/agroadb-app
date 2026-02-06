/**
 * Dashboard com Gráficos Detalhados
 * 
 * Visualização de dados com Recharts
 */
import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { FadeIn, StaggerChildren } from '../components/Animations';
import { Loading } from '../components/Loading';
import { useTheme } from '../contexts/ThemeContext';

export function DashboardCharts() {
  const { actualMode } = useTheme();
  interface DashboardStats {
    investigations_by_month: Array<{ month: string; count: number; completed: number; failed: number }>;
    scrapers_performance: Array<{ name: string; success: number; failed: number }>;
    properties_by_state: Array<{ state: string; count: number }>;
    status_distribution: Array<{ name: string; value: number; color: string }>;
  }

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      // TODO: Implementar chamada à API
      // const response = await api.get('/statistics/dashboard');
      // setStats(response.data);
      
      // Mock data
      setTimeout(() => {
        setStats({
          investigations_by_month: [
            { month: 'Jan', count: 12, completed: 10, failed: 2 },
            { month: 'Fev', count: 18, completed: 15, failed: 3 },
            { month: 'Mar', count: 25, completed: 22, failed: 3 },
            { month: 'Abr', count: 30, completed: 28, failed: 2 },
            { month: 'Mai', count: 28, completed: 25, failed: 3 },
            { month: 'Jun', count: 35, completed: 32, failed: 3 }
          ],
          scrapers_performance: [
            { name: 'CAR', success: 95, failed: 5 },
            { name: 'INCRA', success: 92, failed: 8 },
            { name: 'Receita', success: 88, failed: 12 },
            { name: 'Diários', success: 85, failed: 15 },
            { name: 'Cartórios', success: 90, failed: 10 },
            { name: 'SIGEF', success: 87, failed: 13 }
          ],
          properties_by_state: [
            { state: 'MT', count: 450 },
            { state: 'MS', count: 380 },
            { state: 'GO', count: 320 },
            { state: 'SP', count: 290 },
            { state: 'PR', count: 250 },
            { state: 'MG', count: 220 }
          ],
          status_distribution: [
            { name: 'Concluídas', value: 145, color: '#16a34a' },
            { name: 'Em Progresso', value: 32, color: '#0ea5e9' },
            { name: 'Pendentes', value: 18, color: '#f59e0b' },
            { name: 'Falhas', value: 12, color: '#dc2626' }
          ]
        });
        setLoading(false);
      }, 1000);
    } catch (error) {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loading type="spinner" message="Carregando estatísticas..." />;
  }

  const isDark = actualMode === 'dark';
  const textColor = isDark ? '#e5e7eb' : '#374151';
  const gridColor = isDark ? '#374151' : '#e5e7eb';

  return (
    <div className="space-y-6">
      <StaggerChildren className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Investigações por Mês */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">
            📈 Investigações por Mês
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={stats.investigations_by_month}>
              <defs>
                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#16a34a" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#16a34a" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis dataKey="month" stroke={textColor} />
              <YAxis stroke={textColor} />
              <Tooltip
                contentStyle={{
                  backgroundColor: isDark ? '#1f2937' : '#ffffff',
                  border: `1px solid ${gridColor}`,
                  borderRadius: '8px',
                  color: textColor
                }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="count"
                stroke="#16a34a"
                fillOpacity={1}
                fill="url(#colorCount)"
                name="Total"
              />
              <Area
                type="monotone"
                dataKey="completed"
                stroke="#0ea5e9"
                fill="#0ea5e9"
                fillOpacity={0.6}
                name="Concluídas"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Performance dos Scrapers */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">
            ⚡ Performance dos Scrapers
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.scrapers_performance}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis dataKey="name" stroke={textColor} />
              <YAxis stroke={textColor} />
              <Tooltip
                contentStyle={{
                  backgroundColor: isDark ? '#1f2937' : '#ffffff',
                  border: `1px solid ${gridColor}`,
                  borderRadius: '8px',
                  color: textColor
                }}
              />
              <Legend />
              <Bar dataKey="success" fill="#16a34a" name="Sucesso %" radius={[8, 8, 0, 0]} />
              <Bar dataKey="failed" fill="#dc2626" name="Falha %" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Propriedades por Estado */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">
            🗺️ Propriedades por Estado
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.properties_by_state} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis type="number" stroke={textColor} />
              <YAxis dataKey="state" type="category" stroke={textColor} />
              <Tooltip
                contentStyle={{
                  backgroundColor: isDark ? '#1f2937' : '#ffffff',
                  border: `1px solid ${gridColor}`,
                  borderRadius: '8px',
                  color: textColor
                }}
              />
              <Bar dataKey="count" fill="#0ea5e9" name="Propriedades" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Distribuição por Status */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">
            📊 Status das Investigações
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={stats.status_distribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {stats.status_distribution.map((entry, index: number) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: isDark ? '#1f2937' : '#ffffff',
                  border: `1px solid ${gridColor}`,
                  borderRadius: '8px',
                  color: textColor
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </StaggerChildren>

      {/* Métricas Rápidas */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total de Investigações"
          value="207"
          change="+12%"
          icon="🔍"
          color="blue"
        />
        <MetricCard
          title="Propriedades Encontradas"
          value="1,910"
          change="+8%"
          icon="🏞️"
          color="green"
        />
        <MetricCard
          title="Empresas Identificadas"
          value="542"
          change="+15%"
          icon="🏢"
          color="purple"
        />
        <MetricCard
          title="Taxa de Sucesso"
          value="89%"
          change="+3%"
          icon="✅"
          color="emerald"
        />
      </div>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  icon: string;
  color: string;
}

function MetricCard({ title, value, change, icon, color }: MetricCardProps) {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600',
    green: 'bg-green-50 dark:bg-green-900/20 text-green-600',
    purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600',
    emerald: 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600'
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-2">
        <div className={`w-10 h-10 rounded-lg ${colors[color]} flex items-center justify-center text-2xl`}>
          {icon}
        </div>
        <span className="text-sm text-green-600 font-medium">{change}</span>
      </div>
      <h4 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{value}</h4>
      <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
    </div>
  );
}
