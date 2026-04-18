import { createContext } from 'react'

export interface OnboardingStep {
  id: string
  title: string
  description: string
  target?: string
  position?: 'top' | 'bottom' | 'left' | 'right'
  action?: () => void
  canSkip?: boolean
}

export interface OnboardingFlow {
  id: string
  name: string
  steps: OnboardingStep[]
}

export interface OnboardingContextType {
  isOnboardingActive: boolean
  currentFlow: OnboardingFlow | null
  currentStepIndex: number
  currentStep: OnboardingStep | null
  hasCompletedOnboarding: boolean
  startOnboarding: (flowId: string) => void
  nextStep: () => void
  previousStep: () => void
  skipOnboarding: () => void
  completeOnboarding: () => void
  resetOnboarding: () => void
}

export const OnboardingContext = createContext<OnboardingContextType | undefined>(undefined)
