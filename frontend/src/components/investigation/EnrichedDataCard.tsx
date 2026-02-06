import { FileText } from 'lucide-react'

interface EnrichedDataCardProps {
  targetDescription: string | undefined
}

export function EnrichedDataCard({ targetDescription }: EnrichedDataCardProps) {
  if (!targetDescription || !targetDescription.includes('Receita Federal')) {
    return null
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <div className="flex items-center gap-2 mb-3">
        <div className="bg-emerald-50 rounded-lg p-1.5">
          <FileText className="h-4 w-4 text-emerald-600" />
        </div>
        <h3 className="text-sm font-semibold text-gray-900">Dados Cadastrais</h3>
        <span className="text-[10px] bg-emerald-50 text-emerald-600 px-2 py-0.5 rounded-full font-medium">Enriquecido</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {targetDescription.split('\n').filter(line => line.trim() && !line.startsWith('---')).map((line, i) => {
          // Parse "Receita Federal: Situação: REGULAR | Nascimento: 01/01/1990 | ..."
          if (line.includes(':') && line.includes('|')) {
            const parts = line.split('|').map(p => p.trim())
            return parts.map((part, j) => {
              const [label, ...valueParts] = part.replace(/^Receita Federal:\s*/, '').split(':')
              const value = valueParts.join(':').trim()
              if (!label || !value) return null
              return (
                <div key={`${i}-${j}`} className="bg-gray-50 rounded-lg px-3 py-2.5 border border-gray-100">
                  <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wider">{label.trim()}</p>
                  <p className="text-sm font-medium text-gray-900 mt-0.5 break-words">{value}</p>
                </div>
              )
            })
          }
          // Linha simples (ex: "Fonte: BrasilAPI")
          if (line.includes(':')) {
            const [label, ...valueParts] = line.split(':')
            const value = valueParts.join(':').trim()
            if (label && value) {
              return (
                <div key={i} className="bg-gray-50 rounded-lg px-3 py-2.5 border border-gray-100">
                  <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wider">{label.trim()}</p>
                  <p className="text-sm font-medium text-gray-900 mt-0.5 break-words">{value}</p>
                </div>
              )
            }
          }
          return null
        })}
      </div>
    </div>
  )
}
