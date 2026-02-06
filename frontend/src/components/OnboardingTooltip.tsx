/**
 * Onboarding Tooltip Component
 * 
 * Exibe tooltips guiados durante o onboarding
 */
import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useOnboarding } from '../contexts/OnboardingContext';

export function OnboardingTooltip() {
  const {
    isOnboardingActive,
    currentStep,
    currentStepIndex,
    currentFlow,
    nextStep,
    previousStep,
    skipOnboarding
  } = useOnboarding();

  const [position, setPosition] = useState({ top: 0, left: 0 });
  const [tooltipPosition, setTooltipPosition] = useState<'top' | 'bottom' | 'left' | 'right'>('bottom');
  const tooltipRef = useRef<HTMLDivElement>(null);

  // Calcular posição do tooltip
  useEffect(() => {
    if (!currentStep?.target || !isOnboardingActive) return;

    const updatePosition = () => {
      const targetElement = document.querySelector(currentStep.target!);
      if (!targetElement || !tooltipRef.current) return;

      const targetRect = targetElement.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      const padding = 20;

      let top = 0;
      let left = 0;
      let position = currentStep.position || 'bottom';

      switch (position) {
        case 'top':
          top = targetRect.top - tooltipRect.height - padding;
          left = targetRect.left + (targetRect.width - tooltipRect.width) / 2;
          break;
        case 'bottom':
          top = targetRect.bottom + padding;
          left = targetRect.left + (targetRect.width - tooltipRect.width) / 2;
          break;
        case 'left':
          top = targetRect.top + (targetRect.height - tooltipRect.height) / 2;
          left = targetRect.left - tooltipRect.width - padding;
          break;
        case 'right':
          top = targetRect.top + (targetRect.height - tooltipRect.height) / 2;
          left = targetRect.right + padding;
          break;
      }

      // Ajustar se sair da tela
      const maxLeft = window.innerWidth - tooltipRect.width - padding;
      const maxTop = window.innerHeight - tooltipRect.height - padding;
      
      left = Math.max(padding, Math.min(left, maxLeft));
      top = Math.max(padding, Math.min(top, maxTop));

      setPosition({ top, left });
      setTooltipPosition(position);

      // Highlight do elemento alvo
      targetElement.classList.add('onboarding-highlight');
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition);

    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition);
      
      // Remover highlight
      const targetElement = document.querySelector(currentStep.target!);
      if (targetElement) {
        targetElement.classList.remove('onboarding-highlight');
      }
    };
  }, [currentStep, isOnboardingActive]);

  if (!isOnboardingActive || !currentStep) return null;

  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === (currentFlow?.steps.length || 0) - 1;
  const totalSteps = currentFlow?.steps.length || 0;

  return (
    <>
      {/* Overlay */}
      <AnimatePresence>
        {currentStep.target && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-[9998]"
            onClick={skipOnboarding}
          />
        )}
      </AnimatePresence>

      {/* Tooltip */}
      <motion.div
        ref={tooltipRef}
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        style={{
          position: 'fixed',
          top: currentStep.target ? position.top : '50%',
          left: currentStep.target ? position.left : '50%',
          transform: !currentStep.target ? 'translate(-50%, -50%)' : 'none',
          zIndex: 9999
        }}
        className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-6 max-w-md border border-gray-200 dark:border-gray-700"
      >
        {/* Progress */}
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Passo {currentStepIndex + 1} de {totalSteps}
          </span>
          {currentStep.canSkip !== false && (
            <button
              onClick={skipOnboarding}
              className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              Pular tour
            </button>
          )}
        </div>

        {/* Progress Bar */}
        <div className="h-1 bg-gray-200 dark:bg-gray-700 rounded-full mb-4">
          <motion.div
            className="h-full bg-green-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${((currentStepIndex + 1) / totalSteps) * 100}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>

        {/* Content */}
        <h3 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">
          {currentStep.title}
        </h3>
        <p className="text-gray-600 dark:text-gray-300 mb-6">
          {currentStep.description}
        </p>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <button
            onClick={previousStep}
            disabled={isFirstStep}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            Anterior
          </button>

          <button
            onClick={nextStep}
            className="px-6 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
          >
            {isLastStep ? 'Concluir' : 'Próximo'}
          </button>
        </div>
      </motion.div>

      {/* CSS para highlight */}
      <style>{`
        .onboarding-highlight {
          position: relative;
          z-index: 9999;
          box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.5);
          border-radius: 8px;
          animation: pulse-highlight 2s infinite;
        }

        @keyframes pulse-highlight {
          0%, 100% {
            box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.5);
          }
          50% {
            box-shadow: 0 0 0 8px rgba(34, 197, 94, 0.3);
          }
        }
      `}</style>
    </>
  );
}
