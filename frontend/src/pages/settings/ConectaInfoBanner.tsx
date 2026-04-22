import { Info } from 'lucide-react'

export function ConectaInfoBanner() {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-blue-200 bg-blue-50 p-4">
      <Info className="mt-0.5 h-5 w-5 shrink-0 text-blue-600" />
      <div className="text-sm">
        <p className="mb-1 font-medium text-blue-900">APIs Conecta gov.br</p>
        <p className="text-blue-700">
          As APIs do Conecta são restritas a <strong>órgãos públicos federais e estaduais</strong>. Para solicitar
          acesso, acesse{' '}
          <a href="https://www.gov.br/conecta/catalogo/" target="_blank" rel="noopener noreferrer" className="font-medium underline">
            gov.br/conecta/catalogo
          </a>
          . Após aprovação, configure as credenciais (<code className="rounded bg-blue-100 px-1">CLIENT_ID</code> e{' '}
          <code className="rounded bg-blue-100 px-1">CLIENT_SECRET</code>) no arquivo <code className="rounded bg-blue-100 px-1">.env</code> do backend.
        </p>
      </div>
    </div>
  )
}
