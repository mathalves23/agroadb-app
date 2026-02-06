import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Shield, Loader2, AlertTriangle, Eye, EyeOff } from 'lucide-react'
import { authService } from '@/services/authService'

const registerSchema = z.object({
  email: z.string().email('Email inválido'),
  username: z.string().min(3, 'Usuário deve ter no mínimo 3 caracteres'),
  full_name: z.string().min(3, 'Nome completo deve ter no mínimo 3 caracteres'),
  password: z.string().min(8, 'Senha deve ter no mínimo 8 caracteres'),
  organization: z.string().optional(),
  oab_number: z.string().optional(),
})

type RegisterFormData = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const navigate = useNavigate()
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setIsLoading(true)
      setError('')
      await authService.register(data)
      navigate('/login')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      setError(axiosErr?.response?.data?.detail || (err instanceof Error ? err.message : 'Erro ao criar conta'))
    } finally {
      setIsLoading(false)
    }
  }

  const inputClass =
    'w-full px-4 py-2.5 rounded-xl border border-gray-300 bg-white text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition'

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
            Crie sua conta e<br />
            <span className="text-emerald-400">comece agora</span>
          </h2>
          <p className="mt-4 text-emerald-100/80 text-sm leading-relaxed max-w-md">
            Investigação patrimonial inteligente com acesso a bases governamentais integradas.
            Ideal para advogados, analistas e investigadores.
          </p>
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

          <h1 className="text-2xl font-bold text-gray-900">Criar conta</h1>
          <p className="mt-1 text-sm text-gray-500">Preencha seus dados para se registrar</p>

          <form className="mt-6 space-y-4" onSubmit={handleSubmit(onSubmit)} role="form" aria-label="Formulário de registro">
            {error && (
              <div className="flex items-center gap-2.5 bg-red-50 border border-red-200 rounded-xl p-3" aria-live="polite">
                <AlertTriangle className="h-4 w-4 text-red-500 shrink-0" />
                <p className="text-xs text-red-700">{error}</p>
              </div>
            )}

            <div>
              <label htmlFor="full_name" className="block text-xs font-medium text-gray-700 mb-1.5">Nome Completo *</label>
              <input
                {...register('full_name')}
                id="full_name"
                type="text"
                placeholder="João da Silva"
                aria-invalid={errors.full_name ? true : undefined}
                aria-describedby={errors.full_name ? 'full_name-error' : undefined}
                className={inputClass}
              />
              {errors.full_name && <p id="full_name-error" className="mt-1 text-xs text-red-600">{errors.full_name.message}</p>}
            </div>

            <div>
              <label htmlFor="email" className="block text-xs font-medium text-gray-700 mb-1.5">Email *</label>
              <input
                {...register('email')}
                id="email"
                type="email"
                placeholder="joao@email.com"
                aria-invalid={errors.email ? true : undefined}
                aria-describedby={errors.email ? 'email-error' : undefined}
                className={inputClass}
              />
              {errors.email && <p id="email-error" className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
            </div>

            <div>
              <label htmlFor="username" className="block text-xs font-medium text-gray-700 mb-1.5">Usuário *</label>
              <input
                {...register('username')}
                id="username"
                type="text"
                placeholder="joaosilva"
                aria-invalid={errors.username ? true : undefined}
                aria-describedby={errors.username ? 'username-error' : undefined}
                className={inputClass}
              />
              {errors.username && <p id="username-error" className="mt-1 text-xs text-red-600">{errors.username.message}</p>}
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-medium text-gray-700 mb-1.5">Senha *</label>
              <div className="relative">
                <input
                  {...register('password')}
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Mínimo 8 caracteres"
                  aria-invalid={errors.password ? true : undefined}
                  aria-describedby={errors.password ? 'password-error' : undefined}
                  className={inputClass + ' pr-10'}
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
              {errors.password && <p id="password-error" className="mt-1 text-xs text-red-600">{errors.password.message}</p>}
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="organization" className="block text-xs font-medium text-gray-700 mb-1.5">Organização</label>
                <input {...register('organization')} id="organization" type="text" placeholder="Escritório" className={inputClass} />
              </div>
              <div>
                <label htmlFor="oab_number" className="block text-xs font-medium text-gray-700 mb-1.5">OAB</label>
                <input {...register('oab_number')} id="oab_number" type="text" placeholder="SP 12345" className={inputClass} />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-emerald-600 text-white text-sm font-medium rounded-xl hover:bg-emerald-700 disabled:opacity-50 transition shadow-sm"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Criando...
                </>
              ) : (
                'Criar Conta'
              )}
            </button>

            <p className="text-center text-xs text-gray-500">
              Já tem conta?{' '}
              <Link to="/login" className="font-medium text-emerald-600 hover:text-emerald-700 hover:underline">
                Faça login
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
