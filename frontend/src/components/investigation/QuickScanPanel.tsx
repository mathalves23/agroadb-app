import { Zap, Loader2, Download, FileSpreadsheet, FileText } from 'lucide-react'

interface QuickScanPanelProps {
  running: boolean
  progress: number
  total: number
  log: string[]
  disabled: boolean
  onRunScan: () => void
  onExportPDF: () => void
  onExportExcel?: () => void
  onExportCSV?: () => void
  exportLoading?: boolean
}

export function QuickScanPanel({
  running,
  progress,
  total,
  log,
  disabled,
  onRunScan,
  onExportPDF,
  onExportExcel,
  onExportCSV,
  exportLoading = false,
}: QuickScanPanelProps) {
  return (
    <>
      {/* Ações rápidas */}
      <div className="flex flex-wrap items-center gap-3">
        <button
          onClick={onRunScan}
          disabled={running || disabled}
          className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium shadow-sm transition ${
            running || disabled
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-600 hover:to-orange-600'
          }`}
        >
          {running ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Zap className="h-4 w-4" />
          )}
          {running
            ? `Consultando... (${progress}/${total})`
            : 'Consulta Rápida — Todas as Bases'}
        </button>
        <button
          onClick={onExportPDF}
          disabled={exportLoading}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium border border-gray-200 text-gray-700 hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Download className="h-4 w-4" />
          Exportar PDF
        </button>
        {onExportExcel && (
          <button
            onClick={onExportExcel}
            disabled={exportLoading}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium border border-green-200 text-green-700 hover:bg-green-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {exportLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileSpreadsheet className="h-4 w-4" />
            )}
            Exportar Excel
          </button>
        )}
        {onExportCSV && (
          <button
            onClick={onExportCSV}
            disabled={exportLoading}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium border border-blue-200 text-blue-700 hover:bg-blue-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {exportLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileText className="h-4 w-4" />
            )}
            Exportar CSV
          </button>
        )}
      </div>

      {/* Quick Scan Log */}
      {log.length > 0 && (
        <div className="bg-gray-800 rounded-xl p-4 text-xs font-mono text-gray-300 max-h-48 overflow-auto" role="log" aria-live="polite" aria-label="Log de varredura">
          {log.map((line, i) => (
            <div key={i} className={`py-0.5 ${line.startsWith('✓') ? 'text-emerald-400' : line.startsWith('✗') ? 'text-red-400' : 'text-gray-400'}`}>
              {line}
            </div>
          ))}
          {running && (
            <div
              className="mt-2 h-1.5 bg-gray-700 rounded-full overflow-hidden"
              role="progressbar"
              aria-valuenow={progress}
              aria-valuemin={0}
              aria-valuemax={total}
              aria-label={`Progresso da varredura: ${progress} de ${total}`}
            >
              <div
                className="h-full bg-amber-500 rounded-full transition-all duration-500"
                style={{ width: `${total > 0 ? (progress / total) * 100 : 0}%` }}
              />
            </div>
          )}
        </div>
      )}
    </>
  )
}
