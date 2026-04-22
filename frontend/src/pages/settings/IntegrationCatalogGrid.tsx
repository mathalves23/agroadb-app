import { CheckCircle2, ExternalLink, Key, Shield, XCircle, Zap } from 'lucide-react'

import { categoryConfig, type IntegrationInfo } from '@/pages/settings/catalog'

type Props = {
  getStatus: (name: string) => 'active' | 'inactive' | 'partial'
  items: IntegrationInfo[]
}

export function IntegrationCatalogGrid({ getStatus, items }: Props) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((integration) => {
        const status = getStatus(integration.name)
        const category = categoryConfig[integration.category]

        return (
          <div key={integration.name} className="rounded-xl border border-gray-200/60 bg-white p-4 transition hover:shadow-sm">
            <div className="mb-2 flex items-start justify-between">
              <div className="flex items-center gap-2">
                {integration.category === 'free' && <Zap className="h-4 w-4 text-emerald-500" />}
                {integration.category === 'key' && <Key className="h-4 w-4 text-amber-500" />}
                {integration.category === 'conecta' && <Shield className="h-4 w-4 text-blue-500" />}
                <h3 className="text-sm font-semibold text-gray-900">{integration.name}</h3>
              </div>
              {status === 'active' ? (
                <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700">
                  <CheckCircle2 className="h-3 w-3" />
                  Ativa
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-[10px] font-semibold text-gray-500">
                  <XCircle className="h-3 w-3" />
                  Inativa
                </span>
              )}
            </div>

            <p className="mb-3 text-xs leading-relaxed text-gray-500">{integration.description}</p>

            {integration.envVars && (
              <div className="mb-3">
                <p className="mb-1 text-[10px] font-medium uppercase tracking-wider text-gray-400">Variáveis .env</p>
                <div className="flex flex-wrap gap-1">
                  {integration.envVars.map((envVar) => (
                    <code
                      key={envVar}
                      className="rounded border border-gray-100 bg-gray-50 px-1.5 py-0.5 text-[10px] text-gray-600"
                    >
                      {envVar}
                    </code>
                  ))}
                </div>
              </div>
            )}

            {integration.notes && <p className="mb-3 text-[10px] leading-relaxed text-gray-400">{integration.notes}</p>}

            <div className="flex items-center justify-between border-t border-gray-100 pt-2">
              <span className={`rounded-full bg-${category.color}-50 px-2 py-0.5 text-[10px] font-medium text-${category.color}-600`}>
                {category.label}
              </span>
              {integration.helpUrl && (
                <a
                  href={integration.helpUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[10px] text-gray-400 transition hover:text-emerald-600"
                >
                  <ExternalLink className="h-3 w-3" />
                  Documentação
                </a>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
