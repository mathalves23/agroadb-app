import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Shield, Loader2, AlertTriangle, Eye, EyeOff } from 'lucide-react'
import { authService } from '@/services/authService'
import { api } from '@/lib/axios'
import { useAuthStore } from '@/stores/authStore'

const loginSchema = z.object({
  username: z.string().min(3, 'Usuário ou email deve ter no mínimo 3 caracteres'),
  password: z.string().min(3, 'Senha deve ter no mínimo 3 caracteres'),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function LoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    try {
      setIsLoading(true)
      setError('')
      const tokens = await authService.login(data)
      api.defaults.headers.Authorization = `Bearer ${tokens.access_token}`
      const user = await authService.getMe()
      setAuth({ ...tokens, user })
      navigate('/dashboard')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      setError(axiosErr?.response?.data?.detail || (err instanceof Error ? err.message : 'Erro ao fazer login'))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-emerald-700 via-emerald-800 to-emerald-900 flex-col justify-between p-12">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 backdrop-blur rounded-xl flex items-center justify-center">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">AgroADB</span>
          </div>
        </div>
        <div>
          <h2 className="text-3xl font-bold text-white leading-tight">
            Inteligência Patrimonial<br />
            <span className="text-emerald-400">para o Agronegócio</span>
          </h2>
          <p className="mt-4 text-emerald-100/80 text-sm leading-relaxed max-w-md">
            Acesse dados de 27+ bases governamentais em uma única plataforma.
            SNCR, SIGEF, SICAR, DataJud, Receita Federal, BNMP e muito mais.
          </p>
          <div className="mt-8 flex items-center gap-6">
            {['SNCR', 'SIGEF', 'SICAR', 'DataJud', 'CNPJ'].map((name) => (
              <span key={name} className="text-[10px] font-medium text-emerald-300/60 uppercase tracking-wider">
                {name}
              </span>
            ))}
          </div>
        </div>
        <p className="text-xs text-emerald-200/40">&copy; {new Date().getFullYear()} AgroADB — Todos os direitos reservados</p>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-emerald-600 rounded-xl flex items-center justify-center shadow-sm">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">AgroADB</span>
          </div>

          <h1 className="text-2xl font-bold text-gray-900">Entrar</h1>
          <p className="mt-1 text-sm text-gray-500">Acesse sua conta para continuar</p>

          <form className="mt-8 space-y-5" onSubmit={handleSubmit(onSubmit)} role="form" aria-label="Formulário de login">
            {error && (
              <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-xl p-3" aria-live="polite">
                <AlertTriangle className="h-4 w-4 text-red-500 shrink-0" />
                <p className="text-xs text-red-700">{error}</p>
              </div>
            )}

            <div>
              <label htmlFor="username" className="block text-xs font-medium text-gray-700 mb-1.5">
                Usuário ou Email
              </label>
              <input
                {...register('username')}
                id="username"
                type="text"
                autoComplete="username"
                placeholder="admin"
                aria-invalid={errors.username ? true : undefined}
                aria-describedby={errors.username ? 'username-error' : undefined}
                className="w-full px-4 py-2.5 rounded-xl border border-gray-300 bg-white text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
              />
              {errors.username && (
                <p id="username-error" className="mt-1 text-xs text-red-600">{errors.username.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-medium text-gray-700 mb-1.5">
                Senha
              </label>
              <div className="relative">
                <input
                  {...register('password')}
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  placeholder="••••••••"
                  aria-invalid={errors.password ? true : undefined}
                  aria-describedby={errors.password ? 'password-error' : undefined}
                  className="w-full px-4 py-2.5 pr-10 rounded-xl border border-gray-300 bg-white text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {errors.password && (
                <p id="password-error" className="mt-1 text-xs text-red-600">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-emerald-600 text-white text-sm font-medium rounded-xl hover:bg-emerald-700 disabled:opacity-50 transition shadow-sm"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Entrando...
                </>
              ) : (
                'Entrar'
              )}
            </button>

            <p className="text-center text-xs text-gray-500">
              Não tem conta?{' '}
              <Link to="/register" className="font-medium text-emerald-600 hover:text-emerald-700 hover:underline">
                Registre-se
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
