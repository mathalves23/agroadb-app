import {
  Database,
  Key,
  Shield,
  Zap,
  type LucideIcon,
} from 'lucide-react'

export interface IntegrationInfo {
  name: string
  description: string
  category: 'free' | 'key' | 'conecta'
  status?: 'active' | 'inactive' | 'partial'
  helpUrl?: string
  envVars?: string[]
  notes?: string
}

export const integrations: IntegrationInfo[] = [
  { name: 'BrasilAPI', description: 'CNPJ, CEP, bancos, IBGE, feriados', category: 'free', helpUrl: 'https://brasilapi.com.br' },
  { name: 'IBGE', description: 'Estados, municípios, frequência de nomes', category: 'free', helpUrl: 'https://servicodados.ibge.gov.br' },
  { name: 'Banco Central', description: 'PIX, taxas de câmbio, SELIC, IPCA, CDI', category: 'free', helpUrl: 'https://dadosabertos.bcb.gov.br' },
  { name: 'TSE (Dados Abertos)', description: 'Candidatos, bens declarados, datasets eleitorais', category: 'free', helpUrl: 'https://dadosabertos.tse.jus.br' },
  { name: 'CVM (Dados Abertos)', description: 'Fundos, FIIs, participantes do mercado', category: 'free', helpUrl: 'https://dados.cvm.gov.br' },
  { name: 'dados.gov.br', description: 'Catálogo de dados abertos do governo federal', category: 'free', helpUrl: 'https://dados.gov.br' },
  { name: 'REDESIM / ReceitaWS', description: 'Consulta pública de CNPJ com fallback', category: 'free', helpUrl: 'https://receitaws.com.br' },
  { name: 'Receita Federal (CPF)', description: 'Situação cadastral, nome, nascimento, óbito', category: 'free', helpUrl: 'https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao' },
  { name: 'Receita Federal (CNPJ)', description: 'Razão social, QSA, endereço, CNAE, capital social — 4 fontes de fallback', category: 'free', helpUrl: 'https://solucoes.receita.fazenda.gov.br/Servicos/cnpjreva' },
  { name: 'TJMG', description: 'Processos públicos do Tribunal de Justiça de MG', category: 'free', helpUrl: 'https://www.tjmg.jus.br' },
  { name: 'BNMP / CNJ', description: 'Mandados de prisão (Banco Nacional de Mandados de Prisão)', category: 'free', helpUrl: 'https://portalbnmp.pdpj.jus.br' },
  { name: 'SEEU / CNJ', description: 'Processos de execução penal unificado', category: 'free', helpUrl: 'https://seeu.pje.jus.br' },
  { name: 'SICAR Público', description: 'Cadastro Ambiental Rural — consulta por CAR', category: 'free', helpUrl: 'https://consultapublica.car.gov.br' },
  { name: 'SIGEF Público', description: 'Parcelas INCRA (até 5 páginas por consulta)', category: 'free', helpUrl: 'https://sigef.incra.gov.br/consultar/parcelas' },
  { name: 'Antecedentes MG', description: 'Atestado de antecedentes criminais (Polícia Civil MG)', category: 'free', helpUrl: 'https://www.policiacivil.mg.gov.br/pagina/emissao-atestado' },
  { name: 'Caixa FGTS / CRF', description: 'Regularidade do empregador (FGTS)', category: 'free', helpUrl: 'https://consulta-crf.caixa.gov.br' },
  { name: 'Portal da Transparência (CGU)', description: 'Contratos, servidores, sanções, benefícios sociais', category: 'key', helpUrl: 'https://portaldatransparencia.gov.br/api-de-dados', envVars: ['PORTAL_TRANSPARENCIA_API_KEY'], notes: 'Registro gratuito. Acesse o link, crie uma conta e copie a API Key.' },
  { name: 'DataJud (CNJ)', description: 'Processos judiciais em todos os tribunais brasileiros', category: 'key', helpUrl: 'https://datajud-wiki.cnj.jus.br/api-publica/acesso', envVars: ['DATAJUD_API_KEY'], notes: 'Chave pública disponível na Wiki do DataJud. Já vem pré-configurada.' },
  { name: 'SNCR (Conecta)', description: 'Sistema Nacional de Cadastro Rural — imóveis rurais, CCIR', category: 'conecta', helpUrl: 'https://www.gov.br/conecta/catalogo/', envVars: ['CONECTA_SNCR_CLIENT_ID', 'CONECTA_SNCR_CLIENT_SECRET'], notes: 'Disponível apenas para órgãos públicos federais e estaduais.' },
  { name: 'SIGEF (Conecta)', description: 'Sistema de Gestão Fundiária — parcelas georreferenciadas', category: 'conecta', helpUrl: 'https://www.gov.br/conecta/catalogo/', envVars: ['CONECTA_SIGEF_CLIENT_ID', 'CONECTA_SIGEF_CLIENT_SECRET'], notes: 'Disponível apenas para órgãos públicos.' },
  { name: 'SICAR (Conecta)', description: 'Cadastro Ambiental Rural — consulta por CPF/CNPJ', category: 'conecta', helpUrl: 'https://www.gov.br/conecta/catalogo/', envVars: ['CONECTA_SICAR_CLIENT_ID', 'CONECTA_SICAR_CLIENT_SECRET'] },
  { name: 'SIGEF GEO (Conecta)', description: 'Parcelas georreferenciadas com coordenadas GeoJSON', category: 'conecta', helpUrl: 'https://www.gov.br/conecta/catalogo/', envVars: ['CONECTA_SIGEF_GEO_CLIENT_ID', 'CONECTA_SIGEF_GEO_CLIENT_SECRET'] },
  { name: 'SNCCI (Conecta)', description: 'Créditos de instalação — parcelas, boletos', category: 'conecta', helpUrl: 'https://www.gov.br/conecta/catalogo/', envVars: ['CONECTA_SNCCI_CLIENT_ID', 'CONECTA_SNCCI_CLIENT_SECRET'] },
  { name: 'CNPJ / RFB (Conecta)', description: 'Consulta completa de CNPJ via Receita Federal', category: 'conecta', helpUrl: 'https://www.gov.br/conecta/catalogo/', envVars: ['CONECTA_CNPJ_CLIENT_ID', 'CONECTA_CNPJ_CLIENT_SECRET'] },
  { name: 'CND / RFB (Conecta)', description: 'Certidão Negativa de Débitos', category: 'conecta', helpUrl: 'https://www.gov.br/conecta/catalogo/', envVars: ['CONECTA_CND_CLIENT_ID', 'CONECTA_CND_CLIENT_SECRET'] },
  { name: 'CADIN (Conecta)', description: 'Cadastro de Inadimplentes — débitos com órgãos federais', category: 'conecta', helpUrl: 'https://www.gov.br/conecta/catalogo/', envVars: ['CONECTA_CADIN_CLIENT_ID', 'CONECTA_CADIN_CLIENT_SECRET'] },
]

export const categoryConfig: Record<
  'free' | 'key' | 'conecta',
  { label: string; icon: LucideIcon; color: string; description: string }
> = {
  free: { label: 'APIs Gratuitas', icon: Zap, color: 'emerald', description: 'Funcionam sem configuração' },
  key: { label: 'Requer API Key', icon: Key, color: 'amber', description: 'Registro gratuito necessário' },
  conecta: { label: 'Conecta gov.br', icon: Shield, color: 'blue', description: 'Restritas a órgãos públicos' },
}

export const totalCategory = {
  label: 'Total',
  icon: Database,
  color: 'gray',
}
