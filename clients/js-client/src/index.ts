/**
 * AgroADB JavaScript/TypeScript Client
 * 
 * Cliente oficial para API do AgroADB - Sistema de Análise de Dados Agrários
 * 
 * @packageDocumentation
 */

export interface AgroADBConfig {
  baseUrl?: string;
  apiKey?: string;
  timeout?: number;
  maxRetries?: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  created_at: string;
}

export interface Investigation {
  id: number;
  title: string;
  description?: string;
  status: 'active' | 'completed' | 'archived';
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
  created_by?: User;
}

export interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  investigation_id: number;
  uploaded_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface ExportJob {
  job_id: string;
  dataset_name: string;
  export_format: 'csv' | 'json' | 'ndjson' | 'parquet';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  total_records: number;
  file_size_bytes?: number;
  download_url?: string;
  started_at: string;
  completed_at?: string;
}

/**
 * Erro customizado para API AgroADB
 */
export class AgroADBError extends Error {
  statusCode?: number;
  response?: any;

  constructor(message: string, statusCode?: number, response?: any) {
    super(message);
    this.name = 'AgroADBError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

/**
 * Cliente principal para API AgroADB
 * 
 * @example
 * ```typescript
 * import { AgroADBClient } from '@agroadb/client';
 * 
 * const client = new AgroADBClient({
 *   baseUrl: 'https://api.agroadb.com',
 *   apiKey: 'your_api_key'
 * });
 * 
 * // Login
 * await client.login('user@email.com', 'password');
 * 
 * // Listar investigações
 * const investigations = await client.investigations.list({ limit: 10 });
 * ```
 */
export class AgroADBClient {
  private baseUrl: string;
  private apiKey?: string;
  private accessToken?: string;
  private refreshToken?: string;
  private timeout: number;
  private maxRetries: number;

  public auth: AuthModule;
  public investigations: InvestigationsModule;
  public documents: DocumentsModule;
  public users: UsersModule;
  public analytics: AnalyticsModule;
  public integrations: IntegrationsModule;
  public export: ExportModule;

  /**
   * Cria uma nova instância do cliente AgroADB
   * 
   * @param config - Configuração do cliente
   */
  constructor(config: AgroADBConfig = {}) {
    this.baseUrl = (config.baseUrl || process.env.AGROADB_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
    this.apiKey = config.apiKey || process.env.AGROADB_API_KEY;
    this.timeout = config.timeout || 30000;
    this.maxRetries = config.maxRetries || 3;

    // Inicializar módulos
    this.auth = new AuthModule(this);
    this.investigations = new InvestigationsModule(this);
    this.documents = new DocumentsModule(this);
    this.users = new UsersModule(this);
    this.analytics = new AnalyticsModule(this);
    this.integrations = new IntegrationsModule(this);
    this.export = new ExportModule(this);
  }

  /**
   * Faz login e armazena tokens
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.auth.login({ email, password });
    this.accessToken = response.access_token;
    this.refreshToken = response.refresh_token;
    return response;
  }

  /**
   * Faz logout e limpa tokens
   */
  logout(): void {
    this.accessToken = undefined;
    this.refreshToken = undefined;
  }

  /**
   * Define token de acesso manualmente
   */
  setAccessToken(token: string): void {
    this.accessToken = token;
  }

  /**
   * Obtém headers para requisição
   */
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    } else if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    return headers;
  }

  /**
   * Faz requisição HTTP com retry automático
   */
  async request<T = any>(
    method: string,
    endpoint: string,
    options: {
      params?: Record<string, any>;
      data?: any;
      headers?: Record<string, string>;
    } = {}
  ): Promise<T> {
    const url = new URL(endpoint, this.baseUrl);
    
    // Adicionar query params
    if (options.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    const headers = {
      ...this.getHeaders(),
      ...options.headers,
    };

    const config: RequestInit = {
      method,
      headers,
    };

    if (options.data) {
      config.body = JSON.stringify(options.data);
    }

    let lastError: Error | undefined;

    // Retry logic
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(url.toString(), {
          ...config,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Tratar erros HTTP
        if (!response.ok) {
          const errorBody = await response.json().catch(() => ({}));
          
          if (response.status === 401) {
            throw new AgroADBError('Unauthorized', 401, errorBody);
          } else if (response.status === 404) {
            throw new AgroADBError('Not found', 404, errorBody);
          } else if (response.status === 422) {
            throw new AgroADBError('Validation error', 422, errorBody);
          } else if (response.status === 429) {
            throw new AgroADBError('Rate limit exceeded', 429, errorBody);
          } else {
            throw new AgroADBError(
              `API error: ${response.status}`,
              response.status,
              errorBody
            );
          }
        }

        const text = await response.text();
        return text ? JSON.parse(text) : ({} as T);

      } catch (error: any) {
        lastError = error;

        // Não fazer retry em alguns erros
        if (
          error instanceof AgroADBError &&
          [400, 401, 403, 404, 422].includes(error.statusCode || 0)
        ) {
          throw error;
        }

        // Aguardar antes de tentar novamente
        if (attempt < this.maxRetries) {
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
        }
      }
    }

    throw lastError || new AgroADBError('Request failed');
  }
}

/**
 * Classe base para módulos
 */
abstract class BaseModule {
  constructor(protected client: AgroADBClient) {}

  protected get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    return this.client.request<T>('GET', endpoint, { params });
  }

  protected post<T>(endpoint: string, data?: any): Promise<T> {
    return this.client.request<T>('POST', endpoint, { data });
  }

  protected put<T>(endpoint: string, data: any): Promise<T> {
    return this.client.request<T>('PUT', endpoint, { data });
  }

  protected patch<T>(endpoint: string, data: any): Promise<T> {
    return this.client.request<T>('PATCH', endpoint, { data });
  }

  protected delete<T>(endpoint: string): Promise<T> {
    return this.client.request<T>('DELETE', endpoint);
  }
}

/**
 * Módulo de autenticação
 */
export class AuthModule extends BaseModule {
  /**
   * Faz login
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    return this.post('/api/v1/auth/login', credentials);
  }

  /**
   * Registra novo usuário
   */
  async register(data: Partial<User> & { password: string }): Promise<User> {
    return this.post('/api/v1/auth/register', data);
  }

