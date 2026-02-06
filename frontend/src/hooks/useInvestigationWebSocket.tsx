/**
 * Hook React para WebSocket de Investigação
 * 
 * Gerencia conexão WebSocket, notificações em tempo real e progresso
 * 
 * @example
 * ```tsx
 * function InvestigationPage({ investigationId }) {
 *   const { 
 *     progress, 
 *     notifications, 
 *     isConnected 
 *   } = useInvestigationWebSocket(investigationId);
 *   
 *   return (
 *     <div>
 *       <ProgressBar value={progress.percentage} />
 *       {notifications.map(n => <Notification key={n.id} data={n} />)}
 *     </div>
 *   );
 * }
 * ```
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'react-hot-toast';

interface WebSocketNotification {
  type: string;
  investigation_id: string;
  task_id?: string;
  scraper_type?: string;
  status?: string;
  result?: Record<string, unknown>;
  error?: string;
  retry_count?: number;
  max_retries?: number;
  percentage?: number;
  total_tasks?: number;
  completed_tasks?: number;
  failed_tasks?: number;
  running_tasks?: number;
  message?: string;
  timestamp: string;
}

interface InvestigationProgress {
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  running_tasks: number;
  pending_tasks: number;
  percentage: number;
  tasks: Record<string, string>;
  updated_at: string;
}

interface UseInvestigationWebSocketReturn {
  isConnected: boolean;
  progress: InvestigationProgress;
  notifications: WebSocketNotification[];
  lastNotification: WebSocketNotification | null;
  error: Error | null;
  reconnect: () => void;
}

const INITIAL_PROGRESS: InvestigationProgress = {
  total_tasks: 0,
  completed_tasks: 0,
  failed_tasks: 0,
  running_tasks: 0,
  pending_tasks: 0,
  percentage: 0,
  tasks: {},
  updated_at: new Date().toISOString(),
};

export function useInvestigationWebSocket(
  investigationId: string,
  options?: {
    autoReconnect?: boolean;
    maxReconnectAttempts?: number;
    showToasts?: boolean;
    wsUrl?: string;
  }
): UseInvestigationWebSocketReturn {
  const {
    autoReconnect = true,
    maxReconnectAttempts = 5,
    showToasts = true,
    wsUrl = 'ws://localhost:8000/api/v1',
  } = options || {};

  const [isConnected, setIsConnected] = useState(false);
  const [progress, setProgress] = useState<InvestigationProgress>(INITIAL_PROGRESS);
  const [notifications, setNotifications] = useState<WebSocketNotification[]>([]);
  const [lastNotification, setLastNotification] = useState<WebSocketNotification | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(`${wsUrl}/ws/investigations/${investigationId}`);

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;

        if (showToasts) {
          toast.success('Conectado ao sistema de notificações');
        }

        // Ping a cada 30s para manter conexão ativa
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        const notification: WebSocketNotification = JSON.parse(event.data);

        // Adicionar à lista de notificações
        setNotifications((prev) => [...prev.slice(-50), notification]); // Manter últimas 50
        setLastNotification(notification);

        // Processar por tipo
        handleNotification(notification);
      };

      ws.onerror = () => {
        setError(new Error('Erro na conexão WebSocket'));
      };

      ws.onclose = () => {
        setIsConnected(false);

        // Limpar interval de ping
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Tentar reconectar se habilitado
        if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError(new Error('Não foi possível reconectar ao WebSocket'));
          
          if (showToasts) {
            toast.error('Conexão perdida. Por favor, recarregue a página.');
          }
        }
      };

      wsRef.current = ws;
    } catch (err) {
      setError(err as Error);
    }
  }, [investigationId, wsUrl, autoReconnect, maxReconnectAttempts, showToasts]);

  const handleNotification = (notification: WebSocketNotification) => {
    switch (notification.type) {
      case 'connected':
        // Conexão estabelecida
        break;

      case 'task_started':
        if (showToasts) {
          toast.loading(`Processando ${notification.scraper_type}...`, {
            id: notification.task_id,
          });
        }
        break;

      case 'task_completed':
        if (showToasts) {
          toast.success(`${notification.scraper_type} concluído!`, {
            id: notification.task_id,
          });
        }
        break;

      case 'task_failed':
        if (showToasts) {
          toast.error(
            `${notification.scraper_type} falhou: ${notification.error}`,
            { id: notification.task_id }
          );
        }
        break;

      case 'task_retrying':
        if (showToasts) {
          toast.loading(
            `Tentando novamente ${notification.scraper_type} (${notification.retry_count}/${notification.max_retries})...`,
            { id: notification.task_id }
          );
        }
        break;

      case 'investigation_progress':
        setProgress({
          total_tasks: notification.total_tasks || 0,
          completed_tasks: notification.completed_tasks || 0,
          failed_tasks: notification.failed_tasks || 0,
          running_tasks: notification.running_tasks || 0,
          pending_tasks:
            (notification.total_tasks || 0) -
            (notification.completed_tasks || 0) -
            (notification.failed_tasks || 0) -
            (notification.running_tasks || 0),
          percentage: notification.percentage || 0,
          tasks: {}, // Seria preenchido se necessário
          updated_at: notification.timestamp,
        });
        break;

      case 'circuit_breaker_opened':
        if (showToasts) {
          toast.error(notification.message || 'Circuit breaker aberto', {
            duration: 10000,
          });
        }
        break;

      case 'system_alert':
        if (showToasts) {
          const toastFn = notification.message?.includes('error') ? toast.error : toast;
          toastFn(notification.message || 'Alerta do sistema');
        }
        break;
    }
  };

  const reconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect]);

  useEffect(() => {
    connect();

    return () => {
      // Cleanup
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };
  }, [connect]);

  return {
    isConnected,
    progress,
    notifications,
    lastNotification,
    error,
    reconnect,
  };
}

/**
 * Componente de exemplo usando o hook
 */
