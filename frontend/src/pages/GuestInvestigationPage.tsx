import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { AlertCircle, Download, FileText, Loader2, Shield } from 'lucide-react'
import { investigationService } from '@/services/investigationService'
import type { Investigation } from '@/types/api'

type LegalQuerySummary = {
  id: number
  provider?: string
  query_type?: string
  result_count?: number
  created_at?: string | null
}

type GuestPayload = {
  guest: boolean
  allow_downloads: boolean
  guest_link_id: number
  label?: string | null
  expires_at?: string | null
  investigation: Investigation
  legal_queries: LegalQuerySummary[]
}

export default function GuestInvestigationPage() {
  const [searchParams] = useSearchParams()
  const token = useMemo(() => searchParams.get('t')?.trim() || '', [searchParams])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<GuestPayload | null>(null)
  const [pdfLoading, setPdfLoading] = useState(false)

  useEffect(() => {
    if (!token || token.length < 16) {
      setLoading(false)
      setError('Link inválido ou incompleto. Confirme o URL completo enviado pelo responsável.')
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    investigationService
      .getGuestInvestigation(token)
      .then((body) => {
        if (!cancelled) setData(body as GuestPayload)
      })
      .catch((err: { response?: { status?: number; data?: { detail?: string } } }) => {
        if (cancelled) return
        const status = err.response?.status
        const detail = err.response?.data?.detail
        if (status === 404) {
          setError(typeof detail === 'string' ? detail : 'Link inválido ou expirado.')
        } else {
          setError(typeof detail === 'string' ? detail : 'Não foi possível carregar a investigação.')
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [token])

  const handlePdf = async () => {
    if (!token || !data?.allow_downloads) return
    setPdfLoading(true)
    try {
      const blob = await investigationService.exportGuestInvestigationPdf(token)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `investigacao_${data.investigation.id}_convidado.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      setError('Não foi possível descarregar o PDF. O link pode não permitir exportações.')
    } finally {
      setPdfLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center gap-3 px-4 py-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-600 text-white">
            <Shield className="h-5 w-5" aria-hidden />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-slate-900">AgroADB</h1>
            <p className="text-xs text-slate-500">Visualização segura para convidado (só leitura)</p>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-8">
        {loading && (
          <div className="flex flex-col items-center justify-center gap-3 py-20 text-slate-600">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-600" aria-hidden />
            <p className="text-sm">A carregar dados da investigação…</p>
          </div>
        )}

        {!loading && error && (
          <div
            className="flex gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900"
            role="alert"
          >
            <AlertCircle className="h-5 w-5 shrink-0" aria-hidden />
            <div>
              <p className="font-medium">Não foi possível mostrar o conteúdo</p>
              <p className="mt-1 text-sm text-amber-800">{error}</p>
            </div>
          </div>
        )}

        {!loading && !error && data && (
          <div className="space-y-6">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Investigação
                  </p>
                  <h2 className="mt-1 text-2xl font-bold text-slate-900">{data.investigation.target_name}</h2>
                  {data.label ? (
                    <p className="mt-1 text-sm text-slate-600">
                      Ref. do link: <span className="font-medium">{data.label}</span>
                    </p>
                  ) : null}
                </div>
                <div className="flex flex-col items-end gap-2 text-right text-xs text-slate-600">
                  {data.expires_at ? (
                    <span>
                      Expira em{' '}
                      <time dateTime={data.expires_at}>{new Date(data.expires_at).toLocaleString()}</time>
                    </span>
                  ) : (
                    <span>Sem data de expiração definida</span>
                  )}
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-700">
                    Estado: {data.investigation.status}
                  </span>
                </div>
              </div>

              <dl className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
                <div className="rounded-lg bg-slate-50 p-3">
                  <dt className="text-xs text-slate-500">Imóveis</dt>
                  <dd className="text-lg font-semibold">{data.investigation.properties_found}</dd>
                </div>
                <div className="rounded-lg bg-slate-50 p-3">
                  <dt className="text-xs text-slate-500">Contratos</dt>
                  <dd className="text-lg font-semibold">{data.investigation.lease_contracts_found}</dd>
                </div>
                <div className="rounded-lg bg-slate-50 p-3">
                  <dt className="text-xs text-slate-500">Empresas</dt>
                  <dd className="text-lg font-semibold">{data.investigation.companies_found}</dd>
                </div>
                <div className="rounded-lg bg-slate-50 p-3">
                  <dt className="text-xs text-slate-500">Prioridade</dt>
                  <dd className="text-lg font-semibold">{data.investigation.priority}</dd>
                </div>
              </dl>

              {data.investigation.target_description ? (
                <p className="mt-4 text-sm leading-relaxed text-slate-700">
                  {data.investigation.target_description}
                </p>
              ) : null}

              <div className="mt-6 flex flex-wrap gap-3 border-t border-slate-100 pt-6">
                {data.allow_downloads ? (
                  <button
                    type="button"
                    onClick={() => void handlePdf()}
                    disabled={pdfLoading}
                    className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
                  >
                    {pdfLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                    ) : (
                      <Download className="h-4 w-4" aria-hidden />
                    )}
                    Descarregar PDF
                  </button>
                ) : (
                  <p className="flex items-center gap-2 text-sm text-slate-600">
                    <FileText className="h-4 w-4 shrink-0 text-slate-400" aria-hidden />
                    Este link não permite exportação de PDF. Peça um link com downloads ou acesso
                    registado na plataforma.
                  </p>
                )}
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-sm font-semibold text-slate-900">Consultas legais (resumo)</h3>
              <p className="mt-1 text-xs text-slate-500">
                Apenas metadados — o detalhe das respostas não é exposto nesta vista pública.
              </p>
              {data.legal_queries.length === 0 ? (
                <p className="mt-4 text-sm text-slate-600">Nenhuma consulta registada.</p>
              ) : (
                <div className="mt-4 overflow-x-auto">
                  <table className="w-full min-w-[480px] text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-xs text-slate-500">
                        <th className="py-2 pr-4 font-medium">ID</th>
                        <th className="py-2 pr-4 font-medium">Fornecedor</th>
                        <th className="py-2 pr-4 font-medium">Tipo</th>
                        <th className="py-2 pr-4 font-medium">Resultados</th>
                        <th className="py-2 font-medium">Criada</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.legal_queries.map((q) => (
                        <tr key={q.id} className="border-b border-slate-100 last:border-0">
                          <td className="py-2 pr-4 font-mono text-xs">{q.id}</td>
                          <td className="py-2 pr-4">{q.provider ?? '—'}</td>
                          <td className="py-2 pr-4">{q.query_type ?? '—'}</td>
                          <td className="py-2 pr-4">{q.result_count ?? '—'}</td>
                          <td className="py-2 text-slate-600">
                            {q.created_at ? new Date(q.created_at).toLocaleString() : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
