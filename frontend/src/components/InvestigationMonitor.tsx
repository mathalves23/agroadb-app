/**
 * Painel de exemplo para progresso WebSocket (separado do hook para react-refresh).
 */
import { useInvestigationWebSocket } from '@/hooks/useInvestigationWebSocket'

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
  }
  return icons[type] || '📨'
}

export function InvestigationMonitor({ investigationId }: { investigationId: string }) {
  const { isConnected, progress, notifications, reconnect } = useInvestigationWebSocket(investigationId)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-600">{isConnected ? 'Conectado' : 'Desconectado'}</span>
        </div>
        {!isConnected && (
          <button type="button" onClick={reconnect} className="text-sm text-blue-600 hover:underline">
            Reconectar
          </button>
        )}
      </div>

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

      <div className="space-y-2">
        <h3 className="text-sm font-medium">Atividades Recentes</h3>
        <div className="max-h-48 overflow-y-auto space-y-2">
          {notifications
            .slice(-10)
            .reverse()
            .map((notification, index) => (
              <div
                key={`${notification.task_id}-${index}`}
                className="text-xs p-2 bg-gray-50 rounded border border-gray-200"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">
                    {getNotificationIcon(notification.type)} {notification.scraper_type || 'Sistema'}
                  </span>
                  <span className="text-gray-500">{new Date(notification.timestamp).toLocaleTimeString()}</span>
                </div>
                <p className="text-gray-600 mt-1">{notification.message}</p>
              </div>
            ))}
        </div>
      </div>
    </div>
  )
}