export function InvestigationMonitor({ investigationId }: { investigationId: string }) {
  const { isConnected, progress, notifications, reconnect } = useInvestigationWebSocket(
    investigationId
  );

  return (
    <div className="space-y-4">
      {/* Status de Conexão */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Conectado' : 'Desconectado'}
          </span>
        </div>
        {!isConnected && (
          <button
            onClick={reconnect}
            className="text-sm text-blue-600 hover:underline"
          >
            Reconectar
          </button>
        )}
      </div>

      {/* Barra de Progresso */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="font-medium">Progresso da Investigação</span>
          <span className="text-gray-600">
            {progress.completed_tasks}/{progress.total_tasks} concluídos
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className="bg-blue-600 h-4 rounded-full transition-all duration-500"
            style={{ width: `${progress.percentage}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500">
          <span>{progress.percentage.toFixed(0)}% completo</span>
          <div className="flex gap-4">
            <span>✅ {progress.completed_tasks}</span>
            <span>🔄 {progress.running_tasks}</span>
            <span>❌ {progress.failed_tasks}</span>
            <span>⏳ {progress.pending_tasks}</span>
          </div>
        </div>
      </div>

      {/* Feed de Notificações */}
      <div className="space-y-2">
        <h3 className="text-sm font-medium">Atividades Recentes</h3>
        <div className="max-h-48 overflow-y-auto space-y-2">
          {notifications.slice(-10).reverse().map((notification, index) => (
            <div
              key={`${notification.task_id}-${index}`}
              className="text-xs p-2 bg-gray-50 rounded border border-gray-200"
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">
                  {getNotificationIcon(notification.type)} {notification.scraper_type || 'Sistema'}
                </span>
                <span className="text-gray-500">
                  {new Date(notification.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-gray-600 mt-1">{notification.message}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function getNotificationIcon(type: string): string {
  const icons: Record<string, string> = {
    connected: '🔌',
    task_started: '🎯',
    task_completed: '✅',
    task_failed: '❌',
    task_retrying: '🔄',
    investigation_progress: '📊',
    circuit_breaker_opened: '⚡',
    system_alert: '🔔',
  };
  return icons[type] || '📨';
}