  /**
   * Renova token
   */
  async refresh(refreshToken: string): Promise<AuthResponse> {
    return this.post('/api/v1/auth/refresh', { refresh_token: refreshToken });
  }

  /**
   * Obtém dados do usuário atual
   */
  async me(): Promise<User> {
    return this.get('/api/v1/auth/me');
  }
}

/**
 * Módulo de investigações
 */
export class InvestigationsModule extends BaseModule {
  /**
   * Lista investigações
   */
  async list(params?: {
    limit?: number;
    offset?: number;
    status?: string;
    priority?: string;
  }): Promise<Investigation[]> {
    const response = await this.get<PaginatedResponse<Investigation>>(
      '/api/v1/investigations',
      params
    );
    return response.items;
  }

  /**
   * Obtém investigação por ID
   */
  async get(id: number): Promise<Investigation> {
    return this.get(`/api/v1/investigations/${id}`);
  }

  /**
   * Cria nova investigação
   */
  async create(data: Partial<Investigation>): Promise<Investigation> {
    return this.post('/api/v1/investigations', data);
  }

  /**
   * Atualiza investigação
   */
  async update(id: number, data: Partial<Investigation>): Promise<Investigation> {
    return this.put(`/api/v1/investigations/${id}`, data);
  }

  /**
   * Deleta investigação
   */
  async delete(id: number): Promise<void> {
    return this.delete(`/api/v1/investigations/${id}`);
  }

  /**
   * Busca investigações
   */
  async search(query: string, filters?: Record<string, any>): Promise<Investigation[]> {
    const response = await this.get<{ results: Investigation[] }>(
      '/api/v1/investigations/search',
      { q: query, ...filters }
    );
    return response.results;
  }
}

/**
 * Módulo de documentos
 */
export class DocumentsModule extends BaseModule {
  /**
   * Lista documentos
   */
  async list(investigationId: number): Promise<Document[]> {
    const response = await this.get<PaginatedResponse<Document>>(
      `/api/v1/investigations/${investigationId}/documents`
    );
    return response.items;
  }

  /**
   * Obtém documento
   */
  async get(id: number): Promise<Document> {
    return this.get(`/api/v1/documents/${id}`);
  }

