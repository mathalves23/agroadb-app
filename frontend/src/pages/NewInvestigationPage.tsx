import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  ArrowLeft,
  Search,
  User,
  FileText,
  Building2,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Shield,
  Zap,
} from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { investigationService } from '@/services/investigationService'
import { formatCPFCNPJ } from '@/lib/utils'

type SearchType = 'all' | 'cpf' | 'cnpj' | 'nome'

const investigationSchema = z
  .object({
    target_name: z.string().optional(),
    target_cpf_cnpj: z.string().optional(),
    target_description: z.string().optional(),
    priority: z.number().min(1).max(5).default(3),
    search_type: z.enum(['cpf', 'cnpj', 'nome', 'all']).default('all'),
  })
  .superRefine((data, ctx) => {
    const name = data.target_name?.trim() || ''
    const doc = data.target_cpf_cnpj?.replace(/\D/g, '') || ''

    if (data.search_type === 'cpf') {
      if (doc.length !== 11) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'CPF deve ter 11 dígitos', path: ['target_cpf_cnpj'] })
      }
    } else if (data.search_type === 'cnpj') {
      if (doc.length !== 14) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'CNPJ deve ter 14 dígitos', path: ['target_cpf_cnpj'] })
      }
    } else if (data.search_type === 'nome') {
      if (name.length < 3) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Nome deve ter no mínimo 3 caracteres', path: ['target_name'] })
      }
    } else {
      // all — precisa de pelo menos um
      if (!name && !doc) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Informe o nome ou CPF/CNPJ', path: ['target_name'] })
      }
      if (doc && doc.length !== 11 && doc.length !== 14) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'CPF deve ter 11 dígitos ou CNPJ deve ter 14', path: ['target_cpf_cnpj'] })
      }
    }
  })

type InvestigationFormData = z.infer<typeof investigationSchema>

