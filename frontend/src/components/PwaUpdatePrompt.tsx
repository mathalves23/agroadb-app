import { RefreshCcw, X } from 'lucide-react'
import { NoticeBanner } from '@/components/feedback'
import { usePwaUpdatePrompt } from '@/hooks/usePwaUpdatePrompt'

export default function PwaUpdatePrompt() {
  const { visible, update, dismiss } = usePwaUpdatePrompt()

  if (!visible) return null

  return (
    <NoticeBanner
      title="Atualização pronta"
      description="Uma nova versão do AgroADB já está disponível. Atualize para aplicar melhorias de estabilidade, PWA e sincronização."
      tone="brand"
      role="alert"
      fullBleed
      className="p-4"
      actions={
        <>
          <button
            type="button"
            onClick={dismiss}
            className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 px-3 py-2 text-sm font-medium text-white transition hover:bg-white/20"
          >
            <X className="h-4 w-4" />
            Depois
          </button>
          <button
            type="button"
            onClick={() => {
              void update()
            }}
            className="inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-semibold text-sky-700 transition hover:bg-sky-50"
          >
            <RefreshCcw className="h-4 w-4" />
            Atualizar app
          </button>
        </>
      }
    />
  )
}
