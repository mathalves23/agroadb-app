import { Briefcase, Mail, Save, Shield, User } from 'lucide-react'

import type { ProfileData } from '@/pages/profile/types'

type Props = {
  onSave: () => void
  profile: ProfileData
  saving: boolean
  setProfile: (profile: ProfileData) => void
}

export function ProfileInfoTab({ onSave, profile, saving, setProfile }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-6">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900">
          <User className="h-5 w-5 text-indigo-600" />
          Informações Pessoais
        </h2>
        <p className="mt-1 text-sm text-gray-600">Atualize seus dados pessoais e profissionais</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">Nome Completo</label>
          <input
            type="text"
            value={profile.full_name}
            onChange={(event) => setProfile({ ...profile, full_name: event.target.value })}
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-transparent focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">Email</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              type="email"
              value={profile.email}
              onChange={(event) => setProfile({ ...profile, email: event.target.value })}
              className="w-full rounded-lg border border-gray-300 py-2.5 pl-10 pr-4 focus:border-transparent focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">Nome de Usuário</label>
          <input
            type="text"
            value={profile.username}
            onChange={(event) => setProfile({ ...profile, username: event.target.value })}
            className="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:border-transparent focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">Organização</label>
          <div className="relative">
            <Briefcase className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={profile.organization}
              onChange={(event) => setProfile({ ...profile, organization: event.target.value })}
              className="w-full rounded-lg border border-gray-300 py-2.5 pl-10 pr-4 focus:border-transparent focus:ring-2 focus:ring-indigo-500"
              placeholder="Ex: Escritório de Advocacia"
            />
          </div>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">Número OAB (opcional)</label>
          <div className="relative">
            <Shield className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={profile.oab_number}
              onChange={(event) => setProfile({ ...profile, oab_number: event.target.value })}
              className="w-full rounded-lg border border-gray-300 py-2.5 pl-10 pr-4 focus:border-transparent focus:ring-2 focus:ring-indigo-500"
              placeholder="Ex: OAB/SP 123456"
            />
          </div>
        </div>
      </div>

      <div className="mt-6 flex justify-end">
        <button
          onClick={onSave}
          disabled={saving}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:opacity-50"
        >
          <Save className="h-4 w-4" />
          {saving ? 'Salvando...' : 'Salvar Alterações'}
        </button>
      </div>
    </div>
  )
}
