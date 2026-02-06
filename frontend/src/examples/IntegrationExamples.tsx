/**
 * Exemplo de Integração Frontend - Tribunais e Birôs de Crédito
 * 
 * Este arquivo demonstra como integrar as novas APIs no frontend React
 */

import { useState } from 'react';
import { api } from '@/services/api';

// ============================================
// 1. CONSULTA DE TRIBUNAIS ESTADUAIS
// ============================================

interface ConsultaTribunalRequest {
  cpf_cnpj: string;
  tribunal: string;
  investigation_id?: number;
}

interface ProcessoESAJ {
  numero_processo: string;
  tribunal: string;
  grau: string;
  classe: string;
  assunto: string;
  status: string;
  comarca: string;
  vara: string;
  partes: Array<{ tipo: string; nome: string }>;
  movimentacoes: Array<{ data: string; descricao: string }>;
}

/**
 * Hook para consulta de tribunais
 */
export const useTribunais = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const consultarESAJ1G = async (cpf_cnpj: string, tribunal: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/integrations/tribunais/esaj/1g', {
        cpf_cnpj,
        tribunal
      });
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao consultar tribunal');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const consultarESAJ2G = async (cpf_cnpj: string, tribunal: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/integrations/tribunais/esaj/2g', {
        cpf_cnpj,
        tribunal
      });
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao consultar tribunal');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const consultarProjudi = async (cpf_cnpj: string, tribunal: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/integrations/tribunais/projudi', {
        cpf_cnpj,
        tribunal
      });
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao consultar Projudi');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    consultarESAJ1G,
    consultarESAJ2G,
    consultarProjudi,
    loading,
    error
  };
};

// ============================================
// 2. CONSULTA DE BIRÔS DE CRÉDITO
// ============================================

interface ScoreCredito {
  score: number;
  faixa?: string;
  classificacao?: string;
  probabilidade_inadimplencia?: number;
  data_consulta: string;
}

interface RelatorioCredito {
  cpf_cnpj: string;
  nome: string;
  score?: ScoreCredito;
  restricoes: any[];
  protestos?: any[];
  cheques_sem_fundo?: any[];
  acoes_judiciais?: any[];
  resumo?: {
    protestos_quantidade: number;
    protestos_valor_total: number;
    acoes_quantidade: number;
    dividas_quantidade: number;
    consultas_ultimos_90_dias: number;
  };
}

/**
 * Hook para consulta de birôs de crédito
 */
export const useBirosCredito = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const consultarSerasaScore = async (cpf_cnpj: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/integrations/credito/serasa/score', {
        cpf_cnpj
      });
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao consultar Serasa');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const consultarSerasaRelatorio = async (cpf_cnpj: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/integrations/credito/serasa/relatorio', {
        cpf_cnpj
      });
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao consultar Serasa');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const consultarBoaVistaScore = async (cpf_cnpj: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/integrations/credito/boavista/score', {
        cpf_cnpj
      });
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao consultar Boa Vista');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const consultarBoaVistaRelatorio = async (cpf_cnpj: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/integrations/credito/boavista/relatorio', {
        cpf_cnpj
      });
      
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao consultar Boa Vista');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    consultarSerasaScore,
    consultarSerasaRelatorio,
    consultarBoaVistaScore,
    consultarBoaVistaRelatorio,
    loading,
    error
  };
};

// ============================================
// 3. COMPONENTE DE EXEMPLO
// ============================================

/**
 * Componente que demonstra uso das integrações
 */
