/**
 * Comparação de Investigações
 * 
 * Compara múltiplas investigações lado a lado
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FadeIn } from '../components/Animations';
import { useToast } from '../components/Toast';

interface Investigation {
  id: string;
  target_name: string;
  target_cpf_cnpj: string;
  created_at: Date;
  status: string;
  stats: {
    properties: number;
    companies: number;
    documents: number;
    total_area: number;
  };
}

interface ComparisonProps {
  investigations: Investigation[];
  maxComparisons?: number;
}

export function InvestigationComparison({
  investigations,
  maxComparisons = 3
}: ComparisonProps) {
  const toast = useToast();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [showComparison, setShowComparison] = useState(false);

  const selectedInvestigations = investigations.filter(inv =>
    selectedIds.includes(inv.id)
  );

  const toggleSelection = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(prev => prev.filter(i => i !== id));
    } else if (selectedIds.length < maxComparisons) {
      setSelectedIds(prev => [...prev, id]);
    } else {
      toast.warning(`Máximo de ${maxComparisons} investigações para comparar`);
    }
  };

  const handleCompare = () => {
    if (selectedIds.length < 2) {
      toast.warning('Selecione pelo menos 2 investigações para comparar');
      return;
    }
    setShowComparison(true);
  };

  return (
    <div className="space-y-6">
      {/* Selection Mode */}
      {!showComparison && (
        <FadeIn>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  🔄 Comparar Investigações
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Selecione até {maxComparisons} investigações para comparar
                </p>
              </div>
              <button
                onClick={handleCompare}
                disabled={selectedIds.length < 2}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
              >
                Comparar ({selectedIds.length})
              </button>
            </div>

            {/* Investigation List */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {investigations.map((inv) => (
                <motion.div
                  key={inv.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => toggleSelection(inv.id)}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedIds.includes(inv.id)
                      ? 'border-green-600 bg-green-50 dark:bg-green-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-green-400'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-bold text-gray-900 dark:text-white">
                      {inv.target_name}
                    </h3>
                    {selectedIds.includes(inv.id) && (
                      <span className="text-green-600 text-xl">✓</span>
                    )}
                  </div>
                  
                  <div className="text-sm space-y-1">
                    <p className="text-gray-600 dark:text-gray-400">
                      {inv.target_cpf_cnpj}
                    </p>
                    <div className="flex gap-4 mt-2">
                      <span>🏞️ {inv.stats.properties}</span>
                      <span>🏢 {inv.stats.companies}</span>
                      <span>📄 {inv.stats.documents}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </FadeIn>
      )}

      {/* Comparison View */}
      <AnimatePresence>
        {showComparison && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  📊 Comparação Detalhada
                </h2>
                <button
                  onClick={() => setShowComparison(false)}
                  className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                >
                  ← Voltar
                </button>
              </div>

              {/* Comparison Table */}
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-900">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Métrica
                        </th>
                        {selectedInvestigations.map((inv) => (
                          <th
                            key={inv.id}
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                          >
                            {inv.target_name}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                      <ComparisonRow
                        label="CPF/CNPJ"
                        values={selectedInvestigations.map(i => i.target_cpf_cnpj)}
                        type="text"
                      />
                      <ComparisonRow
                        label="Status"
                        values={selectedInvestigations.map(i => i.status)}
                        type="status"
                      />
                      <ComparisonRow
                        label="Propriedades"
                        values={selectedInvestigations.map(i => i.stats.properties)}
                        type="number"
                        highlight="max"
                      />
                      <ComparisonRow
                        label="Empresas"
                        values={selectedInvestigations.map(i => i.stats.companies)}
                        type="number"
                        highlight="max"
                      />
                      <ComparisonRow
                        label="Documentos"
                        values={selectedInvestigations.map(i => i.stats.documents)}
                        type="number"
                        highlight="max"
                      />
                      <ComparisonRow
                        label="Área Total (ha)"
                        values={selectedInvestigations.map(i => i.stats.total_area)}
                        type="number"
                        highlight="max"
                        format={(v) => (v as number).toLocaleString()}
                      />
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <SummaryCard
                  title="Total de Propriedades"
                  value={selectedInvestigations.reduce((sum, i) => sum + i.stats.properties, 0)}
                  icon="🏞️"
                />
                <SummaryCard
                  title="Total de Empresas"
                  value={selectedInvestigations.reduce((sum, i) => sum + i.stats.companies, 0)}
                  icon="🏢"
                />
                <SummaryCard
                  title="Total de Documentos"
                  value={selectedInvestigations.reduce((sum, i) => sum + i.stats.documents, 0)}
                  icon="📄"
                />
              </div>

              {/* Export Button */}
              <div className="flex justify-end">
                <button className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg">
                  📊 Exportar Comparação
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Comparison Row Component
function ComparisonRow({
  label,
  values,
  type = 'text',
  highlight,
  format
}: {
  label: string;
  values: unknown[];
  type?: 'text' | 'number' | 'status';
  highlight?: 'max' | 'min';
  format?: (value: unknown) => string;
}) {
  const numericValues = type === 'number' ? values.map(v => Number(v)) : [];
  const maxValue = type === 'number' ? Math.max(...numericValues) : null;
  const minValue = type === 'number' ? Math.min(...numericValues) : null;

  return (
    <tr>
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
        {label}
      </td>
      {values.map((value, index) => {
        const numVal = type === 'number' ? Number(value) : null;
        const isHighlighted =
          (highlight === 'max' && numVal === maxValue) ||
          (highlight === 'min' && numVal === minValue);

        return (
          <td
            key={index}
            className={`px-6 py-4 whitespace-nowrap text-sm ${
              isHighlighted
                ? 'bg-green-50 dark:bg-green-900/20 font-bold text-green-600'
                : 'text-gray-700 dark:text-gray-300'
            }`}
          >
            {format ? format(value) : String(value)}
            {isHighlighted && ' 🏆'}
          </td>
        );
      })}
    </tr>
  );
}

// Summary Card
function SummaryCard({ title, value, icon }: { title: string; value: number; icon: string }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-3xl">{icon}</span>
      </div>
      <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
        {value.toLocaleString()}
      </h3>
      <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
    </div>
  );
}
