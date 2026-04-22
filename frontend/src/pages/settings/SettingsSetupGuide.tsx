import { Globe } from 'lucide-react'

export function SettingsSetupGuide() {
  return (
    <div className="rounded-xl border border-gray-200/60 bg-white p-6">
      <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-gray-900">
        <Globe className="h-5 w-5 text-emerald-600" />
        Como configurar
      </h2>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-50 text-xs font-bold text-emerald-700">1</div>
            <h3 className="text-sm font-semibold text-gray-900">APIs Gratuitas</h3>
          </div>
          <p className="text-xs leading-relaxed text-gray-500">
            Já estão funcionando automaticamente. BrasilAPI, IBGE, BCB, Receita Federal (CPF/CNPJ), BNMP, SEEU, TJMG e outras
            não precisam de nenhuma configuração.
          </p>
        </div>
        <div>
          <div className="mb-2 flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-amber-50 text-xs font-bold text-amber-700">2</div>
            <h3 className="text-sm font-semibold text-gray-900">APIs com Chave</h3>
          </div>
          <p className="text-xs leading-relaxed text-gray-500">
            Registre-se gratuitamente nos portais (Portal da Transparência, DataJud), obtenha sua API Key, e configure no arquivo{' '}
            <code className="rounded bg-gray-100 px-1 text-[10px]">backend/.env</code>. Reinicie o backend após alterar.
          </p>
        </div>
        <div>
          <div className="mb-2 flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-50 text-xs font-bold text-blue-700">3</div>
            <h3 className="text-sm font-semibold text-gray-900">Conecta gov.br</h3>
          </div>
          <p className="text-xs leading-relaxed text-gray-500">
            Solicite acesso como órgão público em{' '}
            <a href="https://www.gov.br/conecta/catalogo/" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
              gov.br/conecta
            </a>
            . Após aprovação, configure <code className="rounded bg-gray-100 px-1 text-[10px]">CLIENT_ID</code> e{' '}
            <code className="rounded bg-gray-100 px-1 text-[10px]">CLIENT_SECRET</code> no <code className="rounded bg-gray-100 px-1 text-[10px]">.env</code>.
          </p>
        </div>
      </div>
    </div>
  )
}
