import { Database } from 'lucide-react'

import { categoryConfig } from '@/pages/settings/catalog'
import type { IntegrationInfo } from '@/pages/settings/catalog'

type Props = {
  counts: { all: number; free: number; key: number; conecta: number }
  getStatus: (name: string) => 'active' | 'inactive' | 'partial'
  items: IntegrationInfo[]
}

export function IntegrationCategoryStats({ counts, getStatus, items }: Props) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-4">
      {(Object.entries(categoryConfig) as [keyof typeof categoryConfig, (typeof categoryConfig)['free']][]).map(
        ([key, config]) => {
          const Icon = config.icon
          const count = counts[key]
          const activeCount = items.filter((item) => item.category === key).filter((item) => getStatus(item.name) === 'active').length
          return (
            <div key={key} className="rounded-xl border border-gray-200/60 bg-white p-4">
              <div className="flex items-center gap-3">
                <div className={`rounded-lg bg-${config.color}-50 p-2`}>
                  <Icon className={`h-5 w-5 text-${config.color}-600`} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900">{config.label}</p>
                  <p className="text-xs text-gray-500">
                    {activeCount}/{count} ativas
                  </p>
                </div>
              </div>
            </div>
          )
        }
      )}
      <div className="rounded-xl border border-gray-200/60 bg-white p-4">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-gray-50 p-2">
            <Database className="h-5 w-5 text-gray-600" />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900">Total</p>
            <p className="text-xs text-gray-500">
              {items.filter((item) => getStatus(item.name) === 'active').length}/{items.length} ativas
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
