import { Link } from 'react-router-dom'
import { ArrowLeft, BookOpen } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import manualMarkdown from '@product/manual-do-utilizador.md?raw'

export default function UserGuidePage() {
  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-12">
      <div className="flex items-start gap-4">
        <Link
          to="/dashboard"
          className="flex items-center gap-2 text-gray-500 hover:text-gray-900 transition shrink-0 mt-1"
        >
          <ArrowLeft className="h-5 w-5" />
          <span className="text-sm">Voltar</span>
        </Link>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600">Ajuda</p>
          <p className="text-sm text-gray-500 mt-0.5 flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-emerald-600 shrink-0" aria-hidden />
            Documentação de produto (independente de <code className="text-xs bg-gray-100 px-1 rounded">docs/</code> técnica).
          </p>
        </div>
      </div>

      <article
        className="bg-white rounded-xl border border-gray-200/60 p-6 md:p-8 shadow-sm
          text-gray-800 text-sm leading-relaxed
          [&_h1]:text-xl [&_h1]:font-bold [&_h1]:text-gray-900 [&_h1]:mt-8 [&_h1]:mb-3 [&_h1]:first:mt-0
          [&_h2]:text-base [&_h2]:font-semibold [&_h2]:text-gray-900 [&_h2]:mt-8 [&_h2]:mb-2
          [&_h3]:text-sm [&_h3]:font-semibold [&_h3]:text-gray-800 [&_h3]:mt-4 [&_h3]:mb-2
          [&_hr]:my-8 [&_hr]:border-gray-200
          [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-1 [&_ol]:list-decimal [&_ol]:pl-5
          [&_strong]:text-gray-900 [&_code]:text-xs [&_code]:bg-gray-100 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded"
      >
        <ReactMarkdown>{manualMarkdown}</ReactMarkdown>
      </article>

      <p className="text-xs text-gray-400 text-center">
        Conteúdo em <code className="bg-gray-100 px-1 rounded">product/manual-do-utilizador.md</code> no repositório.
      </p>
    </div>
  )
}
