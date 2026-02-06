/**
 * Timeline Component - Linha do Tempo de Investigações
 * 
 * Visualiza histórico e eventos em ordem cronológica
 */
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { FadeIn, SlideIn } from '../components/Animations';

// Tipos
interface TimelineEvent {
  id: string;
  type: 'investigation' | 'scraper' | 'notification' | 'export' | 'system';
  title: string;
  description: string;
  timestamp: Date;
  status: 'success' | 'error' | 'warning' | 'info';
  metadata?: Record<string, any>;
  icon?: string;
}

interface TimelineProps {
  events: TimelineEvent[];
  groupBy?: 'day' | 'month' | 'none';
  filterBy?: string[];
  onEventClick?: (event: TimelineEvent) => void;
}

export function Timeline({
  events,
  groupBy = 'day',
  filterBy = [],
  onEventClick
}: TimelineProps) {
  const [selectedTypes, setSelectedTypes] = useState<string[]>(filterBy);

  // Filtrar eventos
  const filteredEvents = selectedTypes.length > 0
    ? events.filter(e => selectedTypes.includes(e.type))
    : events;

  // Agrupar eventos
  const groupedEvents = groupBy === 'none'
    ? { 'all': filteredEvents }
    : groupEvents(filteredEvents, groupBy);

  // Tipos de evento
  const eventTypes = [
    { type: 'investigation', label: 'Investigações', icon: '🔍', color: 'bg-blue-100 text-blue-600 dark:bg-blue-900/20' },
    { type: 'scraper', label: 'Scrapers', icon: '⚙️', color: 'bg-purple-100 text-purple-600 dark:bg-purple-900/20' },
    { type: 'notification', label: 'Notificações', icon: '🔔', color: 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/20' },
    { type: 'export', label: 'Exportações', icon: '📄', color: 'bg-green-100 text-green-600 dark:bg-green-900/20' },
    { type: 'system', label: 'Sistema', icon: '⚡', color: 'bg-gray-100 text-gray-600 dark:bg-gray-700' }
  ];

  const toggleType = (type: string) => {
    setSelectedTypes(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <FadeIn>
        <div className="flex flex-wrap gap-2">
          {eventTypes.map(({ type, label, icon, color }) => (
            <button
              key={type}
              onClick={() => toggleType(type)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                selectedTypes.length === 0 || selectedTypes.includes(type)
                  ? color
                  : 'bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-600'
              }`}
            >
              {icon} {label}
            </button>
          ))}
          
          {selectedTypes.length > 0 && (
            <button
              onClick={() => setSelectedTypes([])}
              className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              Limpar Filtros
            </button>
          )}
        </div>
      </FadeIn>

      {/* Timeline */}
      <div className="space-y-8">
        {Object.entries(groupedEvents).map(([group, groupEvents]) => (
          <div key={group}>
            {/* Group Header */}
            {groupBy !== 'none' && (
              <div className="flex items-center gap-4 mb-4">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                  {formatGroupLabel(group, groupBy)}
                </h3>
                <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700"></div>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {groupEvents.length} {groupEvents.length === 1 ? 'evento' : 'eventos'}
                </span>
              </div>
            )}

            {/* Events */}
            <div className="relative">
              {/* Vertical Line */}
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>

              {/* Event Items */}
              <div className="space-y-4">
                {groupEvents.map((event, index) => (
                  <SlideIn
                    key={event.id}
                    direction="left"
                    delay={index * 0.05}
                  >
                    <TimelineItem
                      event={event}
                      onClick={() => onEventClick?.(event)}
                    />
                  </SlideIn>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredEvents.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400 text-lg">
            📭 Nenhum evento encontrado
          </p>
          {selectedTypes.length > 0 && (
            <button
              onClick={() => setSelectedTypes([])}
              className="mt-4 text-green-600 hover:text-green-700"
            >
              Limpar filtros
            </button>
          )}
        </div>
      )}
    </div>
  );
}

// Timeline Item Component
function TimelineItem({ event, onClick }: { event: TimelineEvent; onClick?: () => void }) {
  const statusColors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500'
  };

  const statusIcons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };

  const typeIcons = {
    investigation: '🔍',
    scraper: '⚙️',
    notification: '🔔',
    export: '📄',
    system: '⚡'
  };

  return (
    <motion.div
      whileHover={{ x: 4 }}
      className="relative pl-12 cursor-pointer"
      onClick={onClick}
    >
      {/* Icon Circle */}
      <div className={`absolute left-0 w-8 h-8 rounded-full ${statusColors[event.status]} flex items-center justify-center text-white font-bold shadow-lg`}>
        {statusIcons[event.status]}
      </div>

      {/* Content Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow p-4 border-l-4" style={{ borderColor: `var(--color-${event.status})` }}>
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{event.icon || typeIcons[event.type]}</span>
            <h4 className="font-bold text-gray-900 dark:text-white">{event.title}</h4>
          </div>
          <time className="text-sm text-gray-500 dark:text-gray-400">
            {format(event.timestamp, 'HH:mm', { locale: ptBR })}
          </time>
        </div>

        <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
          {event.description}
        </p>

        {/* Metadata */}
        {event.metadata && Object.keys(event.metadata).length > 0 && (
          <div className="flex flex-wrap gap-2">
            {Object.entries(event.metadata).slice(0, 3).map(([key, value]) => (
              <span
                key={key}
                className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
              >
                {key}: <strong>{String(value)}</strong>
              </span>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

// Helper functions
function groupEvents(events: TimelineEvent[], groupBy: 'day' | 'month'): Record<string, TimelineEvent[]> {
  const groups: Record<string, TimelineEvent[]> = {};

  events.forEach(event => {
    const key = groupBy === 'day'
      ? format(event.timestamp, 'yyyy-MM-dd')
      : format(event.timestamp, 'yyyy-MM');

    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(event);
  });

  // Ordenar por data (mais recente primeiro)
  return Object.fromEntries(
    Object.entries(groups).sort((a, b) => b[0].localeCompare(a[0]))
  );
}

function formatGroupLabel(group: string, groupBy: 'day' | 'month'): string {
  const date = new Date(group + (groupBy === 'month' ? '-01' : ''));
  
  if (groupBy === 'day') {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (format(date, 'yyyy-MM-dd') === format(today, 'yyyy-MM-dd')) {
      return '📅 Hoje';
    } else if (format(date, 'yyyy-MM-dd') === format(yesterday, 'yyyy-MM-dd')) {
      return '📅 Ontem';
    } else {
      return format(date, "d 'de' MMMM 'de' yyyy", { locale: ptBR });
    }
  } else {
    return format(date, "MMMM 'de' yyyy", { locale: ptBR });
  }
}

// Exemplo de uso com dados mock
export function TimelineDemo() {
  const mockEvents: TimelineEvent[] = [
    {
      id: '1',
      type: 'investigation',
      title: 'Nova investigação criada',
      description: 'Investigação "Fazenda Santa Rita" foi iniciada',
      timestamp: new Date(),
      status: 'info',
      metadata: { target: 'João Silva', cpf: '123.456.789-00' }
    },
    {
      id: '2',
      type: 'scraper',
      title: 'CAR Scraper concluído',
      description: 'Encontradas 12 propriedades no CAR',
      timestamp: new Date(Date.now() - 3600000),
      status: 'success',
      metadata: { properties: 12, time: '2.3s' }
    },
    {
      id: '3',
      type: 'scraper',
      title: 'INCRA Scraper falhou',
      description: 'Timeout ao buscar dados do INCRA',
      timestamp: new Date(Date.now() - 7200000),
      status: 'error',
      metadata: { error: 'Timeout', retry: 'Em 30min' }
    },
    {
      id: '4',
      type: 'export',
      title: 'Relatório PDF gerado',
      description: 'Relatório detalhado exportado com sucesso',
      timestamp: new Date(Date.now() - 86400000),
      status: 'success',
      metadata: { format: 'PDF', pages: 23, size: '2.4 MB' }
    }
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          📅 Timeline de Eventos
        </h2>
      </div>

      <Timeline
        events={mockEvents}
        groupBy="day"
        onEventClick={() => {}}
      />
    </div>
  );
}
