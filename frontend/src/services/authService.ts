import { api } from '@/lib/axios'
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from '@/types/api'

export const authService = {
  async login(data: LoginRequest): Promise<TokenResponse> {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    
    const response = await api.post<TokenResponse>('/auth/login', formData, {
      headers: { 
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async register(data: RegisterRequest): Promise<User> {
    const response = await api.post<User>('/auth/register', data)
    return response.data
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },
}
