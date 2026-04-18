import { driver, type DriveStep, type Driver } from 'driver.js'
import 'driver.js/dist/driver.css';

export class OnboardingService {
  private static driver: Driver | null = null;

  static start(): void {
    const hasSeenOnboarding = localStorage.getItem('onboarding_completed');
    
    if (hasSeenOnboarding) {
      return;
    }

    this.startTour();
  }

  static startTour(): void {
    if (this.driver) {
      this.driver.destroy();
    }

    const steps: DriveStep[] = [
      {
        element: '#dashboard-link',
        popover: {
          title: '👋 Bem-vindo ao AgroADB!',
          description: 'Vamos fazer um tour rápido de 5 minutos para você conhecer a plataforma. Você pode pular a qualquer momento.',
          side: 'bottom',
          align: 'start'
        }
      },
      {
        element: '#new-investigation-btn',
        popover: {
          title: '🔍 Criar Investigação',
          description: 'Comece criando uma nova investigação. Você pode investigar pessoas físicas (CPF) ou jurídicas (CNPJ) para descobrir propriedades rurais, empresas e contratos.',
          side: 'bottom',
          align: 'start'
        }
      },
      {
        element: '#investigations-list',
        popover: {
          title: '📋 Suas Investigações',
          description: 'Aqui você vê todas as suas investigações. Filtre por status (Pendente, Em Andamento, Concluída) e prioridade.',
          side: 'top',
          align: 'start'
        }
      },
      {
        element: '#dashboard-stats',
        popover: {
          title: '📊 Dashboard',
          description: 'Acompanhe estatísticas importantes: quantas propriedades foram encontradas, empresas vinculadas, contratos identificados e muito mais.',
          side: 'bottom',
          align: 'start'
        }
      },
      {
        element: '#integrations-btn',
        popover: {
          title: '🔌 Configurar Integrações',
          description: 'Configure as chaves de API para acessar dados do Portal da Transparência, TJMG, SIGEF e outras fontes governamentais.',
          side: 'left',
          align: 'start'
        }
      },
      {
        element: '#export-buttons',
        popover: {
          title: '📄 Exportar Relatórios',
          description: 'Exporte suas investigações em PDF profissional ou Excel com todos os dados organizados em abas.',
          side: 'top',
          align: 'start'
        }
      },
      {
        element: '#share-btn',
        popover: {
          title: '🤝 Compartilhar',
          description: 'Compartilhe investigações com outros usuários da equipe. Defina permissões (visualizar, editar, admin) para cada pessoa.',
          side: 'left',
          align: 'start'
        }
      },
      {
        element: '#comments-section',
        popover: {
          title: '💬 Comentários e Anotações',
          description: 'Adicione comentários compartilhados com a equipe ou anotações privadas (apenas você verá). Ótimo para registrar insights e descobertas.',
          side: 'top',
          align: 'start'
        }
      },
      {
        element: '#notification-bell',
        popover: {
          title: '🔔 Notificações',
          description: 'Receba notificações quando relatórios ficarem prontos, alguém comentar ou compartilhar uma investigação com você.',
          side: 'bottom',
          align: 'end'
        }
      },
      {
        element: '#user-menu',
        popover: {
          title: '⚙️ Perfil e Configurações',
          description: 'Acesse seu perfil, configure notificações por email, altere senha e gerencie suas preferências.',
          side: 'bottom',
          align: 'end'
        }
      },
      {
        popover: {
          title: '🎉 Tudo Pronto!',
          description: 'Você está pronto para começar! Se precisar rever este tour, acesse em Ajuda > Tour Guiado. Boa investigação!',
          side: 'top',
          align: 'center'
        }
      }
    ];

    this.driver = driver({
      showProgress: true,
      steps: steps,
      nextBtnText: 'Próximo →',
      prevBtnText: '← Anterior',
      doneBtnText: 'Concluir ✓',
      progressText: 'Passo {{current}} de {{total}}',
      onDestroyStarted: () => {
        if (this.driver?.hasNextStep()) {
          // User is skipping
          const dontShowAgain = confirm(
            'Deseja pular o tour?\n\nVocê pode reativá-lo depois em: Menu → Ajuda → Tour Guiado'
          );
          if (dontShowAgain) {
            this.driver?.destroy();
            localStorage.setItem('onboarding_completed', 'true');
          }
        } else {
          // Tour completed
          this.driver?.destroy();
          localStorage.setItem('onboarding_completed', 'true');
        }
      },
      onDestroyed: () => {
        this.driver = null;
      }
    });

    this.driver.drive();
  }

  static reset(): void {
    localStorage.removeItem('onboarding_completed');
  }

  static isCompleted(): boolean {
    return localStorage.getItem('onboarding_completed') === 'true';
  }
}

// CSS personalizado para o tour
export const onboardingStyles = `
.driver-popover {
  background: white !important;
  border-radius: 12px !important;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15) !important;
}

.driver-popover-title {
  font-size: 18px !important;
  font-weight: 700 !important;
  color: #1f2937 !important;
}

.driver-popover-description {
  font-size: 14px !important;
  line-height: 1.6 !important;
  color: #4b5563 !important;
}

.driver-popover-progress-text {
  font-size: 12px !important;
  color: #6366f1 !important;
  font-weight: 600 !important;
}

.driver-popover-next-btn,
.driver-popover-prev-btn {
  background: #6366f1 !important;
  color: white !important;
  border: none !important;
  padding: 8px 16px !important;
  border-radius: 6px !important;
  font-weight: 600 !important;
  transition: all 0.2s !important;
}

.driver-popover-next-btn:hover,
.driver-popover-prev-btn:hover {
  background: #4f46e5 !important;
  transform: translateY(-1px) !important;
}

.driver-popover-prev-btn {
  background: #e5e7eb !important;
  color: #374151 !important;
}

.driver-popover-prev-btn:hover {
  background: #d1d5db !important;
}

.driver-popover-close-btn {
  color: #9ca3af !important;
}

.driver-popover-close-btn:hover {
  color: #ef4444 !important;
}
`;
