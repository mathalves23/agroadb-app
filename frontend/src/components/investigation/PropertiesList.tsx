import { memo } from 'react'
import { MapPin } from 'lucide-react'
import { formatCPFCNPJ, formatNumber } from '@/lib/utils'

interface Property {
  id: number
  property_name?: string
  data_source: string
  car_number?: string
  ccir_number?: string
  matricula?: string
  area_hectares?: number
  city?: string
  state?: string
  owner_name?: string
  owner_cpf_cnpj?: string
  address?: string
}

interface PropertiesListProps {
  properties: Property[]
}

export const PropertiesList = memo(function PropertiesList({ properties }: PropertiesListProps) {
  if (!properties || properties.length === 0) {
    return null
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100">
      <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-3">
        <div className="bg-emerald-500 rounded-lg p-2">
          <MapPin className="h-4 w-4 text-white" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-gray-900">Propriedades Rurais</h2>
          <p className="text-xs text-gray-500">{properties.length} imóve{properties.length === 1 ? 'l' : 'is'} encontrado{properties.length === 1 ? '' : 's'}</p>
        </div>
      </div>
      <div className="divide-y divide-gray-50">
        {properties.map((property) => (
          <div key={property.id} className="p-5 hover:bg-gray-50/50 transition">
            <div className="flex items-start justify-between">
              <h3 className="font-medium text-gray-900">
                {property.property_name || 'Propriedade sem nome'}
              </h3>
              <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-medium bg-gray-100 text-gray-600">
                {property.data_source}
              </span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
              {property.car_number && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 text-xs w-20 shrink-0">CAR</span>
                  <span className="font-mono text-xs text-gray-900">{property.car_number}</span>
                </div>
              )}
              {property.ccir_number && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 text-xs w-20 shrink-0">CCIR</span>
                  <span className="font-mono text-xs text-gray-900">{property.ccir_number}</span>
                </div>
              )}
              {property.matricula && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 text-xs w-20 shrink-0">Matrícula</span>
                  <span className="font-mono text-xs text-gray-900">{property.matricula}</span>
                </div>
              )}
              {property.area_hectares && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 text-xs w-20 shrink-0">Área</span>
                  <span className="text-xs font-medium text-gray-900">{formatNumber(property.area_hectares)} ha</span>
                </div>
              )}
              {property.city && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 text-xs w-20 shrink-0">Local</span>
                  <span className="text-xs text-gray-900">{property.city}/{property.state}</span>
                </div>
              )}
              {property.owner_name && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 text-xs w-20 shrink-0">Proprietário</span>
                  <span className="text-xs text-gray-900">{property.owner_name}</span>
                </div>
              )}
              {property.owner_cpf_cnpj && (
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 text-xs w-20 shrink-0">CPF/CNPJ</span>
                  <span className="font-mono text-xs text-gray-900">{formatCPFCNPJ(property.owner_cpf_cnpj)}</span>
                </div>
              )}
              {property.address && (
                <div className="flex items-center gap-2 col-span-2">
                  <span className="text-gray-400 text-xs w-20 shrink-0">Endereço</span>
                  <span className="text-xs text-gray-900">{property.address}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
})
