import { Bell, Camera, Lock, LogOut, User } from 'lucide-react'

import type { ProfileData, ProfileTab } from '@/pages/profile/types'
import { getProfileInitials } from '@/pages/profile/utils'

type Props = {
  activeTab: ProfileTab
  onChangeTab: (tab: ProfileTab) => void
  onLogout: () => void
  profile: ProfileData
}

const tabs: Array<{ id: ProfileTab; label: string; icon: typeof User }> = [
  { id: 'profile', label: 'Informações Pessoais', icon: User },
  { id: 'security', label: 'Segurança', icon: Lock },
  { id: 'notifications', label: 'Notificações', icon: Bell },
]

export function ProfileSidebar({ activeTab, onChangeTab, onLogout, profile }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="text-center">
        <div className="relative inline-block">
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-3xl font-bold text-white">
            {getProfileInitials(profile)}
          </div>
          <button className="absolute bottom-0 right-0 flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-white shadow-lg transition hover:bg-indigo-700">
            <Camera className="h-4 w-4" />
          </button>
        </div>

        <h3 className="mt-4 text-lg font-semibold text-gray-900">{profile.full_name}</h3>
        <p className="text-sm text-gray-600">{profile.email}</p>
        {profile.organization && <p className="mt-1 text-xs text-gray-500">{profile.organization}</p>}
      </div>

      <div className="mt-6 space-y-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onChangeTab(tab.id)}
            className={`flex w-full items-center gap-3 rounded-lg px-4 py-2.5 text-sm font-medium transition ${
              activeTab === tab.id ? 'bg-indigo-50 text-indigo-600' : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      <div className="mt-6 border-t border-gray-200 pt-6">
        <button
          onClick={onLogout}
          className="flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium text-red-600 transition hover:bg-red-50"
        >
          <LogOut className="h-4 w-4" />
          Sair da Conta
        </button>
      </div>
    </div>
  )
}