export const ConsultaIntegrada: React.FC = () => {
  const [cpfCnpj, setCpfCnpj] = useState('');
  const [resultados, setResultados] = useState<any>(null);
  
  const tribunais = useTribunais();
  const credito = useBirosCredito();

  const handleConsultaCompleta = async () => {
    try {
      // 1. Consultar Tribunais
      const tjsp1g = await tribunais.consultarESAJ1G(cpfCnpj, 'tjsp');
      const tjsp2g = await tribunais.consultarESAJ2G(cpfCnpj, 'tjsp');
      
      // 2. Consultar Crédito
      const serasaScore = await credito.consultarSerasaScore(cpfCnpj);
      const boavistaScore = await credito.consultarBoaVistaScore(cpfCnpj);
      
      // 3. Consolidar resultados
      setResultados({
        tribunais: {
          tjsp_1g: tjsp1g,
          tjsp_2g: tjsp2g
        },
        credito: {
          serasa: serasaScore,
          boavista: boavistaScore
        }
      });
      
    } catch (err) {
      console.error('Erro na consulta:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Input */}
      <div>
        <label className="block text-sm font-medium mb-2">
          CPF/CNPJ
        </label>
        <input
          type="text"
          value={cpfCnpj}
          onChange={(e) => setCpfCnpj(e.target.value)}
          className="w-full px-4 py-2 border rounded"
          placeholder="000.000.000-00"
        />
      </div>

      {/* Botão */}
      <button
        onClick={handleConsultaCompleta}
        disabled={tribunais.loading || credito.loading}
        className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {tribunais.loading || credito.loading ? 'Consultando...' : 'Consultar'}
      </button>

      {/* Erros */}
      {(tribunais.error || credito.error) && (
        <div className="p-4 bg-red-50 border border-red-200 rounded">
          <p className="text-red-600">
            {tribunais.error || credito.error}
          </p>
        </div>
      )}

      {/* Resultados */}
      {resultados && (
        <div className="space-y-4">
          {/* Processos */}
          <div className="p-4 bg-gray-50 rounded">
            <h3 className="font-bold mb-2">📋 Processos Judiciais</h3>
            <div className="space-y-2">
              <p>
                TJSP 1ºG: {resultados.tribunais.tjsp_1g.total_processos} processos
              </p>
              <p>
                TJSP 2ºG: {resultados.tribunais.tjsp_2g.total_processos} processos
              </p>
            </div>
          </div>

          {/* Score */}
          <div className="p-4 bg-gray-50 rounded">
            <h3 className="font-bold mb-2">💳 Score de Crédito</h3>
            <div className="space-y-2">
              {resultados.credito.serasa.success && (
                <div>
                  <p className="font-medium">Serasa</p>
                  <p className="text-2xl">
                    {resultados.credito.serasa.score.score}
                  </p>
                  <p className="text-sm text-gray-600">
                    {resultados.credito.serasa.score.faixa}
                  </p>
                </div>
              )}
              
              {resultados.credito.boavista.success && (
                <div>
                  <p className="font-medium">Boa Vista</p>
                  <p className="text-2xl">
                    {resultados.credito.boavista.score.score}
                  </p>
                  <p className="text-sm text-gray-600">
                    {resultados.credito.boavista.score.classificacao}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ============================================
// 4. COMPONENTE DE SCORE
// ============================================

interface ScoreCardProps {
  score?: ScoreCredito;
  nome?: string;
  loading: boolean;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ score, nome, loading }) => {
  if (loading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-8 bg-gray-200 rounded w-1/2"></div>
      </div>
    );
  }

  if (!score) {
    return (
      <div className="p-6 bg-gray-50 rounded-lg">
        <p className="text-gray-500">Score não disponível</p>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 800) return 'text-green-600';
    if (score >= 600) return 'text-blue-600';
    if (score >= 400) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-gray-500">{nome}</span>
        <span className="text-xs text-gray-400">
          {new Date(score.data_consulta).toLocaleDateString()}
        </span>
      </div>
      
      <div className={`text-4xl font-bold ${getScoreColor(score.score)}`}>
        {score.score}
      </div>
      
      <div className="mt-2">
        <span className="text-sm text-gray-600">
          {score.faixa || score.classificacao}
        </span>
      </div>
      
      {score.probabilidade_inadimplencia !== undefined && (
        <div className="mt-4 pt-4 border-t">
          <span className="text-xs text-gray-500">
            Prob. Inadimplência: {(score.probabilidade_inadimplencia * 100).toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  );
};

// ============================================
// 5. COMPONENTE DE PROCESSOS
// ============================================

interface ProcessosListProps {
  processos: ProcessoESAJ[];
  loading: boolean;
}

export const ProcessosList: React.FC<ProcessosListProps> = ({ processos, loading }) => {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="p-4 bg-white rounded-lg shadow animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!processos || processos.length === 0) {
    return (
      <div className="p-6 bg-gray-50 rounded-lg text-center">
        <p className="text-gray-500">Nenhum processo encontrado</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {processos.map((processo, index) => (
        <div key={index} className="p-4 bg-white rounded-lg shadow hover:shadow-md transition">
          <div className="flex items-start justify-between mb-2">
            <div>
              <h4 className="font-mono text-sm text-blue-600">
                {processo.numero_processo}
              </h4>
              <p className="text-xs text-gray-500 mt-1">
                {processo.tribunal} - {processo.grau}
              </p>
            </div>
            <span className={`px-2 py-1 text-xs rounded ${
              processo.status === 'ATIVO' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            }`}>
              {processo.status}
            </span>
          </div>

          <div className="space-y-1 text-sm">
            <p><strong>Classe:</strong> {processo.classe}</p>
            <p><strong>Assunto:</strong> {processo.assunto}</p>
            <p><strong>Vara:</strong> {processo.vara}</p>
            <p><strong>Comarca:</strong> {processo.comarca}</p>
          </div>

          {processo.partes && processo.partes.length > 0 && (
            <div className="mt-3 pt-3 border-t">
              <p className="text-xs font-medium text-gray-700 mb-1">Partes:</p>
              {processo.partes.slice(0, 2).map((parte, i) => (
                <p key={i} className="text-xs text-gray-600">
                  {parte.tipo}: {parte.nome}
                </p>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

// ============================================
// 6. EXPORT
// ============================================

export default {
  useTribunais,
  useBirosCredito,
  ConsultaIntegrada,
  ScoreCard,
  ProcessosList
};
