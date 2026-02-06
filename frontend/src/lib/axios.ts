import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
})

// Request interceptor — adiciona token de autenticação
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor — trata 401 com cuidado
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status

    // Só faz logout em 401 se NÃO for uma requisição de login/registro
    if (status === 401) {
      const url = error.config?.url || ''
      const isAuthEndpoint = url.includes('/auth/login') || url.includes('/auth/register')

      if (!isAuthEndpoint) {
        const currentPath = window.location.pathname
        // Evita loop de redirecionamento
        if (currentPath !== '/login') {
          useAuthStore.getState().logout()
          window.location.href = '/login'
        }
      }
    }

    return Promise.reject(error)
  }
)
