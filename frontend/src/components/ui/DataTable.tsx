import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDown,
  ChevronUp,
  ChevronsUpDown,
  Search,
  Filter,
  Download,
  MoreVertical,
  Eye,
  Edit,
  Trash2,
  Copy
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button, Badge, Avatar, Input } from './Controls';
import { Dropdown } from './Overlays';

// ==================== DATA TABLE ====================

export interface Column<T> {
  key: string;
  header: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: unknown, row: T) => React.ReactNode;
  width?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (row: T) => void;
  selectedRows?: Set<string>;
  onSelectRows?: (ids: Set<string>) => void;
  actions?: (row: T) => React.ReactNode;
  loading?: boolean;
  emptyState?: React.ReactNode;
  pagination?: {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
  };
}

export function DataTable<T extends { id: string }>({
  data,
  columns,
  onRowClick,
  selectedRows,
  onSelectRows,
  actions,
  loading = false,
  emptyState,
  pagination,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = React.useState<string | null>(null);
  const [sortDirection, setSortDirection] = React.useState<'asc' | 'desc'>('asc');
  const [searchQuery, setSearchQuery] = React.useState('');
  const [filters, setFilters] = React.useState<Record<string, string>>({});

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const handleSelectAll = () => {
    if (selectedRows?.size === data.length) {
      onSelectRows?.(new Set());
    } else {
      onSelectRows?.(new Set(data.map(row => row.id)));
    }
  };

  const handleSelectRow = (id: string) => {
    const newSelection = new Set(selectedRows);
    if (newSelection.has(id)) {
      newSelection.delete(id);
    } else {
      newSelection.add(id);
    }
    onSelectRows?.(newSelection);
  };

  // Filtrar e ordenar dados
  let processedData = [...data];

  // Aplicar busca
  if (searchQuery) {
    processedData = processedData.filter(row =>
      Object.values(row).some(value =>
        String(value).toLowerCase().includes(searchQuery.toLowerCase())
      )
    );
  }

  // Aplicar ordenação
  if (sortKey) {
    processedData.sort((a, b) => {
      const aValue = (a as Record<string, unknown>)[sortKey];
      const bValue = (b as Record<string, unknown>)[sortKey];
      const direction = sortDirection === 'asc' ? 1 : -1;
      return aValue < bValue ? -direction : direction;
    });
  }

  return (
    <div className="w-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-4 mb-4">
        <div className="flex-1 max-w-md">
          <Input
            placeholder="Buscar..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leftIcon={<Search className="w-4 h-4" />}
          />
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" icon={<Filter className="w-4 h-4" />}>
            Filtros
          </Button>
          <Button variant="outline" size="sm" icon={<Download className="w-4 h-4" />}>
            Exportar
          </Button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-800">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              {onSelectRows && (
                <th className="w-12 px-6 py-4">
                  <input
                    type="checkbox"
                    checked={selectedRows?.size === data.length && data.length > 0}
                    onChange={handleSelectAll}
                    className="w-4 h-4 rounded border-gray-300 text-green-600 focus:ring-green-500"
                  />
                </th>
              )}
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={cn(
                    'px-6 py-4 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider',
                    column.sortable && 'cursor-pointer select-none hover:text-gray-700 dark:hover:text-gray-300',
                    column.width
                  )}
                  onClick={() => column.sortable && handleSort(column.key)}
                >
                  <div className="flex items-center gap-2">
                    {column.header}
                    {column.sortable && (
                      <span className="text-gray-400">
                        {sortKey === column.key ? (
                          sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                        ) : (
                          <ChevronsUpDown className="w-4 h-4" />
                        )}
                      </span>
                    )}
                  </div>
                </th>
              ))}
              {actions && (
                <th className="w-20 px-6 py-4 text-right text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Ações
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
            {loading ? (
              <tr>
                <td colSpan={columns.length + (onSelectRows ? 1 : 0) + (actions ? 1 : 0)} className="px-6 py-12">
                  <div className="flex items-center justify-center">
                    <div className="animate-spin w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full" />
                  </div>
                </td>
              </tr>
            ) : processedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length + (onSelectRows ? 1 : 0) + (actions ? 1 : 0)} className="px-6 py-12">
                  {emptyState || (
                    <div className="text-center text-gray-500 dark:text-gray-400">
                      Nenhum resultado encontrado
                    </div>
                  )}
                </td>
              </tr>
            ) : (
              processedData.map((row, index) => (
                <motion.tr
                  key={row.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => onRowClick?.(row)}
                  className={cn(
                    'hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors',
                    onRowClick && 'cursor-pointer',
                    selectedRows?.has(row.id) && 'bg-green-50 dark:bg-green-950/20'
                  )}
                >
                  {onSelectRows && (
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedRows?.has(row.id)}
                        onChange={() => handleSelectRow(row.id)}
                        onClick={(e) => e.stopPropagation()}
                        className="w-4 h-4 rounded border-gray-300 text-green-600 focus:ring-green-500"
                      />
                    </td>
                  )}
                  {columns.map((column) => (
                    <td key={column.key} className="px-6 py-4 text-sm text-gray-900 dark:text-white">
                      {column.render
                        ? column.render((row as Record<string, unknown>)[column.key], row)
                        : String((row as Record<string, unknown>)[column.key])}
                    </td>
                  ))}
                  {actions && (
                    <td className="px-6 py-4 text-right" onClick={(e) => e.stopPropagation()}>
                      {actions(row)}
                    </td>
                  )}
                </motion.tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && (
        <div className="flex items-center justify-between mt-4">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Mostrando {processedData.length} de {data.length} resultados
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => pagination.onPageChange(pagination.currentPage - 1)}
              disabled={pagination.currentPage === 1}
            >
              Anterior
            </Button>
            {Array.from({ length: pagination.totalPages }, (_, i) => i + 1).map((page) => (
              <Button
                key={page}
                variant={page === pagination.currentPage ? 'solid' : 'ghost'}
                size="sm"
                onClick={() => pagination.onPageChange(page)}
              >
                {page}
              </Button>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() => pagination.onPageChange(pagination.currentPage + 1)}
              disabled={pagination.currentPage === pagination.totalPages}
            >
              Próximo
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

// ==================== EXAMPLE USAGE ====================

export const ExampleTable = () => {
  interface Investigation {
    id: string;
    name: string;
    type: string;
    status: 'active' | 'pending' | 'completed' | 'cancelled';
    progress: number;
    createdAt: string;
    assignee: {
      name: string;
      avatar?: string;
    };
  }

  const sampleData: Investigation[] = [
    {
      id: '1',
      name: 'Fazenda São João',
      type: 'Propriedade Rural',
      status: 'active',
      progress: 75,
      createdAt: '2026-02-01',
      assignee: { name: 'João Silva' },
    },
    {
      id: '2',
      name: 'Empresa XYZ Ltda',
      type: 'Due Diligence',
      status: 'completed',
      progress: 100,
      createdAt: '2026-01-28',
      assignee: { name: 'Maria Santos' },
    },
    {
      id: '3',
      name: 'Sítio Santa Clara',
      type: 'Análise Patrimonial',
      status: 'pending',
      progress: 25,
      createdAt: '2026-02-03',
      assignee: { name: 'Pedro Costa' },
    },
  ];

  const [selectedRows, setSelectedRows] = React.useState<Set<string>>(new Set());

  const columns: Column<Investigation>[] = [
    {
      key: 'name',
      header: 'Nome',
      sortable: true,
      render: (value, row) => (
        <div>
          <div className="font-semibold text-gray-900 dark:text-white">{value}</div>
          <div className="text-xs text-gray-500">{row.type}</div>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (value) => {
        const colors = {
          active: 'primary',
          pending: 'warning',
          completed: 'success',
          cancelled: 'error',
        } as const;
        const labels = {
          active: 'Ativo',
          pending: 'Pendente',
          completed: 'Concluído',
          cancelled: 'Cancelado',
        };
        return <Badge color={colors[value as keyof typeof colors]}>{labels[value as keyof typeof labels]}</Badge>;
      },
    },
    {
      key: 'progress',
      header: 'Progresso',
      render: (value) => (
        <div className="flex items-center gap-3">
          <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-emerald-600 rounded-full transition-all duration-300"
              style={{ width: `${value}%` }}
            />
          </div>
          <span className="text-sm font-medium text-gray-600 dark:text-gray-400 w-12 text-right">
            {value}%
          </span>
        </div>
      ),
    },
    {
      key: 'assignee',
      header: 'Responsável',
      render: (value) => (
        <div className="flex items-center gap-2">
          <Avatar src={value.avatar} name={value.name} size="sm" />
          <span className="text-sm">{value.name}</span>
        </div>
      ),
    },
    {
      key: 'createdAt',
      header: 'Data',
      sortable: true,
      render: (value) => new Date(value).toLocaleDateString('pt-BR'),
    },
  ];

  return (
    <DataTable
      data={sampleData}
      columns={columns}
      selectedRows={selectedRows}
      onSelectRows={setSelectedRows}
      onRowClick={() => {}}
      actions={(row) => (
        <Dropdown
          trigger={
            <Button variant="ghost" size="sm" icon={<MoreVertical className="w-4 h-4" />} />
          }
          items={[
            {
              id: 'view',
              label: 'Visualizar',
              icon: <Eye className="w-4 h-4" />,
              onClick: () => {},
            },
            {
              id: 'edit',
              label: 'Editar',
              icon: <Edit className="w-4 h-4" />,
              onClick: () => {},
            },
            {
              id: 'duplicate',
              label: 'Duplicar',
              icon: <Copy className="w-4 h-4" />,
              onClick: () => {},
            },
            {
              id: 'delete',
              label: 'Excluir',
              icon: <Trash2 className="w-4 h-4" />,
              onClick: () => {},
              danger: true,
            },
          ]}
        />
      )}
      pagination={{
        currentPage: 1,
        totalPages: 5,
        onPageChange: () => {},
      }}
    />
  );
};
