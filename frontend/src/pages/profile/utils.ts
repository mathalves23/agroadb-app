import type { PasswordData, ProfileData } from '@/pages/profile/types'

export function getProfileInitials(profile: Pick<ProfileData, 'full_name'>): string {
  return profile.full_name
    .split(' ')
    .map((name) => name[0])
    .filter(Boolean)
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

export function validatePasswordChange(passwordData: PasswordData): string | null {
  if (passwordData.new_password !== passwordData.confirm_password) {
    return 'As senhas não coincidem'
  }

  if (passwordData.new_password.length < 6) {
    return 'A nova senha deve ter pelo menos 6 caracteres'
  }

  return null
}
