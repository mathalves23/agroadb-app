/**
 * Filtros Avançados para Investigações
 * 
 * Sistema de filtros completo com múltiplos critérios
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SlideIn } from '../components/Animations';

export interface FilterCriteria {
  status?: string[];
  dateRange?: { start: Date | null; end: Date | null };
  search?: string;
  minProperties?: number;
  maxProperties?: number;
  minCompanies?: number;
  maxCompanies?: number;
  states?: string[];
  sources?: string[];
  sortBy?: 'created_at' | 'updated_at' | 'target_name' | 'total_results';
  sortOrder?: 'asc' | 'desc';
}

interface AdvancedFiltersProps {
  onApplyFilters: (filters: FilterCriteria) => void;
  onClearFilters: () => void;
  initialFilters?: FilterCriteria;
}

export function AdvancedFilters({
  onApplyFilters,
  onClearFilters,
  initialFilters = {}
}: AdvancedFiltersProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [filters, setFilters] = useState<FilterCriteria>(initialFilters);

  const handleApply = () => {
    onApplyFilters(filters);
    setIsOpen(false);
  };

  const handleClear = () => {
    setFilters({});
    onClearFilters();
  };

  const activeFiltersCount = Object.values(filters).filter(v =>
    Array.isArray(v) ? v.length > 0 : v !== undefined && v !== null && v !== ''
  ).length;

  return (
    <div className="relative">
      {/* Filter Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        Filtros Avançados
        {activeFiltersCount > 0 && (
          <span className="px-2 py-0.5 bg-green-600 text-white text-xs rounded-full">
            {activeFiltersCount}
          </span>
        )}
      </button>

      {/* Filter Panel */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black/20 z-40"
            />

            {/* Panel */}
            <SlideIn direction="down" className="absolute top-full right-0 mt-2 z-50">
              <div className="w-[600px] max-w-[90vw] bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    🔍 Filtros Avançados
                  </h3>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-6 max-h-[70vh] overflow-y-auto pr-2">
                  {/* Status */}
                  <FilterSection title="Status">
                    <div className="flex flex-wrap gap-2">
                      {['completed', 'in_progress', 'pending', 'failed'].map((status) => (
                        <button
                          key={status}
                          onClick={() => {
                            const current = filters.status || [];
                            setFilters({
                              ...filters,
                              status: current.includes(status)
                                ? current.filter(s => s !== status)
                                : [...current, status]
                            });
                          }}
                          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                            (filters.status || []).includes(status)
                              ? 'bg-green-600 text-white'
                              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                          }`}
                        >
                          {status === 'completed' ? '✅ Concluída' :
                           status === 'in_progress' ? '🔄 Em Progresso' :
                           status === 'pending' ? '⏳ Pendente' : '❌ Falhou'}
                        </button>
                      ))}
                    </div>
                  </FilterSection>

                  {/* Date Range */}
                  <FilterSection title="Período">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                          De
                        </label>
                        <input
                          type="date"
                          value={filters.dateRange?.start?.toISOString().split('T')[0] || ''}
                          onChange={(e) => setFilters({
                            ...filters,
                            dateRange: {
                              ...filters.dateRange,
                              start: e.target.value ? new Date(e.target.value) : null,
                              end: filters.dateRange?.end || null
                            }
                          })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                          Até
                        </label>
                        <input
                          type="date"
                          value={filters.dateRange?.end?.toISOString().split('T')[0] || ''}
                          onChange={(e) => setFilters({
                            ...filters,
                            dateRange: {
                              start: filters.dateRange?.start || null,
                              ...filters.dateRange,
                              end: e.target.value ? new Date(e.target.value) : null
                            }
                          })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                    </div>
                  </FilterSection>

                  {/* Number Ranges */}
                  <FilterSection title="Quantidade de Propriedades">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                          Mínimo
                        </label>
                        <input
                          type="number"
                          min="0"
                          value={filters.minProperties || ''}
                          onChange={(e) => setFilters({
                            ...filters,
                            minProperties: e.target.value ? parseInt(e.target.value) : undefined
                          })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          placeholder="0"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                          Máximo
                        </label>
                        <input
                          type="number"
                          min="0"
                          value={filters.maxProperties || ''}
                          onChange={(e) => setFilters({
                            ...filters,
                            maxProperties: e.target.value ? parseInt(e.target.value) : undefined
                          })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          placeholder="∞"
                        />
                      </div>
                    </div>
                  </FilterSection>

                  {/* States */}
                  <FilterSection title="Estados">
                    <div className="flex flex-wrap gap-2">
                      {['MT', 'MS', 'GO', 'SP', 'PR', 'MG', 'BA', 'TO', 'PA', 'RO'].map((state) => (
                        <button
                          key={state}
                          onClick={() => {
                            const current = filters.states || [];
                            setFilters({
                              ...filters,
                              states: current.includes(state)
                                ? current.filter(s => s !== state)
                                : [...current, state]
                            });
                          }}
                          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                            (filters.states || []).includes(state)
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                          }`}
                        >
                          {state}
                        </button>
                      ))}
                    </div>
                  </FilterSection>

                  {/* Sort */}
                  <FilterSection title="Ordenação">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                          Ordenar por
                        </label>
                        <select
                          value={filters.sortBy || 'created_at'}
                          onChange={(e) => setFilters({
                            ...filters,
                            sortBy: e.target.value as FilterCriteria['sortBy']
                          })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="created_at">Data de Criação</option>
                          <option value="updated_at">Última Atualização</option>
                          <option value="target_name">Nome do Alvo</option>
                          <option value="total_results">Total de Resultados</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
                          Ordem
                        </label>
                        <select
                          value={filters.sortOrder || 'desc'}
                          onChange={(e) => setFilters({
                            ...filters,
                            sortOrder: e.target.value as 'asc' | 'desc'
                          })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="desc">Decrescente</option>
                          <option value="asc">Crescente</option>
                        </select>
                      </div>
                    </div>
                  </FilterSection>
                </div>

                {/* Actions */}
                <div className="flex gap-3 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={handleClear}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium transition-colors"
                  >
                    Limpar Filtros
                  </button>
                  <button
                    onClick={handleApply}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
                  >
                    Aplicar Filtros
                  </button>
                </div>
              </div>
            </SlideIn>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}

// Filter Section Component
function FilterSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h4 className="text-sm font-bold text-gray-900 dark:text-white mb-3">
        {title}
      </h4>
      {children}
    </div>
  );
}
