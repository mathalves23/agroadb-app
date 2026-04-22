import { Bell, Save } from 'lucide-react'

import type { NotificationSettings } from '@/pages/profile/types'

type Props = {
  notifications: NotificationSettings
  onSave: () => void
  saving: boolean
  setNotifications: (settings: NotificationSettings) => void
}

const options: Array<{
  key: keyof NotificationSettings
  title: string
  description: string
}> = [
  {
    key: 'email_investigations',
    title: 'Atualizações de Investigações',
    description: 'Receba emails sobre novas atividades em suas investigações',
  },
  {
    key: 'email_reports',
    title: 'Relatórios Gerados',
    description: 'Notificações quando relatórios ficarem prontos',
  },
  {
    key: 'email_updates',
    title: 'Atualizações do Sistema',
    description: 'Novidades, atualizações e melhorias da plataforma',
  },
  {
    key: 'email_marketing',
    title: 'Dicas e Conteúdo Educacional',
    description: 'Tutoriais, dicas de uso e melhores práticas',
  },
]

export function ProfileNotificationsTab({
  notifications,
  onSave,
  saving,
  setNotifications,
}: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-6">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900">
          <Bell className="h-5 w-5 text-indigo-600" />
          Preferências de Notificações
        </h2>
        <p className="mt-1 text-sm text-gray-600">Escolha como e quando deseja receber notificações</p>
      </div>

      <div className="space-y-4">
        {options.map((option) => (
          <div
            key={option.key}
            className="flex items-center justify-between rounded-lg border border-gray-200 p-4 transition hover:bg-gray-50"
          >
            <div>
              <h3 className="text-sm font-medium text-gray-900">{option.title}</h3>
              <p className="mt-1 text-xs text-gray-600">{option.description}</p>
            </div>
            <label className="relative inline-flex cursor-pointer items-center">
              <input
                type="checkbox"
                checked={notifications[option.key]}
                onChange={(event) =>
                  setNotifications({
                    ...notifications,
                    [option.key]: event.target.checked,
                  })
                }
                className="peer sr-only"
              />
              <div className="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-indigo-600 peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300" />
            </label>
          </div>
        ))}
      </div>

      <div className="mt-6 flex justify-end">
        <button
          onClick={onSave}
          disabled={saving}
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:opacity-50"
        >
          <Save className="h-4 w-4" />
          {saving ? 'Salvando...' : 'Salvar Preferências'}
        </button>
      </div>
    </div>
  )
}
