import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Database, XCircle } from 'lucide-react'
import { legalService, type IntegrationStatus } from '@/services/legalService'

type LegalQueriesTabProps = {
  investigationId: string | undefined
  defaultCpfCnpj: string
  onApplyCpfCnpj?: () => void
  onError?: (message: string) => void
  onDataJudResult?: (data: Record<string, unknown> | null) => void
  onSigefResult?: (data: Record<string, unknown> | null) => void
}

export function LegalQueriesTab({
  investigationId,
  defaultCpfCnpj,
  onApplyCpfCnpj,
  onError,
  onDataJudResult,
  onSigefResult,
}: LegalQueriesTabProps) {
  const [dataJudPath, setDataJudPath] = useState('/api_publica_trf1/_search')
  const [dataJudPayload, setDataJudPayload] = useState(
    JSON.stringify({ query: { match: { numeroProcesso: '' } } }, null, 2)
  )
  const [dataJudResult, setDataJudResult] = useState<Record<string, unknown> | null>(null)
  const [sigefCpfCnpj, setSigefCpfCnpj] = useState('')
  const [sigefCodigoImovel, setSigefCodigoImovel] = useState('')
  const [sigefPagina, setSigefPagina] = useState(1)
  const [sigefResult, setSigefResult] = useState<Record<string, unknown> | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const { data: integrationStatus } = useQuery({
    queryKey: ['integrationStatus'],
    queryFn: () => legalService.getIntegrationStatus(),
  })
  const status = integrationStatus as IntegrationStatus | undefined
  const dataJudConfigured = status?.datajud?.configured ?? false
  const sigefConfigured = status?.sigef_parcelas?.configured ?? false
  const credentialsMissing = !dataJudConfigured || !sigefConfigured

  const setError = (msg: string) => {
    setErrorMessage(msg)
    onError?.(msg)
  }

  const dataJudMutation = useMutation({
    mutationFn: (payload: { path: string; payload: Record<string, unknown> }) =>
      legalService.datajudProxy({
        path: payload.path,
        method: 'POST',
        payload: payload.payload,
        investigation_id: investigationId ? Number(investigationId) : undefined,
      }),
    onSuccess: (data) => {
      const raw = data && typeof data === 'object' && 'data' in data ? (data as { data: unknown }).data : data
      const result = (raw as Record<string, unknown>) ?? null
      setDataJudResult(result)
      onDataJudResult?.(result)
      setErrorMessage(null)
    },
    onError: (error: { response?: { data?: { detail?: unknown } }; message?: string }) => {
      const detail = error?.response?.data?.detail
      const msg =
        typeof detail === 'object' && detail !== null && 'detail' in detail
          ? String((detail as { detail: string }).detail)
          : typeof detail === 'string'
            ? detail
            : error?.message || 'Erro ao consultar DataJud'
      setError(msg)
    },
  })

  const sigefMutation = useMutation({
    mutationFn: (params: Record<string, unknown>) =>
      legalService.sigefParcelas({
        ...params,
        investigation_id: investigationId ? Number(investigationId) : undefined,
      }),
    onSuccess: (data) => {
      const raw = data && typeof data === 'object' && 'data' in data ? (data as { data: unknown }).data : data
      const result = (raw as Record<string, unknown>) ?? null
      setSigefResult(result)
      onSigefResult?.(result)
      setErrorMessage(null)
    },
    onError: (error: { response?: { data?: { detail?: unknown } }; message?: string }) => {
      const detail = error?.response?.data?.detail
      const msg =
        typeof detail === 'object' && detail !== null && 'detail' in detail
          ? String((detail as { detail: string }).detail)
          : typeof detail === 'string'
            ? detail
            : error?.message || 'Erro ao consultar SIGEF'
      setError(msg)
    },
  })

  return (
    <div className="space-y-6">
      {/* Estado: credenciais ausentes */}
      {credentialsMissing && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
          <div className="bg-amber-100 rounded-lg p-1.5 shrink-0 mt-0.5">
            <Database className="h-4 w-4 text-amber-600" />
          </div>
          <div>
            <p className="text-sm font-semibold text-amber-800">Credenciais ausentes</p>
            <p className="mt-1 text-xs text-amber-700">
              Para usar DataJud e SIGEF Parcelas, configure as variáveis no <code className="bg-amber-100 px-1 rounded">.env</code> do backend:
            </p>
            <ul className="mt-2 text-xs text-amber-700 list-disc list-inside space-y-0.5">
              {!dataJudConfigured && (
                <li><code>DATAJUD_API_URL</code> e <code>DATAJUD_API_KEY</code> (DataJud/CNJ)</li>
              )}
              {!sigefConfigured && (
                <li><code>SIGEF_PARCELAS_API_URL</code> (SIGEF Parcelas)</li>
              )}
            </ul>
            <p className="mt-2 text-xs text-amber-600">
              Após configurar, reinicie o backend. Para Conecta (SNCR/SIGEF/SICAR), use <code>CONECTA_*_CLIENT_ID</code>, <code>CONECTA_*_CLIENT_SECRET</code> ou <code>CONECTA_*_API_KEY</code>.
            </p>
          </div>
        </div>
      )}

      {errorMessage && (
        <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-xl p-3">
          <XCircle className="h-4 w-4 text-red-500 shrink-0" />
          <p className="text-xs text-red-700">{errorMessage}</p>
          <button
            onClick={() => { setErrorMessage(null) }}
            className="ml-auto text-red-400 hover:text-red-600 text-xs font-medium"
          >
            Fechar
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Seção DataJud */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900">Consulta DataJud</h2>
          <p className="text-sm text-gray-500 mt-1">
            Busque processos pelo número CNJ (path e payload da API pública DataJud).
          </p>
          <div className="mt-4 space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">Path</label>
              <input
                value={dataJudPath}
                onChange={(e) => setDataJudPath(e.target.value)}
                className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                placeholder="/api_publica_trf1/_search"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Payload (JSON)</label>
              <textarea
                value={dataJudPayload}
                onChange={(e) => setDataJudPayload(e.target.value)}
                rows={6}
                className="mt-1 w-full rounded-md border-gray-300 shadow-sm font-mono text-xs"
              />
            </div>
            <button
              onClick={() => {
                if (!dataJudConfigured) {
                  setError('DataJud não configurado. Configure DATAJUD_API_URL e DATAJUD_API_KEY no .env.')
                  return
                }
                try {
                  const parsed = JSON.parse(dataJudPayload) as Record<string, unknown>
                  dataJudMutation.mutate({ path: dataJudPath, payload: parsed })
                } catch {
                  setError('Payload JSON inválido')
                }
              }}
              disabled={dataJudMutation.isPending || !dataJudConfigured}
              className={`px-4 py-2 rounded-md text-sm text-white ${
                dataJudMutation.isPending || !dataJudConfigured
                  ? 'bg-green-300 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {dataJudMutation.isPending ? 'Consultando...' : 'Consultar'}
            </button>
          </div>
          {dataJudResult && (
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-700">Resultado</h3>
              <pre className="mt-2 text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                {JSON.stringify(dataJudResult, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Seção SIGEF Parcelas */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900">Consulta SIGEF (Parcelas)</h2>
          <p className="text-sm text-gray-500 mt-1">
            Parcelas por CPF/CNPJ ou código do imóvel (web service configurado).
          </p>
          <div className="mt-4 space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">CPF/CNPJ</label>
              <input
                value={sigefCpfCnpj || defaultCpfCnpj}
                onChange={(e) => setSigefCpfCnpj(e.target.value)}
                className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                placeholder="00000000000"
              />
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700">Código imóvel</label>
                <input
                  value={sigefCodigoImovel}
                  onChange={(e) => setSigefCodigoImovel(e.target.value)}
                  className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                  placeholder="Código do imóvel"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Página</label>
                <input
                  type="number"
                  min={1}
                  value={sigefPagina}
                  onChange={(e) => setSigefPagina(Number(e.target.value) || 1)}
                  className="mt-1 w-full rounded-md border-gray-300 shadow-sm"
                />
              </div>
            </div>
            {defaultCpfCnpj && (
              <button
                type="button"
                onClick={onApplyCpfCnpj}
                className="text-xs text-indigo-600 hover:underline"
              >
                Usar CPF/CNPJ da investigação
              </button>
            )}
            <button
              onClick={() => {
                if (!sigefConfigured) {
                  setError('SIGEF_PARCELAS_API_URL não configurada no .env.')
                  return
                }
                sigefMutation.mutate({
                  cpf: sigefCpfCnpj || defaultCpfCnpj || undefined,
                  cnpj: sigefCpfCnpj || defaultCpfCnpj || undefined,
                  codigo_imovel: sigefCodigoImovel || undefined,
                  pagina: sigefPagina,
                })
              }}
              disabled={sigefMutation.isPending || !sigefConfigured}
              className={`px-4 py-2 rounded-md text-sm text-white ${
                sigefMutation.isPending || !sigefConfigured
                  ? 'bg-green-300 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {sigefMutation.isPending ? 'Consultando...' : 'Consultar'}
            </button>
          </div>
          {sigefResult && (
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-700">Resultado</h3>
              <pre className="mt-2 text-xs bg-gray-50 p-3 rounded-lg overflow-auto max-h-64">
                {JSON.stringify(sigefResult, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
