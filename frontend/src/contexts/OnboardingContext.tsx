/**
 * Onboarding Context - Sistema de Onboarding para Novos Usuários
 * 
 * Gerencia o fluxo de onboarding e tour guiado
 */
import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';

// Tipos
export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  target?: string; // Seletor CSS do elemento alvo
  position?: 'top' | 'bottom' | 'left' | 'right';
  action?: () => void;
  canSkip?: boolean;
}

export interface OnboardingFlow {
  id: string;
  name: string;
  steps: OnboardingStep[];
}

interface OnboardingContextType {
  isOnboardingActive: boolean;
  currentFlow: OnboardingFlow | null;
  currentStepIndex: number;
  currentStep: OnboardingStep | null;
  hasCompletedOnboarding: boolean;
  startOnboarding: (flowId: string) => void;
  nextStep: () => void;
  previousStep: () => void;
  skipOnboarding: () => void;
  completeOnboarding: () => void;
  resetOnboarding: () => void;
}

// Fluxos de onboarding predefinidos
const onboardingFlows: Record<string, OnboardingFlow> = {
  'first-time': {
    id: 'first-time',
    name: 'Primeiros Passos',
    steps: [
      {
        id: 'welcome',
        title: '🎉 Bem-vindo ao AgroADB!',
        description: 'Vamos fazer um tour rápido pela plataforma para você conhecer as principais funcionalidades.',
        canSkip: true
      },
      {
        id: 'dashboard',
        title: '📊 Dashboard',
        description: 'Aqui você vê um resumo de todas as suas investigações ativas e recentes.',
        target: '[data-tour="dashboard"]',
        position: 'bottom'
      },
      {
        id: 'create-investigation',
        title: '🔍 Nova Investigação',
        description: 'Clique aqui para criar uma nova investigação. Você pode buscar por CPF, CNPJ ou nome.',
        target: '[data-tour="create-investigation"]',
        position: 'bottom'
      },
      {
        id: 'notifications',
        title: '🔔 Notificações',
        description: 'Receba alertas em tempo real sobre o progresso das suas investigações.',
        target: '[data-tour="notifications"]',
        position: 'left'
      },
      {
        id: 'profile',
        title: '👤 Perfil',
        description: 'Configure suas preferências, segurança e webhooks aqui.',
        target: '[data-tour="profile"]',
        position: 'left'
      },
      {
        id: 'complete',
        title: '✅ Pronto!',
        description: 'Você está pronto para começar. Crie sua primeira investigação e explore todas as funcionalidades!',
        canSkip: false
      }
    ]
  },
  'investigation-details': {
    id: 'investigation-details',
    name: 'Detalhes da Investigação',
    steps: [
      {
        id: 'overview',
        title: '📋 Visão Geral',
        description: 'Veja informações principais e progresso da investigação.',
        target: '[data-tour="investigation-overview"]',
        position: 'top'
      },
      {
        id: 'results',
        title: '📊 Resultados',
        description: 'Navegue pelos resultados de cada scraper (CAR, INCRA, Receita, etc).',
        target: '[data-tour="investigation-results"]',
        position: 'top'
      },
      {
        id: 'export',
        title: '📄 Exportar',
        description: 'Gere relatórios profissionais em PDF ou Excel.',
        target: '[data-tour="export-button"]',
        position: 'left'
      },
      {
        id: 'map',
        title: '🗺️ Mapa',
        description: 'Visualize propriedades rurais no mapa interativo.',
        target: '[data-tour="map-view"]',
        position: 'top'
      }
    ]
  }
};

// Context
const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined);

// Provider
export function OnboardingProvider({ children }: { children: ReactNode }) {
  const [isOnboardingActive, setIsOnboardingActive] = useState(false);
  const [currentFlow, setCurrentFlow] = useState<OnboardingFlow | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(() => {
    return localStorage.getItem('agroadb-onboarding-completed') === 'true';
  });

  // Iniciar onboarding automaticamente para novos usuários
  useEffect(() => {
    if (!hasCompletedOnboarding && !isOnboardingActive) {
      // Aguardar 1 segundo para a página carregar
      const timer = setTimeout(() => {
        startOnboarding('first-time');
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [hasCompletedOnboarding]);

  const startOnboarding = (flowId: string) => {
    const flow = onboardingFlows[flowId];
    if (flow) {
      setCurrentFlow(flow);
      setCurrentStepIndex(0);
      setIsOnboardingActive(true);
    }
  };

  const nextStep = () => {
    if (!currentFlow) return;
    
    if (currentStepIndex < currentFlow.steps.length - 1) {
      setCurrentStepIndex(prev => prev + 1);
    } else {
      completeOnboarding();
    }
  };

  const previousStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1);
    }
  };

  const skipOnboarding = () => {
    setIsOnboardingActive(false);
    setCurrentFlow(null);
    setCurrentStepIndex(0);
  };

  const completeOnboarding = () => {
    setIsOnboardingActive(false);
    setCurrentFlow(null);
    setCurrentStepIndex(0);
    setHasCompletedOnboarding(true);
    localStorage.setItem('agroadb-onboarding-completed', 'true');
  };

  const resetOnboarding = () => {
    setHasCompletedOnboarding(false);
    localStorage.removeItem('agroadb-onboarding-completed');
  };

  const currentStep = currentFlow?.steps[currentStepIndex] || null;

  return (
    <OnboardingContext.Provider
      value={{
        isOnboardingActive,
        currentFlow,
        currentStepIndex,
        currentStep,
        hasCompletedOnboarding,
        startOnboarding,
        nextStep,
        previousStep,
        skipOnboarding,
        completeOnboarding,
        resetOnboarding
      }}
    >
      {children}
    </OnboardingContext.Provider>
  );
}

// Hook
export function useOnboarding() {
  const context = useContext(OnboardingContext);
  if (!context) {
    throw new Error('useOnboarding must be used within OnboardingProvider');
  }
  return context;
}