  /**
   * Deleta documento
   */
  async delete(id: number): Promise<void> {
    return this.delete(`/api/v1/documents/${id}`);
  }
}

/**
 * Módulo de usuários
 */
export class UsersModule extends BaseModule {
  /**
   * Lista usuários
   */
  async list(params?: { limit?: number; offset?: number }): Promise<User[]> {
    const response = await this.get<PaginatedResponse<User>>('/api/v1/users', params);
    return response.items;
  }

  /**
   * Obtém usuário
   */
  async get(id: number): Promise<User> {
    return this.get(`/api/v1/users/${id}`);
  }

  /**
   * Cria usuário
   */
  async create(data: Partial<User> & { password: string }): Promise<User> {
    return this.post('/api/v1/users', data);
  }

  /**
   * Atualiza usuário
   */
  async update(id: number, data: Partial<User>): Promise<User> {
    return this.put(`/api/v1/users/${id}`, data);
  }

  /**
   * Deleta usuário
   */
  async delete(id: number): Promise<void> {
    return this.delete(`/api/v1/users/${id}`);
  }
}

/**
 * Módulo de analytics
 */
export class AnalyticsModule extends BaseModule {
  /**
   * Dashboard consolidado
   */
  async dashboard(params?: { start_date?: string; end_date?: string }): Promise<any> {
    return this.get('/api/v1/analytics/dashboard', params);
  }

  /**
   * Relatório de performance
   */
  async performanceReport(params?: { start_date?: string; end_date?: string }): Promise<any> {
    return this.get('/api/v1/analytics/reports/performance', params);
  }

  /**
   * Analytics de usuários
   */
  async userAnalytics(): Promise<any> {
    return this.get('/api/v1/analytics/user/dashboard');
  }

  /**
   * Análise de funil
   */
  async funnelAnalysis(funnelKey: string): Promise<any> {
    return this.get(`/api/v1/analytics/user/funnel/${funnelKey}`);
  }
}

/**
 * Módulo de integrações
 */
export class IntegrationsModule extends BaseModule {
  /**
   * Lista integrações
   */
  async list(): Promise<any[]> {
    const response = await this.get<{ integrations: any[] }>('/api/v1/integrations');
    return response.integrations;
  }

  /**
   * Busca no TJSP
   */
  async tjspSearch(cpf: string): Promise<any> {
    return this.post('/api/v1/integrations/tjsp/search', { cpf });
  }

  /**
   * Consulta Serasa
   */
  async serasaQuery(cpf: string): Promise<any> {
    return this.post('/api/v1/integrations/serasa/query', { cpf });
  }

  /**
   * Receita Federal
   */
  async receitaFederal(cnpj: string): Promise<any> {
    return this.post('/api/v1/integrations/receita-federal/cnpj', { cnpj });
  }
}

/**
 * Módulo de exportação
 */
export class ExportModule extends BaseModule {
  /**
   * Cria job de exportação
   */
  async createExport(params: {
    data_source: string;
    export_format?: 'csv' | 'json' | 'ndjson' | 'parquet';
    start_date?: string;
    end_date?: string;
  }): Promise<ExportJob> {
    return this.post('/api/v1/analytics/export/file/create', undefined);
  }

  /**
   * Status de exportação
   */
  async getStatus(jobId: string): Promise<ExportJob> {
    return this.get(`/api/v1/analytics/export/file/status/${jobId}`);
  }

  /**
   * Lista exportações
   */
  async list(limit: number = 50): Promise<ExportJob[]> {
    const response = await this.get<{ jobs: ExportJob[] }>(
      '/api/v1/analytics/export/file/list',
      { limit }
    );
    return response.jobs;
  }

  /**
   * Exporta para BigQuery
   */
  async exportToBigQuery(params: {
    project_id: string;
    dataset: string;
    table_name: string;
    data_source: string;
  }): Promise<any> {
    return this.post('/api/v1/analytics/export/warehouse/bigquery', undefined);
  }

  /**
   * Exporta para Redshift
   */
  async exportToRedshift(params: {
    cluster: string;
    database: string;
    table_name: string;
    data_source: string;
  }): Promise<any> {
    return this.post('/api/v1/analytics/export/warehouse/redshift', undefined);
  }
}

/**
 * Cria cliente com configuração padrão
 */
export function createClient(config?: AgroADBConfig): AgroADBClient {
  return new AgroADBClient(config);
}

// Export default
export default AgroADBClient;
