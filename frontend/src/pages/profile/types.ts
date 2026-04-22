export type ProfileTab = 'profile' | 'security' | 'notifications'

export interface ProfileData {
  full_name: string
  email: string
  username: string
  organization?: string
  oab_number?: string
}

export interface NotificationSettings {
  email_investigations: boolean
  email_reports: boolean
  email_updates: boolean
  email_marketing: boolean
}

export interface PasswordData {
  current_password: string
  new_password: string
  confirm_password: string
}

export interface PasswordVisibility {
  current: boolean
  new: boolean
  confirm: boolean
}
