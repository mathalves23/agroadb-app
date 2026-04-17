/**
 * Logger leve para desenvolvimento e erros em produção.
 * Compatível com Vite e Jest (NODE_ENV).
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error'

interface LogEntry {
  level: LogLevel
  message: string
  data?: unknown
  timestamp: Date
  component?: string
}

const LOG_COLORS: Record<LogLevel, string> = {
  debug: '#8b5cf6',
  info: '#3b82f6',
  warn: '#f59e0b',
  error: '#ef4444',
}

const LOG_ICONS: Record<LogLevel, string> = {
  debug: '🔍',
  info: 'ℹ️',
  warn: '⚠️',
  error: '❌',
}

function isDevEnvironment(): boolean {
  if (typeof process !== 'undefined' && process.env.NODE_ENV === 'production') {
    return false
  }
  try {
    return Boolean(import.meta.env?.DEV)
  } catch {
    return true
  }
}

class Logger {
  private readonly isDev = isDevEnvironment()
  private logHistory: LogEntry[] = []
  private readonly maxHistorySize = 100

  private log(
    level: LogLevel,
    message: string,
    data?: unknown,
    component?: string,
  ): void {
    const entry: LogEntry = {
      level,
      message,
      data,
      timestamp: new Date(),
      component,
    }

    this.logHistory.unshift(entry)
    if (this.logHistory.length > this.maxHistorySize) {
      this.logHistory.pop()
    }

    if (!this.isDev && level !== 'error') {
      return
    }

    const prefix = component ? `[${component}]` : ''
    const icon = LOG_ICONS[level]
    const color = LOG_COLORS[level]
    const style = `
      color: ${color};
      font-weight: bold;
      padding: 2px 6px;
      border-radius: 3px;
      background: ${color}15;
    `

    if (data !== undefined) {
      console.groupCollapsed(`%c${icon} ${prefix} ${message}`, style)
      console.log('Data:', data)
      console.log('Timestamp:', entry.timestamp.toISOString())
      console.groupEnd()
    } else {
      console.log(`%c${icon} ${prefix} ${message}`, style)
    }
  }

  debug(message: string, data?: unknown, component?: string): void {
    this.log('debug', message, data, component)
  }

  info(message: string, data?: unknown, component?: string): void {
    this.log('info', message, data, component)
  }

  warn(message: string, data?: unknown, component?: string): void {
    this.log('warn', message, data, component)
  }

  error(message: string, data?: unknown, component?: string): void {
    this.log('error', message, data, component)
    if (!this.isDev) {
      this.reportError(message, data, component)
    }
  }

  time(label: string): void {
    if (this.isDev) console.time(label)
  }

  timeEnd(label: string): void {
    if (this.isDev) console.timeEnd(label)
  }

  group(label: string): void {
    if (this.isDev) console.group(label)
  }

  groupEnd(): void {
    if (this.isDev) console.groupEnd()
  }

  getHistory(): LogEntry[] {
    return [...this.logHistory]
  }

  clearHistory(): void {
    this.logHistory = []
  }

  exportLogs(): string {
    return JSON.stringify(this.logHistory, null, 2)
  }

  private reportError(message: string, data?: unknown, component?: string): void {
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') return
    try {
      const errorReport = {
        message,
        data,
        component,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
      }
      const errors = JSON.parse(localStorage.getItem('error_reports') || '[]')
      errors.unshift(errorReport)
      if (errors.length > 50) errors.pop()
      localStorage.setItem('error_reports', JSON.stringify(errors))
    } catch {
      // ignore
    }
  }
}

const logger = new Logger()

export const log = {
  debug: (message: string, data?: unknown, component?: string) =>
    logger.debug(message, data, component),
  info: (message: string, data?: unknown, component?: string) =>
    logger.info(message, data, component),
  warn: (message: string, data?: unknown, component?: string) =>
    logger.warn(message, data, component),
  error: (message: string, data?: unknown, component?: string) =>
    logger.error(message, data, component),
  time: (label: string) => logger.time(label),
  timeEnd: (label: string) => logger.timeEnd(label),
  group: (label: string) => logger.group(label),
  groupEnd: () => logger.groupEnd(),
  getHistory: () => logger.getHistory(),
  clearHistory: () => logger.clearHistory(),
  exportLogs: () => logger.exportLogs(),
}

export default logger
