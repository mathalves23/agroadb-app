import { memo } from 'react'
import { Building2 } from 'lucide-react'
import { formatCPFCNPJ } from '@/lib/utils'

interface Company {
  id: number
  corporate_name?: string
  trade_name?: string
  cnpj: string
  status?: string
  city?: string
  state?: string
  address?: string
  main_activity?: string
}

interface CompaniesListProps {
  companies: Company[]
}

export const CompaniesList = memo(function CompaniesList({ companies }: CompaniesListProps) {
  if (!companies || companies.length === 0) {
    return null
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100">
      <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-3">
        <div className="bg-purple-500 rounded-lg p-2">
          <Building2 className="h-4 w-4 text-white" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-gray-900">Empresas Identificadas</h2>
          <p className="text-xs text-gray-500">{companies.length} empresa{companies.length === 1 ? '' : 's'} encontrada{companies.length === 1 ? '' : 's'}</p>
        </div>
      </div>
      <div className="divide-y divide-gray-50">
        {companies.map((company) => (
          <div key={company.id} className="p-5 hover:bg-gray-50/50 transition">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-medium text-gray-900">
                  {company.corporate_name || company.trade_name || 'Empresa'}
                </h3>
                {company.trade_name && company.corporate_name && (
                  <p className="text-xs text-gray-500 mt-0.5">{company.trade_name}</p>
                )}
              </div>
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-medium ${
                  company.status?.toLowerCase().includes('ativ')
                    ? 'bg-emerald-50 text-emerald-700'
                    : 'bg-red-50 text-red-700'
                }`}
              >
                {company.status || 'Desconhecido'}
              </span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-gray-400 text-xs w-20 shrink-0">CNPJ</span>
                <span className="font-mono text-xs text-gray-900">{formatCPFCNPJ(company.cnpj)}</span>
              </div>
              {company.city && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 text-xs w-20 shrink-0">Local</span>
                  <span className="text-xs text-gray-900">{company.city}/{company.state}</span>
                </div>
              )}
              {company.address && (
                <div className="flex items-center gap-2 col-span-2">
                  <span className="text-gray-400 text-xs w-20 shrink-0">Endereço</span>
                  <span className="text-xs text-gray-900">{company.address}</span>
                </div>
              )}
              {company.main_activity && (
                <div className="flex items-center gap-2 col-span-2">
                  <span className="text-gray-400 text-xs w-20 shrink-0">Atividade</span>
                  <span className="text-xs text-gray-900">{company.main_activity}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
})