export default function NewInvestigationPage() {
  const navigate = useNavigate()
  const [error, setError] = useState<string>('')
  const [docType, setDocType] = useState<'none' | 'cpf' | 'cnpj'>('none')

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<InvestigationFormData>({
    resolver: zodResolver(investigationSchema),
    defaultValues: {
      priority: 3,
      search_type: 'all',
      target_name: '',
      target_cpf_cnpj: '',
    },
  })

  const watchCpfCnpj = watch('target_cpf_cnpj')
  const watchSearchType = watch('search_type') as SearchType

  const handleDocChange = useCallback(
    (value: string) => {
      const cleaned = value.replace(/\D/g, '')
      if (cleaned.length <= 11) {
        setDocType(cleaned.length > 0 ? 'cpf' : 'none')
        setValue('target_cpf_cnpj', formatCPFCNPJ(cleaned))
      } else {
        setDocType('cnpj')
        setValue('target_cpf_cnpj', formatCPFCNPJ(cleaned.slice(0, 14)))
      }
    },
    [setValue]
  )

  const mutation = useMutation({
    mutationFn: investigationService.create,
    onSuccess: (data) => {
      navigate(`/investigations/${data.id}`)
    },
    onError: (err: unknown) => {
      const axiosErr = err as { response?: { data?: { detail?: string } } }
      setError(axiosErr?.response?.data?.detail || (err instanceof Error ? err.message : 'Erro ao criar investigação'))
    },
  })

  const onSubmit = (data: InvestigationFormData) => {
    setError('')
    const cleaned = data.target_cpf_cnpj?.replace(/\D/g, '') || ''
    const name = data.target_name?.trim() || ''

    // Se pesquisa por CPF/CNPJ sem nome, usar o documento como nome
    const finalName = name || (cleaned ? `Investigação ${formatCPFCNPJ(cleaned)}` : 'Investigação sem nome')

    mutation.mutate({
      target_name: finalName,
      target_cpf_cnpj: cleaned || undefined,
      target_description: data.target_description?.trim() || undefined,
      priority: data.priority,
    })
  }

  // Controle de visibilidade dos campos
  const showNameField = watchSearchType === 'nome' || watchSearchType === 'all'
  const showDocField = watchSearchType === 'cpf' || watchSearchType === 'cnpj' || watchSearchType === 'all'
  const nameRequired = watchSearchType === 'nome'
  const docRequired = watchSearchType === 'cpf' || watchSearchType === 'cnpj'

  const docPlaceholder =
    watchSearchType === 'cpf'
      ? '000.000.000-00'
      : watchSearchType === 'cnpj'
        ? '00.000.000/0000-00'
        : '000.000.000-00 ou 00.000.000/0000-00'

  const docLabel =
    watchSearchType === 'cpf'
      ? 'CPF'
      : watchSearchType === 'cnpj'
        ? 'CNPJ'
        : 'CPF ou CNPJ'

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <button
        onClick={() => navigate('/investigations')}
        className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900 transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Voltar para investigações</span>
      </button>

      <div className="flex items-center gap-4">
        <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-3 shadow-sm">
          <Search className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Nova Investigação</h1>
          <p className="text-sm text-gray-500">
            Pesquise por CPF, CNPJ ou nome para iniciar a investigação patrimonial
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {error && (
          <div className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-xl p-4">
            <AlertTriangle className="h-5 w-5 text-red-500 shrink-0" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Tipo de busca */}
        <div className="bg-white rounded-xl border border-gray-200/60 p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Tipo de pesquisa</h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {([
              { value: 'all' as SearchType, label: 'Todas as bases', icon: Zap, desc: 'Nome + documento' },
              { value: 'cpf' as SearchType, label: 'Por CPF', icon: User, desc: 'Apenas CPF' },
              { value: 'cnpj' as SearchType, label: 'Por CNPJ', icon: Building2, desc: 'Apenas CNPJ' },
              { value: 'nome' as SearchType, label: 'Por nome', icon: FileText, desc: 'Apenas nome' },
            ]).map((type) => (
              <button
                key={type.value}
                type="button"
                onClick={() => setValue('search_type', type.value)}
                className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition ${
                  watchSearchType === type.value
                    ? 'border-emerald-500 bg-emerald-50/50'
                    : 'border-gray-100 hover:border-gray-300'
                }`}
              >
                <type.icon
                  className={`h-5 w-5 ${
                    watchSearchType === type.value ? 'text-emerald-600' : 'text-gray-400'
                  }`}
                />
                <span
                  className={`text-xs font-medium ${
                    watchSearchType === type.value ? 'text-emerald-700' : 'text-gray-500'
                  }`}
                >
                  {type.label}
                </span>
                <span className="text-[10px] text-gray-400">{type.desc}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Dados do alvo */}
        <div className="bg-white rounded-xl border border-gray-200/60 p-6 space-y-5">
          <h2 className="text-sm font-semibold text-gray-700">Dados do alvo</h2>

          {/* CPF / CNPJ — aparece primeiro quando pesquisa é por documento */}
          {showDocField && (
            <div>
              <label htmlFor="target_cpf_cnpj" className="block text-sm font-medium text-gray-700 mb-1.5">
                {docLabel}
                {docRequired && <span className="text-red-500 ml-0.5">*</span>}
                {docType !== 'none' && watchSearchType === 'all' && (
                  <span className={`ml-2 text-xs font-normal ${docType === 'cpf' ? 'text-blue-600' : 'text-violet-600'}`}>
                    ({docType === 'cpf' ? 'Pessoa Física' : 'Pessoa Jurídica'})
                  </span>
                )}
              </label>
              <div className="relative">
                <Shield className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  id="target_cpf_cnpj"
                  type="text"
                  value={watchCpfCnpj || ''}
                  onChange={(e) => handleDocChange(e.target.value)}
                  placeholder={docPlaceholder}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-200 bg-white text-gray-900 placeholder-gray-400 font-mono focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
                  maxLength={18}
                />
              </div>
              {errors.target_cpf_cnpj && (
                <p className="mt-1.5 text-xs text-red-600 flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  {errors.target_cpf_cnpj.message}
                </p>
              )}
              <p className="mt-1.5 text-xs text-gray-400">
                O CPF/CNPJ será usado para pesquisar em SNCR, SIGEF, SICAR, DataJud, Transparência, BrasilAPI, CVM e outras bases.
              </p>
            </div>
          )}

          {/* Nome completo */}
          {showNameField && (
            <div>
              <label htmlFor="target_name" className="block text-sm font-medium text-gray-700 mb-1.5">
                {watchSearchType === 'nome' ? 'Nome completo' : 'Nome (opcional)'}
                {nameRequired && <span className="text-red-500 ml-0.5">*</span>}
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  {...register('target_name')}
                  id="target_name"
                  type="text"
                  placeholder={watchSearchType === 'nome' ? 'Ex: João da Silva' : 'Nome do investigado (opcional)'}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
                />
              </div>
              {errors.target_name && (
                <p className="mt-1.5 text-xs text-red-600 flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  {errors.target_name.message}
                </p>
              )}
            </div>
          )}

          {/* Nome quando pesquisa é por CPF/CNPJ (campo escondido por padrão, mostra apenas como complemento) */}
          {!showNameField && (
            <div>
              <label htmlFor="target_name" className="block text-sm font-medium text-gray-700 mb-1.5">
                Nome (opcional)
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  {...register('target_name')}
                  id="target_name"
                  type="text"
                  placeholder="Nome do investigado (opcional, para identificação)"
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
                />
              </div>
              <p className="mt-1 text-[11px] text-gray-400">
                Se não informado, será gerado automaticamente a partir do CPF/CNPJ.
              </p>
            </div>
          )}

          {/* Contexto / Descrição */}
          <div>
            <label htmlFor="target_description" className="block text-sm font-medium text-gray-700 mb-1.5">
              Contexto / Descrição
            </label>
            <textarea
              {...register('target_description')}
              id="target_description"
              rows={3}
              placeholder="Informações adicionais: contexto judicial, relação com o caso, observações..."
              className="w-full px-4 py-2.5 rounded-lg border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition resize-none"
            />
          </div>

          {/* Prioridade */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Prioridade</label>
            <div className="flex items-center gap-3">
              {[
                { value: 1, label: 'Baixa', color: 'bg-gray-200' },
                { value: 2, label: 'Normal', color: 'bg-blue-300' },
                { value: 3, label: 'Média', color: 'bg-amber-300' },
                { value: 4, label: 'Alta', color: 'bg-orange-400' },
                { value: 5, label: 'Urgente', color: 'bg-red-500' },
              ].map((level) => (
                <button
                  key={level.value}
                  type="button"
                  onClick={() => setValue('priority', level.value)}
                  className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg border-2 transition ${
                    watch('priority') === level.value
                      ? 'border-emerald-500 bg-emerald-50/50'
                      : 'border-gray-100 hover:border-gray-300'
                  }`}
                >
                  <div className={`h-2 w-8 rounded-full ${level.color}`} />
                  <span className="text-[10px] font-medium text-gray-600">{level.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* O que será pesquisado */}
        <div className="bg-white rounded-xl border border-gray-200/60 p-6">
          <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <Zap className="h-4 w-4 text-amber-500" />
            Bases que serão consultadas
          </h3>
          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
            {[
              { name: 'SNCR/INCRA', desc: 'Cadastro Rural', free: false },
              { name: 'SIGEF', desc: 'Parcelas Georreferenciadas', free: false },
              { name: 'SICAR', desc: 'Cadastro Ambiental Rural', free: false },
              { name: 'DataJud/CNJ', desc: 'Processos Judiciais', free: true },
              { name: 'CNPJ/RFB', desc: 'Receita Federal', free: false },
              { name: 'CADIN', desc: 'Restrições Cadastrais', free: false },
              { name: 'CND', desc: 'Certidão de Débitos', free: false },
              { name: 'SNCCI', desc: 'Crédito Instalação', free: false },
              { name: 'BrasilAPI', desc: 'CNPJ, CEP, Bancos', free: true },
              { name: 'Transparência/CGU', desc: 'Sanções, Contratos, Servidores', free: true },
              { name: 'ReceitaWS', desc: 'CNPJ público gratuito', free: true },
              { name: 'IBGE', desc: 'Municípios, Estados, Nomes', free: true },
              { name: 'TSE', desc: 'Candidatos, Bens Declarados', free: true },
              { name: 'CVM', desc: 'Fundos, FIIs, Corretoras', free: true },
              { name: 'BCB', desc: 'SELIC, IPCA, PIX, Câmbio', free: true },
              { name: 'dados.gov.br', desc: 'Datasets Abertos', free: true },
              { name: 'TJMG', desc: 'Processos Judiciais MG', free: true },
              { name: 'Antecedentes/MG', desc: 'Certidão Criminal MG', free: true },
              { name: 'SICAR/CAR', desc: 'Imóvel Rural por CAR', free: true },
              { name: 'Portal gov.br', desc: 'Serviços Públicos', free: false },
              { name: 'Serv. Estaduais', desc: 'Carta de Serviços', free: false },
              { name: 'Caixa FGTS/CRF', desc: 'Regularidade FGTS', free: true },
              { name: 'BNMP/CNJ', desc: 'Mandados de Prisão', free: true },
              { name: 'SEEU/CNJ', desc: 'Execução Penal', free: true },
              { name: 'SIGEF Público', desc: 'Parcelas INCRA', free: true },
              { name: 'Receita Federal (CPF)', desc: 'Situação cadastral', free: true },
              { name: 'Receita Federal (CNPJ)', desc: 'Dados cadastrais PJ', free: true },
            ].map((base) => (
              <div key={base.name} className="flex items-center gap-2 bg-gray-50/80 rounded-lg px-3 py-2 border border-gray-100">
                <CheckCircle2 className={`h-3.5 w-3.5 shrink-0 ${base.free ? 'text-emerald-500' : 'text-amber-500'}`} />
                <div className="min-w-0">
                  <p className="text-xs font-medium text-gray-700">{base.name}</p>
                  <p className="text-[10px] text-gray-400 truncate">{base.desc}</p>
                </div>
                {base.free && <span className="ml-auto text-[9px] font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded whitespace-nowrap">FREE</span>}
              </div>
            ))}
          </div>
        </div>

        {/* Ações */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => navigate('/investigations')}
            className="px-5 py-2.5 rounded-lg border border-gray-200 text-sm font-medium text-gray-600 hover:bg-gray-50 transition"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg bg-emerald-600 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50 transition shadow-sm"
          >
            {mutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Criando investigação...
              </>
            ) : (
              <>
                <Search className="h-4 w-4" />
                Iniciar Investigação
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
