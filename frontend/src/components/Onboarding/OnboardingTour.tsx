import { useState, useEffect } from 'react';
import type { Step, CallBackProps} from 'react-joyride';
import Joyride, { STATUS, ACTIONS, EVENTS } from 'react-joyride';

interface OnboardingTourProps {
  run?: boolean;
  onComplete?: () => void;
}

export default function OnboardingTour({ run = false, onComplete }: OnboardingTourProps) {
  const [runTour, setRunTour] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    // Verificar se o usuário já completou o tour
    const tourCompleted = localStorage.getItem('tour_completed');
    
    if (!tourCompleted && run) {
      // Aguardar 1 segundo para elementos carregarem
      const timer = setTimeout(() => {
        setRunTour(true);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [run]);

  const steps: Step[] = [
    {
      target: 'body',
      content: (
        <div className="space-y-3">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
            👋 Bem-vindo ao AgroADB!
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Vamos fazer um tour rápido pela plataforma para você conhecer as principais funcionalidades de inteligência patrimonial.
          </p>
          <div className="flex items-center gap-2 text-sm text-gray-500 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-3 border border-blue-100">
            <span className="text-blue-600">💡</span>
            <span>Você pode pular o tour a qualquer momento clicando em "Pular Tour"</span>
          </div>
        </div>
      ),
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '[data-tour="dashboard-kpis"]',
      content: (
        <div className="space-y-2">
          <h3 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">📊 KPIs do Dashboard</h3>
          <p className="text-gray-600 leading-relaxed">
            Visualize métricas importantes em tempo real: total de investigações, propriedades encontradas, 
            empresas vinculadas e dados de consultas legais (DataJud, SIGEF, INCRA).
          </p>
          <div className="bg-blue-50 rounded-lg p-2 mt-2">
            <p className="text-xs text-blue-700">
              💡 Os KPIs são atualizados automaticamente conforme suas investigações progridem
            </p>
          </div>
        </div>
      ),
      placement: 'bottom',
      disableBeacon: true,
    },
    {
      target: '[data-tour="recent-investigations"]',
      content: (
        <div className="space-y-2">
          <h3 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">🔍 Investigações Recentes</h3>
          <p className="text-gray-600 leading-relaxed">
            Acompanhe suas investigações mais recentes com informações de status, 
            propriedades e empresas encontradas. Clique em uma investigação para ver detalhes completos.
          </p>
          <div className="bg-purple-50 rounded-lg p-2 mt-2">
            <p className="text-xs text-purple-700">
              💡 Use os filtros avançados para organizar por status e período
            </p>
          </div>
        </div>
      ),
      placement: 'top',
      disableBeacon: true,
    },
    {
      target: '[data-tour="new-investigation"]',
      content: (
        <div className="space-y-2">
          <h3 className="text-lg font-bold bg-gradient-to-r from-emerald-600 to-blue-600 bg-clip-text text-transparent">➕ Nova Investigação</h3>
          <p className="text-gray-600 leading-relaxed">
            Clique aqui para criar uma nova investigação. Você pode buscar por CPF, 
            CNPJ ou nome da pessoa/empresa que deseja investigar.
          </p>
          <div className="grid grid-cols-2 gap-2 mt-2">
            <div className="bg-blue-50 rounded-lg p-2">
              <p className="text-xs font-semibold text-blue-900">🔍 Busca Completa</p>
              <p className="text-[10px] text-blue-700">Investigação detalhada em múltiplas bases</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-2">
              <p className="text-xs font-semibold text-purple-900">⚡ Quick Scan</p>
              <p className="text-[10px] text-purple-700">Resultados rápidos e instantâneos</p>
            </div>
          </div>
        </div>
      ),
      placement: 'bottom',
      disableBeacon: true,
    },
    {
      target: '[data-tour="sidebar-investigations"]',
      content: (
        <div className="space-y-2">
          <h3 className="text-lg font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">📋 Todas as Investigações</h3>
          <p className="text-gray-600 leading-relaxed">
            Acesse a lista completa de suas investigações com filtros avançados 
            por status (pendente, em andamento, concluída) e período.
          </p>
          <div className="bg-indigo-50 rounded-lg p-2 mt-2">
            <p className="text-xs text-indigo-700">
              💡 Use a busca para encontrar investigações rapidamente por nome ou documento
            </p>
          </div>
        </div>
      ),
      placement: 'right',
      disableBeacon: true,
    },
    {
      target: '[data-tour="sidebar-settings"]',
      content: (
        <div className="space-y-2">
          <h3 className="text-lg font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">⚙️ Integrações e APIs</h3>
          <p className="text-gray-600 leading-relaxed">
            Configure integrações com APIs governamentais como Portal da Transparência, 
            SIGEF, DataJud, INCRA, Receita Federal e muito mais para enriquecer suas investigações.
          </p>
          <div className="bg-purple-50 rounded-lg p-2 mt-2">
            <p className="text-xs text-purple-700">
              🔐 Gerencie tokens de API e configure webhooks para automações
            </p>
          </div>
        </div>
      ),
      placement: 'right',
      disableBeacon: true,
    },
    {
      target: '[data-tour="sidebar-user-guide"]',
      content: (
        <div className="space-y-2">
          <h3 className="text-lg font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">📖 Manual do utilizador</h3>
          <p className="text-gray-600 leading-relaxed">
            Aceda à documentação de produto: fluxos da plataforma, boas práticas e ajuda contextual. Está separada da
            documentação técnica para programadores.
          </p>
          <div className="bg-emerald-50 rounded-lg p-2 mt-2">
            <p className="text-xs text-emerald-800">
              O conteúdo em Markdown mantém-se em <code className="font-mono text-[10px]">product/</code> no repositório.
            </p>
          </div>
        </div>
      ),
      placement: 'right',
      disableBeacon: true,
    },
    {
      target: '[data-tour="notifications"]',
      content: (
        <div className="space-y-2">
          <h3 className="text-lg font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">🔔 Notificações em Tempo Real</h3>
          <p className="text-gray-600 leading-relaxed">
            Receba alertas em tempo real sobre o progresso das suas investigações, 
            quando novos dados forem encontrados ou quando uma investigação for concluída.
          </p>
          <div className="bg-amber-50 rounded-lg p-2 mt-2">
            <p className="text-xs text-amber-700">
              💡 Configure notificações por email e webhooks nas configurações
            </p>
          </div>
        </div>
      ),
      placement: 'bottom',
      disableBeacon: true,
    },
    {
      target: '[data-tour="user-menu"]',
      content: (
        <div className="space-y-2">
          <h3 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">👤 Menu do Usuário</h3>
          <p className="text-gray-600 leading-relaxed">
            Acesse seu perfil, altere preferências, gerencie sua conta e 
            reinicie este tour a qualquer momento clicando em "Tour Guiado".
          </p>
          <div className="bg-blue-50 rounded-lg p-2 mt-2">
            <p className="text-xs text-blue-700">
              🔐 Configure autenticação de dois fatores e gerencie suas sessões
            </p>
          </div>
        </div>
      ),
      placement: 'bottom',
      disableBeacon: true,
    },
    {
      target: 'body',
      content: (
        <div className="space-y-3">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 via-blue-600 to-purple-600 bg-clip-text text-transparent">
            ✅ Tour Concluído!
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Você está pronto para começar! Explore as funcionalidades e crie sua primeira investigação.
          </p>
          <div className="grid grid-cols-2 gap-3 mt-4">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
              <div className="font-semibold text-blue-900 text-sm mb-1">🔍 Quick Scan</div>
              <div className="text-xs text-blue-700">
                Investigações rápidas com resultados instantâneos de múltiplas bases
              </div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200">
              <div className="font-semibold text-purple-900 text-sm mb-1">📄 Exportação</div>
              <div className="text-xs text-purple-700">
                Gere relatórios profissionais em PDF ou Excel com um clique
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 mt-3">
            <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-3 border border-emerald-200">
              <div className="font-semibold text-emerald-900 text-sm mb-1">🗺️ Mapas Interativos</div>
              <div className="text-xs text-emerald-700">
                Visualize propriedades rurais em mapa com coordenadas SIGEF
              </div>
            </div>
            <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg p-3 border border-amber-200">
              <div className="font-semibold text-amber-900 text-sm mb-1">⚖️ Consultas Legais</div>
              <div className="text-xs text-amber-700">
                DataJud, SIGEF, BNMP e outros sistemas jurídicos integrados
              </div>
            </div>
          </div>
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-3 mt-3 border border-blue-200">
            <p className="text-sm text-gray-700 font-medium">
              💡 Dica: Você pode reiniciar este tour a qualquer momento através do menu do usuário → Tour Guiado
            </p>
          </div>
        </div>
      ),
      placement: 'center',
      disableBeacon: true,
    },
  ];

  const handleJoyrideCallback = (data: CallBackProps) => {
    const { status, action, index, type } = data;

    if (([STATUS.FINISHED, STATUS.SKIPPED] as string[]).includes(status)) {
      // Tour finalizado ou pulado
      setRunTour(false);
      setStepIndex(0);
      localStorage.setItem('tour_completed', 'true');
      
      if (onComplete) {
        onComplete();
      }
    } else if (type === EVENTS.STEP_AFTER || type === EVENTS.TARGET_NOT_FOUND) {
      // Avançar para o próximo step
      setStepIndex(index + (action === ACTIONS.PREV ? -1 : 1));
    }
  };

  return (
    <Joyride
      steps={steps}
      run={runTour}
      stepIndex={stepIndex}
      continuous
      showProgress
      showSkipButton
      scrollToFirstStep
      disableScrolling={false}
      callback={handleJoyrideCallback}
      styles={{
        options: {
          primaryColor: '#3b82f6',
          textColor: '#374151',
          backgroundColor: '#ffffff',
          arrowColor: '#ffffff',
          overlayColor: 'rgba(0, 0, 0, 0.65)',
          zIndex: 10000,
        },
        tooltip: {
          borderRadius: 16,
          padding: 24,
          fontSize: 14,
          boxShadow: '0 20px 25px -5px rgba(59, 130, 246, 0.15), 0 10px 10px -5px rgba(139, 92, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.1)',
        },
        tooltipContainer: {
          textAlign: 'left',
        },
        tooltipTitle: {
          fontSize: 18,
          fontWeight: 700,
          marginBottom: 8,
        },
        tooltipContent: {
          padding: '12px 0',
        },
        buttonNext: {
          background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
          borderRadius: 10,
          fontSize: 14,
          fontWeight: 600,
          padding: '12px 24px',
          outline: 'none',
          boxShadow: '0 4px 12px -2px rgba(59, 130, 246, 0.4)',
        },
        buttonBack: {
          color: '#6b7280',
          fontSize: 14,
          fontWeight: 600,
          marginRight: 12,
          padding: '8px 16px',
          borderRadius: 8,
        },
        buttonSkip: {
          color: '#9ca3af',
          fontSize: 13,
          fontWeight: 600,
          padding: '8px 16px',
        },
        buttonClose: {
          display: 'none',
        },
        spotlight: {
          borderRadius: 12,
          boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.65), 0 0 20px rgba(59, 130, 246, 0.6)',
        },
        beacon: {
          width: 36,
          height: 36,
        },
        beaconInner: {
          backgroundColor: '#3b82f6',
        },
        beaconOuter: {
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          border: '2px solid #3b82f6',
        },
      }}
      locale={{
        back: 'Voltar',
        close: 'Fechar',
        last: 'Finalizar',
        next: 'Próximo',
        skip: 'Pular Tour',
      }}
    />
  );
}
