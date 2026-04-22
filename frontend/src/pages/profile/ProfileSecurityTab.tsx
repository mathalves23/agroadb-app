import { Eye, EyeOff, Lock, Save } from 'lucide-react'

import type { PasswordData, PasswordVisibility } from '@/pages/profile/types'

type Props = {
  onSave: () => void
  passwordData: PasswordData
  saving: boolean
  setPasswordData: (data: PasswordData) => void
  setShowPasswords: (value: PasswordVisibility) => void
  showPasswords: PasswordVisibility
}

export function ProfileSecurityTab({
  onSave,
  passwordData,
  saving,
  setPasswordData,
  setShowPasswords,
  showPasswords,
}: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-6">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900">
          <Lock className="h-5 w-5 text-indigo-600" />
          Segurança da Conta
        </h2>
        <p className="mt-1 text-sm text-gray-600">Altere sua senha e gerencie a segurança da conta</p>
      </div>

      <div className="space-y-4">
        {[
          {
            field: 'current_password' as const,
            iconKey: 'current' as const,
            label: 'Senha Atual',
          },
          {
            field: 'new_password' as const,
            iconKey: 'new' as const,
            label: 'Nova Senha',
          },
          {
            field: 'confirm_password' as const,
            iconKey: 'confirm' as const,
            label: 'Confirmar Nova Senha',
          },
        ].map((item) => (
          <div key={item.field}>
            <label className="mb-2 block text-sm font-medium text-gray-700">{item.label}</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                type={showPasswords[item.iconKey] ? 'text' : 'password'}
                value={passwordData[item.field]}
                onChange={(event) =>
                  setPasswordData({
                    ...passwordData,
                    [item.field]: event.target.value,
                  })
                }
                className="w-full rounded-lg border border-gray-300 py-2.5 pl-10 pr-10 focus:border-transparent focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="button"
                onClick={() =>
                  setShowPasswords({
                    ...showPasswords,
                    [item.iconKey]: !showPasswords[item.iconKey],
                  })
                }
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPasswords[item.iconKey] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {item.field === 'new_password' && <p className="mt-1 text-xs text-gray-500">Mínimo de 6 caracteres</p>}
          </div>
        ))}
      </div>

      <div className="mt-6 flex justify-end">
        <button
          onClick={onSave}
          disabled={saving || !passwordData.current_password || !passwordData.new_password}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:opacity-50"
        >
          <Save className="h-4 w-4" />
          {saving ? 'Alterando...' : 'Alterar Senha'}
        </button>
      </div>
    </div>
  )
}
