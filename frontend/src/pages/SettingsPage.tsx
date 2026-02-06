import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeft,
  Settings,
  Key,
  Database,
  Globe,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Info,
  ExternalLink,
  Shield,
  Scale,
  Building2,
  Leaf,
  Zap,
} from 'lucide-react'
import { legalService } from '@/services/legalService'

interface IntegrationInfo {
  name: string
  description: string
  category: 'free' | 'key' | 'conecta'
  status?: 'active' | 'inactive' | 'partial'
  helpUrl?: string
  envVars?: string[]
  notes?: string
}

const integrations: IntegrationInfo[] = [
  // --- APIs Gratuitas (sem configuração) ---
  {
    name: 'BrasilAPI',
    description: 'CNPJ, CEP, bancos, IBGE, feriados',
    category: 'free',
    helpUrl: 'https://brasilapi.com.br',
  },
  {
    name: 'IBGE',
    description: 'Estados, municípios, frequência de nomes',
    category: 'free',
    helpUrl: 'https://servicodados.ibge.gov.br',
  },
  {
    name: 'Banco Central',
    description: 'PIX, taxas de câmbio, SELIC, IPCA, CDI',
    category: 'free',
    helpUrl: 'https://dadosabertos.bcb.gov.br',
  },
  {
    name: 'TSE (Dados Abertos)',
    description: 'Candidatos, bens declarados, datasets eleitorais',
    category: 'free',
    helpUrl: 'https://dadosabertos.tse.jus.br',
  },
  {
    name: 'CVM (Dados Abertos)',
    description: 'Fundos, FIIs, participantes do mercado',
    category: 'free',
    helpUrl: 'https://dados.cvm.gov.br',
  },
  {
    name: 'dados.gov.br',
    description: 'Catálogo de dados abertos do governo federal',
    category: 'free',
    helpUrl: 'https://dados.gov.br',
  },
  {
    name: 'REDESIM / ReceitaWS',
    description: 'Consulta pública de CNPJ com fallback',
    category: 'free',
    helpUrl: 'https://receitaws.com.br',
  },
  {
    name: 'Receita Federal (CPF)',
    description: 'Situação cadastral, nome, nascimento, óbito',
    category: 'free',
    helpUrl: 'https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao',
  },
  {
    name: 'Receita Federal (CNPJ)',
    description: 'Razão social, QSA, endereço, CNAE, capital social — 4 fontes de fallback',
    category: 'free',
    helpUrl: 'https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva',
  },
  {
    name: 'TJMG',
    description: 'Processos públicos do Tribunal de Justiça de MG',
    category: 'free',
    helpUrl: 'https://www.tjmg.jus.br',
  },
  {
    name: 'BNMP / CNJ',
    description: 'Mandados de prisão (Banco Nacional de Mandados de Prisão)',
    category: 'free',
    helpUrl: 'https://portalbnmp.pdpj.jus.br',
  },
  {
    name: 'SEEU / CNJ',
    description: 'Processos de execução penal unificado',
    category: 'free',
    helpUrl: 'https://seeu.pje.jus.br',
  },
  {
    name: 'SICAR Público',
    description: 'Cadastro Ambiental Rural — consulta por CAR',
    category: 'free',
    helpUrl: 'https://consultapublica.car.gov.br',
  },
  {
    name: 'SIGEF Público',
    description: 'Parcelas INCRA (até 5 páginas por consulta)',
    category: 'free',
    helpUrl: 'https://sigef.incra.gov.br/consultar/parcelas',
  },
  {
    name: 'Antecedentes MG',
    description: 'Atestado de antecedentes criminais (Polícia Civil MG)',
    category: 'free',
    helpUrl: 'https://www.policiacivil.mg.gov.br/pagina/emissao-atestado',
  },
  {
    name: 'Caixa FGTS / CRF',
    description: 'Regularidade do empregador (FGTS)',
    category: 'free',
    helpUrl: 'https://consulta-crf.caixa.gov.br',
  },
  // --- APIs com chave (gratuitas com registro) ---
  {
    name: 'Portal da Transparência (CGU)',
    description: 'Contratos, servidores, sanções, benefícios sociais',
    category: 'key',
    helpUrl: 'https://portaldatransparencia.gov.br/api-de-dados',
    envVars: ['PORTAL_TRANSPARENCIA_API_KEY'],
    notes: 'Registro gratuito. Acesse o link, crie uma conta e copie a API Key.',
  },
  {
    name: 'DataJud (CNJ)',
    description: 'Processos judiciais em todos os tribunais brasileiros',
    category: 'key',
    helpUrl: 'https://datajud-wiki.cnj.jus.br/api-publica/acesso',
    envVars: ['DATAJUD_API_KEY'],
    notes: 'Chave pública disponível na Wiki do DataJud. Já vem pré-configurada.',
  },
  // --- APIs Conecta gov.br (credenciamento de órgão público) ---
  {
    name: 'SNCR (Conecta)',
    description: 'Sistema Nacional de Cadastro Rural — imóveis rurais, CCIR',
    category: 'conecta',
    helpUrl: 'https://www.gov.br/conecta/catalogo/',
    envVars: ['CONECTA_SNCR_CLIENT_ID', 'CONECTA_SNCR_CLIENT_SECRET'],
    notes: 'Disponível apenas para órgãos públicos federais e estaduais.',
  },
  {
    name: 'SIGEF (Conecta)',
    description: 'Sistema de Gestão Fundiária — parcelas georreferenciadas',
    category: 'conecta',
    helpUrl: 'https://www.gov.br/conecta/catalogo/',
    envVars: ['CONECTA_SIGEF_CLIENT_ID', 'CONECTA_SIGEF_CLIENT_SECRET'],
    notes: 'Disponível apenas para órgãos públicos.',
  },
  {
    name: 'SICAR (Conecta)',
    description: 'Cadastro Ambiental Rural — consulta por CPF/CNPJ',
    category: 'conecta',
    helpUrl: 'https://www.gov.br/conecta/catalogo/',
    envVars: ['CONECTA_SICAR_CLIENT_ID', 'CONECTA_SICAR_CLIENT_SECRET'],
  },
  {
    name: 'SIGEF GEO (Conecta)',
    description: 'Parcelas georreferenciadas com coordenadas GeoJSON',
    category: 'conecta',
    helpUrl: 'https://www.gov.br/conecta/catalogo/',
    envVars: ['CONECTA_SIGEF_GEO_CLIENT_ID', 'CONECTA_SIGEF_GEO_CLIENT_SECRET'],
  },
  {
    name: 'SNCCI (Conecta)',
    description: 'Créditos de instalação — parcelas, boletos',
    category: 'conecta',
    helpUrl: 'https://www.gov.br/conecta/catalogo/',
    envVars: ['CONECTA_SNCCI_CLIENT_ID', 'CONECTA_SNCCI_CLIENT_SECRET'],
  },
  {
    name: 'CNPJ / RFB (Conecta)',
    description: 'Consulta completa de CNPJ via Receita Federal',
    category: 'conecta',
    helpUrl: 'https://www.gov.br/conecta/catalogo/',
    envVars: ['CONECTA_CNPJ_CLIENT_ID', 'CONECTA_CNPJ_CLIENT_SECRET'],
  },
  {
    name: 'CND / RFB (Conecta)',
    description: 'Certidão Negativa de Débitos',
    category: 'conecta',
    helpUrl: 'https://www.gov.br/conecta/catalogo/',
    envVars: ['CONECTA_CND_CLIENT_ID', 'CONECTA_CND_CLIENT_SECRET'],
  },
  {
    name: 'CADIN (Conecta)',
    description: 'Cadastro de Inadimplentes — débitos com órgãos federais',
    category: 'conecta',
    helpUrl: 'https://www.gov.br/conecta/catalogo/',
    envVars: ['CONECTA_CADIN_CLIENT_ID', 'CONECTA_CADIN_CLIENT_SECRET'],
  },
]

