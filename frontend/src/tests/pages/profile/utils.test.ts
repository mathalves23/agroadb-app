import { getProfileInitials, validatePasswordChange } from '@/pages/profile/utils'

describe('profile utils', () => {
  it('builds initials from profile full name', () => {
    expect(getProfileInitials({ full_name: 'Maria de Araujo' })).toBe('MD')
  })

  it('rejects mismatched passwords', () => {
    expect(
      validatePasswordChange({
        current_password: '123456',
        new_password: 'abcdef',
        confirm_password: 'abcdeg',
      })
    ).toBe('As senhas não coincidem')
  })

  it('accepts valid password change payloads', () => {
    expect(
      validatePasswordChange({
        current_password: '123456',
        new_password: 'abcdef',
        confirm_password: 'abcdef',
      })
    ).toBeNull()
  })
})
