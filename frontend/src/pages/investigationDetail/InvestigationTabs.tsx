import { Brain, Database, Network as NetworkIcon, Scale, Users } from 'lucide-react'

export type InvestigationDetailTab = 'summary' | 'legal' | 'network' | 'ml' | 'collaboration'

type Props = {
  activeTab: InvestigationDetailTab
  onChange: (tab: InvestigationDetailTab) => void
}

const tabs: Array<{
  id: InvestigationDetailTab
  label: string
  icon: typeof Database
}> = [
  { id: 'summary', label: 'Resumo', icon: Database },
  { id: 'legal', label: 'Consultas Legais', icon: Scale },
  { id: 'network', label: 'Rede', icon: NetworkIcon },
  { id: 'ml', label: 'Análise ML', icon: Brain },
  { id: 'collaboration', label: 'Colaboração', icon: Users },
]

export function InvestigationTabs({ activeTab, onChange }: Props) {
  return (
    <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-xl w-fit" role="tablist" aria-label="Secoes da investigacao">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          role="tab"
          aria-selected={activeTab === tab.id}
          onClick={() => onChange(tab.id)}
          className={`px-5 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === tab.id
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          <span className="flex items-center gap-2">
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </span>
        </button>
      ))}
    </div>
  )
}
