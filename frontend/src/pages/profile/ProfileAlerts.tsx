import { AlertCircle, CheckCircle } from 'lucide-react'

type Props = {
  error: string
  saveSuccess: boolean
}

export function ProfileAlerts({ error, saveSuccess }: Props) {
  return (
    <>
      {saveSuccess && (
        <div className="mb-6 flex items-center gap-3 rounded-xl border border-green-200 bg-green-50 p-4">
          <CheckCircle className="h-5 w-5 text-green-600" />
          <p className="text-sm font-medium text-green-800">Alterações salvas com sucesso!</p>
        </div>
      )}

      {error && (
        <div className="mb-6 flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-4">
          <AlertCircle className="h-5 w-5 text-red-600" />
          <p className="text-sm font-medium text-red-800">{error}</p>
        </div>
      )}
    </>
  )
}
