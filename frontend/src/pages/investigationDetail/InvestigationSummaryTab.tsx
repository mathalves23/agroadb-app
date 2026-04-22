import { Scale, Search } from 'lucide-react'

import {
  DossierSummary,
  KpiCards,
  PropertiesList,
  CompaniesList,
  QueryCharts,
  QuickScanPanel,
} from '@/components/investigation'
import { formatDateTime } from '@/lib/utils'
import { buildSummaryFields } from '@/pages/investigationDetail/summary'
import type { LegalQueryEntry } from '@/services/legalService'
import type { Company, Investigation, Property } from '@/types/api'
import type { SummarySource } from '@/pages/investigationDetail/summary'

type Props = {
  chartByDate: Array<{ date: string; consultas: number }>
  chartByProvider: Array<{ name: string; consultas: number; resultados: number }>
  companies?: Company[]
  defaultCpfCnpj: string
  exportLoading: boolean
  handleExportCSV: () => void
  handleExportExcel: () => void
  isDevMode: boolean
  investigation: Investigation
  legalQueries?: LegalQueryEntry[]
  latestQuery: LegalQueryEntry | null
  onApplyCpfCnpj: () => void
  onExportPDF: () => void
  onExportTrustBundle: () => void
  onRunQuickScan: () => void
  onOpenLegalTab: () => void
  pieData: Array<{ name: string; value: number }>
  properties?: Property[]
  quickScanLog: string[]
  quickScanProgress: number
  quickScanRunning: boolean
  quickScanTotal: number
  summaryCpfCnpj: string
  summarySources: SummarySource[]
  summarySourcesWithDataCount: number
  totalQueries: number
  totalResults: number
}

export function InvestigationSummaryTab({
  chartByDate,
  chartByProvider,
  companies,
  defaultCpfCnpj,
  exportLoading,
  handleExportCSV,
  handleExportExcel,
  isDevMode,
  investigation,
  legalQueries,
  latestQuery,
  onApplyCpfCnpj,
  onExportPDF,
  onExportTrustBundle,
  onRunQuickScan,
  onOpenLegalTab,
  pieData,
  properties,
  quickScanLog,
  quickScanProgress,
  quickScanRunning,
  quickScanTotal,
  summaryCpfCnpj,
  summarySources,
  summarySourcesWithDataCount,
  totalQueries,
  totalResults,
}: Props) {
  return (
    <div className="space-y-6">
      <QuickScanPanel
        running={quickScanRunning}
        progress={quickScanProgress}
        total={quickScanTotal}
        log={quickScanLog}
        disabled={!defaultCpfCnpj}
        onRunScan={onRunQuickScan}
        onExportPDF={onExportPDF}
        onExportExcel={handleExportExcel}
        onExportCSV={handleExportCSV}
        onExportTrustBundle={onExportTrustBundle}
        exportLoading={exportLoading}
      />

      <p className="max-w-3xl text-xs leading-relaxed text-gray-500">
        A consulta rápida e o passo de dados cadastrais usam integrações e fontes públicas. Em ambiente de
        produção não são criados registos fictícios de propriedades ou empresas após o enriquecimento.
        {isDevMode && (
          <span className="mt-1 block text-gray-400">
            Modo desenvolvimento: para permitir dados de demonstração (etiqueta MOCK_DEMO) no servidor,
            defina <code className="rounded bg-gray-100 px-1 text-[11px]">ENABLE_INVESTIGATION_ENRICH_DEMO_SEED=true</code> no{' '}
            <code className="rounded bg-gray-100 px-1 text-[11px]">.env</code> do backend (nunca em produção).
          </span>
        )}
      </p>

      <KpiCards
        propertiesFound={investigation.properties_found}
        leaseContractsFound={investigation.lease_contracts_found}
        companiesFound={investigation.companies_found}
        totalQueries={totalQueries}
        sourcesWithDataCount={summarySourcesWithDataCount}
        totalResults={totalResults}
      />

      <DossierSummary
        summaryCpfCnpj={summaryCpfCnpj}
        defaultCpfCnpj={defaultCpfCnpj}
        targetName={investigation.target_name}
        summarySources={summarySources}
        latestQuery={latestQuery}
        onApplyCpfCnpj={onApplyCpfCnpj}
        buildSummaryFields={buildSummaryFields}
      />

      {legalQueries && legalQueries.length > 0 && (
        <QueryCharts
          chartByProvider={chartByProvider}
          pieData={pieData}
          chartByDate={chartByDate}
        />
      )}

      {properties && properties.length > 0 && <PropertiesList properties={properties} />}

      {companies && companies.length > 0 && <CompaniesList companies={companies} />}

      {legalQueries && legalQueries.length > 0 && (
        <div className="rounded-xl border border-gray-100 bg-white shadow-sm">
          <div className="flex items-center gap-3 border-b border-gray-100 px-6 py-4">
            <div className="rounded-lg bg-indigo-500 p-2">
              <Scale className="h-4 w-4 text-white" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-gray-900">Histórico de Consultas</h2>
              <p className="text-xs text-gray-500">
                {legalQueries.length} consulta{legalQueries.length === 1 ? '' : 's'} realizada
                {legalQueries.length === 1 ? '' : 's'}
              </p>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">Provedor</th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">Tipo</th>
                  <th className="px-6 py-3 text-right text-xs font-medium uppercase text-gray-500">Resultados</th>
                  <th className="px-6 py-3 text-right text-xs font-medium uppercase text-gray-500">Data</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {legalQueries.slice(0, 20).map((query) => (
                  <tr key={query.id} className="transition hover:bg-gray-50/50">
                    <td className="px-6 py-3">
                      <span className="inline-flex items-center rounded-md bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700">
                        {query.provider}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-xs text-gray-700">{query.query_type}</td>
                    <td className="px-6 py-3 text-right text-xs font-medium text-gray-900">{query.result_count}</td>
                    <td className="px-6 py-3 text-right text-xs text-gray-500">{formatDateTime(query.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {(!properties || properties.length === 0) &&
        (!companies || companies.length === 0) &&
        (!legalQueries || legalQueries.length === 0) &&
        summarySourcesWithDataCount === 0 && (
          <div className="rounded-xl border border-gray-100 bg-white p-12 text-center shadow-sm">
            <Search className="mx-auto h-12 w-12 text-gray-300" />
            <h3 className="mt-4 text-base font-medium text-gray-900">Nenhum dado encontrado ainda</h3>
            <p className="mt-2 text-sm text-gray-500">
              Acesse a aba{' '}
              <button onClick={onOpenLegalTab} className="font-medium text-indigo-600 hover:underline">
                Consultas Legais
              </button>{' '}
              para pesquisar nas bases governamentais.
            </p>
          </div>
        )}
    </div>
  )
}