const categoryConfig = {
  free: { label: 'APIs Gratuitas', icon: Zap, color: 'emerald', description: 'Funcionam sem configuração' },
  key: { label: 'Requer API Key', icon: Key, color: 'amber', description: 'Registro gratuito necessário' },
  conecta: { label: 'Conecta gov.br', icon: Shield, color: 'blue', description: 'Restritas a órgãos públicos' },
}

export default function SettingsPage() {
  const navigate = useNavigate()
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'free' | 'key' | 'conecta'>('all')

  const { data: integrationStatus, isLoading, refetch } = useQuery({
    queryKey: ['integration-status'],
    queryFn: () => legalService.getIntegrationStatus(),
    staleTime: 60_000,
  })

  // Derivar status de cada integração a partir do endpoint /status
  const getStatus = (name: string): 'active' | 'inactive' | 'partial' => {
    if (!integrationStatus) return 'inactive'
    const statusMap: Record<string, string> = {
      'BrasilAPI': 'brasilapi',
      'IBGE': 'ibge',
      'Banco Central': 'bcb',
      'TSE (Dados Abertos)': 'tse',
      'CVM (Dados Abertos)': 'cvm',
      'dados.gov.br': 'dados_gov',
      'REDESIM / ReceitaWS': 'redesim',
      'Receita Federal (CPF)': 'receita_cpf',
      'Receita Federal (CNPJ)': 'receita_cnpj',
      'TJMG': 'tjmg',
      'BNMP / CNJ': 'bnmp_cnj',
      'SEEU / CNJ': 'seeu_cnj',
      'SICAR Público': 'sicar_publico',
      'SIGEF Público': 'sigef_publico',
      'Antecedentes MG': 'antecedentes_mg',
      'Caixa FGTS / CRF': 'caixa_fgts',
      'Portal da Transparência (CGU)': 'portal_transparencia',
      'DataJud (CNJ)': 'datajud',
      'SNCR (Conecta)': 'conecta_sncr',
      'SIGEF (Conecta)': 'conecta_sigef',
      'SICAR (Conecta)': 'conecta_sicar',
      'SIGEF GEO (Conecta)': 'conecta_sigef_geo',
      'SNCCI (Conecta)': 'conecta_sncci',
      'CNPJ / RFB (Conecta)': 'conecta_cnpj',
      'CND / RFB (Conecta)': 'conecta_cnd',
      'CADIN (Conecta)': 'conecta_cadin',
    }
    const key = statusMap[name]
    if (!key) return 'active' // APIs gratuitas sem mapeamento estão sempre ativas
    const entry = (integrationStatus as Record<string, any>)?.[key]
    if (!entry) return 'active' // Não listada no status = funciona sem config
    if (entry.configured === true) return 'active'
    if (entry.configured === false && entry.auth_required === false) return 'active'
    return 'inactive'
  }

  const filtered = selectedCategory === 'all' ? integrations : integrations.filter((i) => i.category === selectedCategory)

  const counts = {
    all: integrations.length,
    free: integrations.filter((i) => i.category === 'free').length,
    key: integrations.filter((i) => i.category === 'key').length,
    conecta: integrations.filter((i) => i.category === 'conecta').length,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-500 hover:text-gray-900 transition">
            <ArrowLeft className="h-5 w-5" />
            <span className="text-sm">Voltar</span>
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
              <Settings className="h-6 w-6 text-emerald-600" />
              Integrações
            </h1>
            <p className="text-sm text-gray-500 mt-0.5">{integrations.length} bases de dados configuradas</p>
          </div>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-xl hover:bg-gray-50 transition"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Atualizar Status
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        {(Object.entries(categoryConfig) as [string, typeof categoryConfig.free][]).map(([key, cfg]) => {
          const Icon = cfg.icon
          const count = counts[key as keyof typeof counts]
          const activeCount = integrations
            .filter((i) => i.category === key)
            .filter((i) => getStatus(i.name) === 'active').length
          return (
            <div key={key} className="bg-white rounded-xl border border-gray-200/60 p-4">
              <div className="flex items-center gap-3">
                <div className={`bg-${cfg.color}-50 rounded-lg p-2`}>
                  <Icon className={`h-5 w-5 text-${cfg.color}-600`} />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900">{cfg.label}</p>
                  <p className="text-xs text-gray-500">
                    {activeCount}/{count} ativas
                  </p>
                </div>
              </div>
            </div>
          )
        })}
        <div className="bg-white rounded-xl border border-gray-200/60 p-4">
          <div className="flex items-center gap-3">
            <div className="bg-gray-50 rounded-lg p-2">
              <Database className="h-5 w-5 text-gray-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900">Total</p>
              <p className="text-xs text-gray-500">
                {integrations.filter((i) => getStatus(i.name) === 'active').length}/{integrations.length} ativas
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-xl w-fit">
        {(['all', 'free', 'key', 'conecta'] as const).map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              selectedCategory === cat ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {cat === 'all' ? `Todas (${counts.all})` : `${categoryConfig[cat].label} (${counts[cat]})`}
          </button>
        ))}
      </div>

      {/* Info banner for Conecta */}
      {(selectedCategory === 'conecta' || selectedCategory === 'all') && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start gap-3">
          <Info className="h-5 w-5 text-blue-600 mt-0.5 shrink-0" />
          <div className="text-sm">
            <p className="font-medium text-blue-900 mb-1">APIs Conecta gov.br</p>
            <p className="text-blue-700">
              As APIs do Conecta são restritas a <strong>órgãos públicos federais e estaduais</strong>. Para solicitar
              acesso, acesse{' '}
              <a href="https://www.gov.br/conecta/catalogo/" target="_blank" rel="noopener noreferrer" className="underline font-medium">
                gov.br/conecta/catalogo
              </a>
              . Após aprovação, configure as credenciais (<code className="bg-blue-100 px-1 rounded">CLIENT_ID</code> e{' '}
              <code className="bg-blue-100 px-1 rounded">CLIENT_SECRET</code>) no arquivo <code className="bg-blue-100 px-1 rounded">.env</code> do backend.
            </p>
          </div>
        </div>
      )}

      {/* Integration Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {filtered.map((integration) => {
          const status = getStatus(integration.name)
          const catCfg = categoryConfig[integration.category]

          return (
            <div
              key={integration.name}
              className="bg-white rounded-xl border border-gray-200/60 p-4 hover:shadow-sm transition"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {integration.category === 'free' && <Zap className="h-4 w-4 text-emerald-500" />}
                  {integration.category === 'key' && <Key className="h-4 w-4 text-amber-500" />}
                  {integration.category === 'conecta' && <Shield className="h-4 w-4 text-blue-500" />}
                  <h3 className="text-sm font-semibold text-gray-900">{integration.name}</h3>
                </div>
                {status === 'active' ? (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] font-semibold rounded-full">
                    <CheckCircle2 className="h-3 w-3" />
                    Ativa
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-100 text-gray-500 text-[10px] font-semibold rounded-full">
                    <XCircle className="h-3 w-3" />
                    Inativa
                  </span>
                )}
              </div>

              <p className="text-xs text-gray-500 mb-3 leading-relaxed">{integration.description}</p>

              {integration.envVars && (
                <div className="mb-3">
                  <p className="text-[10px] font-medium text-gray-400 uppercase tracking-wider mb-1">Variáveis .env</p>
                  <div className="flex flex-wrap gap-1">
                    {integration.envVars.map((v) => (
                      <code key={v} className="text-[10px] bg-gray-50 text-gray-600 px-1.5 py-0.5 rounded border border-gray-100">
                        {v}
                      </code>
                    ))}
                  </div>
                </div>
              )}

              {integration.notes && (
                <p className="text-[10px] text-gray-400 mb-3 leading-relaxed">{integration.notes}</p>
              )}

              <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                <span className={`text-[10px] font-medium text-${catCfg.color}-600 bg-${catCfg.color}-50 px-2 py-0.5 rounded-full`}>
                  {catCfg.label}
                </span>
                {integration.helpUrl && (
                  <a
                    href={integration.helpUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-[10px] text-gray-400 hover:text-emerald-600 transition"
                  >
                    <ExternalLink className="h-3 w-3" />
                    Documentação
                  </a>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* How to configure */}
      <div className="bg-white rounded-xl border border-gray-200/60 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Globe className="h-5 w-5 text-emerald-600" />
          Como configurar
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="bg-emerald-50 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold text-emerald-700">1</div>
              <h3 className="text-sm font-semibold text-gray-900">APIs Gratuitas</h3>
            </div>
            <p className="text-xs text-gray-500 leading-relaxed">
              Já estão funcionando automaticamente. BrasilAPI, IBGE, BCB, Receita Federal (CPF/CNPJ), BNMP, SEEU, TJMG e outras
              não precisam de nenhuma configuração.
            </p>
          </div>
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="bg-amber-50 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold text-amber-700">2</div>
              <h3 className="text-sm font-semibold text-gray-900">APIs com Chave</h3>
            </div>
            <p className="text-xs text-gray-500 leading-relaxed">
              Registre-se gratuitamente nos portais (Portal da Transparência, DataJud), obtenha sua API Key, e configure no arquivo{' '}
              <code className="bg-gray-100 px-1 rounded text-[10px]">backend/.env</code>. Reinicie o backend após alterar.
            </p>
          </div>
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="bg-blue-50 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold text-blue-700">3</div>
              <h3 className="text-sm font-semibold text-gray-900">Conecta gov.br</h3>
            </div>
            <p className="text-xs text-gray-500 leading-relaxed">
              Solicite acesso como órgão público em{' '}
              <a href="https://www.gov.br/conecta/catalogo/" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
                gov.br/conecta
              </a>
              . Após aprovação, configure <code className="bg-gray-100 px-1 rounded text-[10px]">CLIENT_ID</code> e{' '}
              <code className="bg-gray-100 px-1 rounded text-[10px]">CLIENT_SECRET</code> no <code className="bg-gray-100 px-1 rounded text-[10px]">.env</code>.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
