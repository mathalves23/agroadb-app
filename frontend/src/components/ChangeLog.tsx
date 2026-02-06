import React, { useState, useEffect } from 'react';
import { History, FileText, Share2, Edit3, Plus, Trash2, MessageSquare, UserPlus, UserMinus, Eye, AlertTriangle, CheckCircle, XCircle, Activity } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface ChangeLogEntry {
  id: number;
  user_id: number;
  user_name: string;
  user_email?: string;
  action: string;
  field_changed?: string;
  old_value?: any;
  new_value?: any;
  description?: string;
  timestamp: string;
}

interface ChangeLogProps {
  investigationId: number;
}

export default function ChangeLog({ investigationId }: ChangeLogProps) {
  const [entries, setEntries] = useState<ChangeLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    loadChangeLog();
  }, [investigationId]);

  const loadChangeLog = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/v1/collaboration/investigations/${investigationId}/changelog`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setEntries(data.changelog);
      }
    } catch (error) {
      // silenced for production
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (action: string) => {
    const actionLower = action.toLowerCase();
    const icons: Record<string, any> = {
      created: Plus,
      create: Plus,
      updated: Edit3,
      update: Edit3,
      edited: Edit3,
      edit: Edit3,
      shared: Share2,
      share: Share2,
      commented: MessageSquare,
      comment: MessageSquare,
      deleted: Trash2,
      delete: Trash2,
      removed: XCircle,
      remove: XCircle,
      added: UserPlus,
      add: UserPlus,
      revoked: UserMinus,
      revoke: UserMinus,
      viewed: Eye,
      view: Eye,
      status_changed: Activity,
      approved: CheckCircle,
      rejected: XCircle,
      warning: AlertTriangle,
    };
    return icons[actionLower] || FileText;
  };

  const getActionColor = (action: string) => {
    const actionLower = action.toLowerCase();
    const colors: Record<string, string> = {
      created: 'bg-green-100 text-green-700 border-green-300',
      create: 'bg-green-100 text-green-700 border-green-300',
      updated: 'bg-blue-100 text-blue-700 border-blue-300',
      update: 'bg-blue-100 text-blue-700 border-blue-300',
      edited: 'bg-blue-100 text-blue-700 border-blue-300',
      edit: 'bg-blue-100 text-blue-700 border-blue-300',
      shared: 'bg-purple-100 text-purple-700 border-purple-300',
      share: 'bg-purple-100 text-purple-700 border-purple-300',
      commented: 'bg-cyan-100 text-cyan-700 border-cyan-300',
      comment: 'bg-cyan-100 text-cyan-700 border-cyan-300',
      deleted: 'bg-red-100 text-red-700 border-red-300',
      delete: 'bg-red-100 text-red-700 border-red-300',
      removed: 'bg-red-100 text-red-700 border-red-300',
      remove: 'bg-red-100 text-red-700 border-red-300',
      added: 'bg-emerald-100 text-emerald-700 border-emerald-300',
      add: 'bg-emerald-100 text-emerald-700 border-emerald-300',
      revoked: 'bg-orange-100 text-orange-700 border-orange-300',
      revoke: 'bg-orange-100 text-orange-700 border-orange-300',
      viewed: 'bg-gray-100 text-gray-700 border-gray-300',
      view: 'bg-gray-100 text-gray-700 border-gray-300',
      status_changed: 'bg-indigo-100 text-indigo-700 border-indigo-300',
      approved: 'bg-green-100 text-green-700 border-green-300',
      rejected: 'bg-red-100 text-red-700 border-red-300',
      warning: 'bg-amber-100 text-amber-700 border-amber-300',
    };
    return colors[actionLower] || 'bg-gray-100 text-gray-700 border-gray-300';
  };

  const getActionLabel = (action: string) => {
    const actionLower = action.toLowerCase();
    const labels: Record<string, string> = {
      created: 'Criou',
      create: 'Criou',
      updated: 'Atualizou',
      update: 'Atualizou',
      edited: 'Editou',
      edit: 'Editou',
      shared: 'Compartilhou',
      share: 'Compartilhou',
      commented: 'Comentou',
      comment: 'Comentou',
      deleted: 'Deletou',
      delete: 'Deletou',
      removed: 'Removeu',
      remove: 'Removeu',
      added: 'Adicionou',
      add: 'Adicionou',
      revoked: 'Revogou',
      revoke: 'Revogou',
      viewed: 'Visualizou',
      view: 'Visualizou',
      status_changed: 'Mudou status',
      approved: 'Aprovou',
      rejected: 'Rejeitou',
      warning: 'Alerta',
    };
    return labels[actionLower] || action;
  };

  const filteredEntries = filter === 'all'
    ? entries
    : entries.filter(e => e.action.toLowerCase().includes(filter.toLowerCase()));

  const getInitials = (name: string) => {
    if (!name || name === 'Sistema') return 'S';
    return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
  };

  const renderDiff = (oldValue: any, newValue: any, field: string) => {
    if (oldValue === null || oldValue === undefined) return null;
    if (newValue === null || newValue === undefined) return null;

    const oldStr = String(oldValue);
    const newStr = String(newValue);

    return (
      <div className="mt-2 p-3 bg-white rounded border border-gray-200 text-xs">
        <div className="font-medium text-gray-700 mb-2">Campo alterado: {field}</div>
        <div className="space-y-1">
          <div className="flex items-start gap-2">
            <span className="text-red-600 font-medium shrink-0">-</span>
            <span className="text-red-700 bg-red-50 px-2 py-1 rounded flex-1 break-all">{oldStr}</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-green-600 font-medium shrink-0">+</span>
            <span className="text-green-700 bg-green-50 px-2 py-1 rounded flex-1 break-all">{newStr}</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <History className="h-5 w-5 text-indigo-600" />
          Histórico de Alterações
          <span className="text-sm font-normal text-gray-500">({filteredEntries.length})</span>
        </h3>

        {/* Filter */}
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
        >
          <option value="all">Todas as ações</option>
          <option value="created">Criações</option>
          <option value="updated">Atualizações</option>
          <option value="shared">Compartilhamentos</option>
          <option value="commented">Comentários</option>
          <option value="deleted">Exclusões</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">
          <div className="animate-spin h-8 w-8 border-4 border-indigo-600 border-t-transparent rounded-full mx-auto mb-3"></div>
          <p className="text-sm">Carregando histórico...</p>
        </div>
      ) : filteredEntries.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <History className="h-12 w-12 mx-auto mb-3 text-gray-300" />
          <p className="text-sm font-medium">Nenhuma alteração encontrada</p>
          <p className="text-xs text-gray-400 mt-1">
            {filter !== 'all' ? 'Tente outro filtro' : 'O histórico ficará registrado aqui'}
          </p>
        </div>
      ) : (
        <div className="relative">
          {/* Timeline Line */}
          <div className="absolute left-[30px] top-0 bottom-0 w-0.5 bg-gradient-to-b from-indigo-200 via-purple-200 to-gray-200"></div>

          {/* Entries */}
          <div className="space-y-4">
            {filteredEntries.map((entry, index) => {
              const Icon = getActionIcon(entry.action);
              const colorClass = getActionColor(entry.action);
              const isRecent = index === 0;

              return (
                <div key={entry.id} className="relative flex gap-4 group">
                  {/* Icon with pulse animation for recent */}
                  <div className="relative shrink-0">
                    <div className={`w-[60px] h-[60px] rounded-full ${colorClass} border-4 flex items-center justify-center z-10 bg-white shadow-lg transition-transform group-hover:scale-110`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    {isRecent && (
                      <div className="absolute inset-0 rounded-full bg-indigo-400 animate-ping opacity-20"></div>
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 pt-2 pb-4">
                    <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 hover:shadow-md hover:border-gray-300 transition-all">
                      <div className="flex items-start justify-between gap-3 mb-3">
                        <div className="flex items-center gap-3 flex-1">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center shadow-sm">
                            <span className="text-xs font-bold text-white">
                              {getInitials(entry.user_name)}
                            </span>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="text-sm font-semibold text-gray-900">
                                {entry.user_name}
                              </span>
                              <span className="text-sm text-gray-600">
                                {getActionLabel(entry.action).toLowerCase()}
                              </span>
                              {isRecent && (
                                <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                                  Recente
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                              <span>{format(new Date(entry.timestamp), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}</span>
                              <span>•</span>
                              <span>{formatDistanceToNow(new Date(entry.timestamp), { addSuffix: true, locale: ptBR })}</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {entry.description && (
                        <p className="text-sm text-gray-700 mb-2">
                          {entry.description}
                        </p>
                      )}

                      {/* Field Changed Info */}
                      {entry.field_changed && (
                        <div className="mb-2">
                          <span className="inline-flex items-center px-2.5 py-1 bg-indigo-50 text-indigo-700 text-xs font-medium rounded-full border border-indigo-200">
                            Campo: {entry.field_changed}
                          </span>
                        </div>
                      )}

                      {/* Diff Display */}
                      {entry.old_value && entry.new_value && entry.field_changed && 
                        renderDiff(entry.old_value, entry.new_value, entry.field_changed)
                      }

                      {/* New Value Only */}
                      {!entry.old_value && entry.new_value && (
                        <div className="mt-2 p-3 bg-green-50 rounded border border-green-200">
                          <p className="text-xs font-semibold text-green-700 mb-1">Novo valor:</p>
                          <p className="text-xs text-green-800">
                            {typeof entry.new_value === 'object' 
                              ? JSON.stringify(entry.new_value, null, 2)
                              : String(entry.new_value)
                            }
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
