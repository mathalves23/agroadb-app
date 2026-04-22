import { Shield } from 'lucide-react'
import type { Organization } from '@/services/organizationService'

type Props = {
  govHumanReview: boolean
  govMutationPending: boolean
  govMutationError: boolean
  govOrgId: number | null
  govRefUrl: string
  onChangeHumanReview: (value: boolean) => void
  onChangeOrg: (orgId: number) => void
  onChangeRefUrl: (value: string) => void
  onSave: () => void
  orgs: Organization[]
}

export function GovernanceSettingsCard({
  govHumanReview,
  govMutationPending,
  govMutationError,
  govOrgId,
  govRefUrl,
  onChangeHumanReview,
  onChangeOrg,
  onChangeRefUrl,
  onSave,
  orgs,
}: Props) {
  if (!orgs.length || govOrgId === null) {
    return null
  }

  return (
    <div className="rounded-xl border border-gray-200/60 bg-white p-6">
      <h2 className="mb-2 flex items-center gap-2 text-lg font-bold text-gray-900">
        <Shield className="h-5 w-5 text-indigo-600" />
        Governança de IA — score de risco
      </h2>
      <p className="mb-4 max-w-3xl text-xs leading-relaxed text-gray-500">
        Para transparência e defesa regulatória (LGPD / maturidade ANPD): exija revisão humana antes
        de decisões com base no score automatizado e associe a referência ao RIPD ou DPIA da
        organização.
      </p>
      {orgs.length > 1 && (
        <>
          <label className="mb-1 block text-xs font-medium text-gray-700">Organização</label>
          <select
            value={govOrgId}
            onChange={(event) => onChangeOrg(Number(event.target.value))}
            className="mb-4 w-full max-w-md rounded-lg border border-gray-300 px-3 py-2 text-sm"
          >
            {orgs.map((org) => (
              <option key={org.id} value={org.id}>
                {org.name}
              </option>
            ))}
          </select>
        </>
      )}
      <label className="mb-3 flex cursor-pointer items-center gap-2 text-sm text-gray-800">
        <input
          type="checkbox"
          checked={govHumanReview}
          onChange={(event) => onChangeHumanReview(event.target.checked)}
          className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
        Revisão humana obrigatória para uso decisório do score
      </label>
      <label className="mb-1 block text-xs font-medium text-gray-700">
        Referência (URL ou texto) — RIPD / DPIA / registo interno
      </label>
      <input
        type="url"
        value={govRefUrl}
        onChange={(event) => onChangeRefUrl(event.target.value)}
        placeholder="https://…"
        className="mb-3 w-full max-w-2xl rounded-lg border border-gray-300 px-3 py-2 text-sm"
      />
      <button
        type="button"
        disabled={govMutationPending}
        onClick={onSave}
        className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {govMutationPending ? 'A guardar…' : 'Guardar política'}
      </button>
      {govMutationError && (
        <p className="mt-2 text-xs text-red-600">
          Não foi possível guardar. Verifique se tem papel admin na organização.
        </p>
      )}
    </div>
  )
}
