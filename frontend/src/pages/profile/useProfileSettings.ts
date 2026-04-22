import { useEffect, useState } from 'react'

import { api } from '@/lib/axios'
import { useAuthStore } from '@/stores/authStore'
import type {
  NotificationSettings,
  PasswordData,
  PasswordVisibility,
  ProfileData,
  ProfileTab,
} from '@/pages/profile/types'
import { validatePasswordChange } from '@/pages/profile/utils'

const DEFAULT_NOTIFICATIONS: NotificationSettings = {
  email_investigations: true,
  email_reports: true,
  email_updates: false,
  email_marketing: false,
}

function createInitialProfile(user: ReturnType<typeof useAuthStore.getState>['user']): ProfileData {
  return {
    full_name: user?.full_name || '',
    email: user?.email || '',
    username: user?.username || '',
    organization: user?.organization || '',
    oab_number: user?.oab_number || '',
  }
}

export function useProfileSettings() {
  const { logout, user } = useAuthStore()
  const [activeTab, setActiveTab] = useState<ProfileTab>('profile')
  const [profile, setProfile] = useState<ProfileData>(() => createInitialProfile(user))
  const [passwordData, setPasswordData] = useState<PasswordData>({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [showPasswords, setShowPasswords] = useState<PasswordVisibility>({
    current: false,
    new: false,
    confirm: false,
  })
  const [notifications, setNotifications] = useState<NotificationSettings>(DEFAULT_NOTIFICATIONS)
  const [saving, setSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setProfile(createInitialProfile(user))
  }, [user])

  useEffect(() => {
    void loadProfile()
    void loadNotificationSettings()
  }, [])

  const setSuccessWithTimeout = () => {
    setSaveSuccess(true)
    window.setTimeout(() => setSaveSuccess(false), 3000)
  }

  const loadProfile = async () => {
    try {
      const response = await api.get('/users/me')
      const data = response.data as ProfileData
      setProfile({
        full_name: data.full_name,
        email: data.email,
        username: data.username,
        organization: data.organization || '',
        oab_number: data.oab_number || '',
      })
    } catch {
      // noop
    }
  }

  const loadNotificationSettings = async () => {
    try {
      const response = await api.get('/users/me/notifications')
      setNotifications(response.data as NotificationSettings)
    } catch {
      // noop
    }
  }

  const handleSaveProfile = async () => {
    setSaving(true)
    setError('')
    setSaveSuccess(false)

    try {
      await api.patch('/users/me', profile)
      setSuccessWithTimeout()
    } catch (requestError) {
      const detail =
        (requestError as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Erro ao salvar perfil'
      setError(detail)
    } finally {
      setSaving(false)
    }
  }

  const handleChangePassword = async () => {
    setError('')
    const validationError = validatePasswordChange(passwordData)
    if (validationError) {
      setError(validationError)
      return
    }

    setSaving(true)
    try {
      await api.post('/users/me/password', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      })
      setSuccessWithTimeout()
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      })
    } catch (requestError) {
      const detail =
        (requestError as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        'Erro ao alterar senha'
      setError(detail)
    } finally {
      setSaving(false)
    }
  }

  const handleSaveNotifications = async () => {
    setSaving(true)
    setError('')

    try {
      await api.put('/users/me/notifications', notifications)
      setSuccessWithTimeout()
    } catch {
      setError('Erro ao salvar preferências')
    } finally {
      setSaving(false)
    }
  }

  return {
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
  }
}
