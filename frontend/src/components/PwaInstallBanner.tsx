import { Download, ShieldCheck, Smartphone, X } from 'lucide-react'
import { usePwaInstallPrompt } from '@/hooks/usePwaInstallPrompt'

export default function PwaInstallBanner() {
  const { canShowPrompt, install, dismiss } = usePwaInstallPrompt()

  if (!canShowPrompt) return null

  return (
    <aside className="mb-4 overflow-hidden rounded-2xl border border-emerald-200 bg-gradient-to-r from-emerald-600 via-emerald-500 to-lime-500 text-white shadow-lg">
      <div className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <div className="rounded-xl bg-white/15 p-2.5">
            <Smartphone className="h-5 w-5" />
          </div>
          <div>
            <p className="text-sm font-semibold">Instale o AgroADB como app</p>
            <p className="mt-1 max-w-2xl text-sm text-emerald-50/90">
              Abra mais rapido, mantenha o acesso ao manual e use o painel com experiencia mais
              proxima de app no desktop e no mobile.
            </p>
            <div className="mt-2 flex flex-wrap gap-2 text-xs text-emerald-50/90">
              <span className="inline-flex items-center gap-1 rounded-full bg-white/10 px-2 py-1">
                <Download className="h-3.5 w-3.5" />
                Acesso rapido
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-white/10 px-2 py-1">
                <ShieldCheck className="h-3.5 w-3.5" />
                Manual e atalhos disponiveis
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={dismiss}
            className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-3 py-2 text-sm font-medium text-white transition hover:bg-white/20"
          >
            <X className="h-4 w-4" />
            Agora nao
          </button>
          <button
            type="button"
            onClick={() => {
              void install()
            }}
            className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-50"
          >
            <Download className="h-4 w-4" />
            Instalar app
          </button>
        </div>
      </div>
    </aside>
  )
}
