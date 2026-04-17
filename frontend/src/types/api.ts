// API Types
export interface User {
  id: number
  email: string
  username: string
  full_name: string
  organization?: string
  oab_number?: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  full_name: string
  password: string
  organization?: string
  oab_number?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export type InvestigationStatus = 'pending' | 'in_progress' | 'completed' | 'failed'

export interface Investigation {
  id: number
  user_id: number
  target_name: string
  target_cpf_cnpj?: string
  target_description?: string
  status: InvestigationStatus
  priority: number
  properties_found: number
  lease_contracts_found: number
  companies_found: number
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface InvestigationCreate {
  target_name: string
  target_cpf_cnpj?: string
  target_description?: string
  priority?: number
}

export interface InvestigationListResponse {
  items: Investigation[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface Property {
  id: number
  investigation_id: number
  car_number?: string
  ccir_number?: string
  matricula?: string
  property_name?: string
  area_hectares?: number
  state?: string
  city?: string
  address?: string
  coordinates?: { lat: number; lng: number } | Record<string, unknown>
  owner_name?: string
  owner_cpf_cnpj?: string
  data_source: string
  created_at: string
  updated_at: string
}

export interface LeaseContract {
  id: number
  investigation_id: number
  lessor_name?: string
  lessor_cpf_cnpj?: string
  lessee_name?: string
  lessee_cpf_cnpj?: string
  property_description?: string
  area_leased?: number
  value?: number
  data_source: string
  created_at: string
  updated_at: string
}

export interface Company {
  id: number
  investigation_id: number
  cnpj: string
  corporate_name?: string
  trade_name?: string
  status?: string
  state?: string
  city?: string
  address?: string
  main_activity?: string
  partners?: Array<{ name: string; role?: string; cpf_cnpj?: string }> | Record<string, unknown>
  data_source: string
  created_at: string
  updated_at: string
}
