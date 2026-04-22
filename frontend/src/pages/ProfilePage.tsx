import { User } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { ProfileAlerts } from '@/pages/profile/ProfileAlerts'
import { ProfileInfoTab } from '@/pages/profile/ProfileInfoTab'
import { ProfileNotificationsTab } from '@/pages/profile/ProfileNotificationsTab'
import { ProfileSecurityTab } from '@/pages/profile/ProfileSecurityTab'
import { ProfileSidebar } from '@/pages/profile/ProfileSidebar'
import { useProfileSettings } from '@/pages/profile/useProfileSettings'

export default function ProfilePage() {
  const navigate = useNavigate()
  const {
    activeTab,
    error,
    handleChangePassword,
    handleSaveNotifications,
    handleSaveProfile,
    logout,
    notifications,
    passwordData,
    profile,
    saveSuccess,
    saving,
    setActiveTab,
    setNotifications,
    setPasswordData,
    setProfile,
    setShowPasswords,
    showPasswords,
  } = useProfileSettings()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => navigate(-1)} className="text-gray-600 hover:text-gray-900">
                ← Voltar
              </button>
              <div>
                <h1 className="flex items-center gap-3 text-2xl font-bold text-gray-900">
                  <User className="h-7 w-7 text-indigo-600" />
                  Meu Perfil
                </h1>
                <p className="mt-1 text-sm text-gray-600">
                  Gerencie suas informações pessoais e preferências
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
          <div className="lg:col-span-1">
            <ProfileSidebar
              activeTab={activeTab}
              onChangeTab={setActiveTab}
              onLogout={logout}
              profile={profile}
            />
          </div>

          <div className="lg:col-span-3">
            <ProfileAlerts error={error} saveSuccess={saveSuccess} />

            {activeTab === 'profile' && (
              <ProfileInfoTab
                onSave={handleSaveProfile}
                profile={profile}
                saving={saving}
                setProfile={setProfile}
              />
            )}

            {activeTab === 'security' && (
              <ProfileSecurityTab
                onSave={handleChangePassword}
                passwordData={passwordData}
                saving={saving}
                setPasswordData={setPasswordData}
                setShowPasswords={setShowPasswords}
                showPasswords={showPasswords}
              />
            )}

            {activeTab === 'notifications' && (
              <ProfileNotificationsTab
                notifications={notifications}
                onSave={handleSaveNotifications}
                saving={saving}
                setNotifications={setNotifications}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
