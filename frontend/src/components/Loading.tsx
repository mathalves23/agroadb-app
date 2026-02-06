/**
 * Loading States - Estados de Carregamento Informativos
 * 
 * Componentes de loading com feedback visual e mensagens contextuais
 */
import React from 'react';
import { motion } from 'framer-motion';

// Tipos de loading
export type LoadingType = 'spinner' | 'skeleton' | 'dots' | 'progress' | 'pulse';

interface LoadingProps {
  type?: LoadingType;
  message?: string;
  progress?: number; // 0-100
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
}

export function Loading({
  type = 'spinner',
  message,
  progress,
  size = 'md',
  fullScreen = false
}: LoadingProps) {
  const containerClasses = fullScreen
    ? 'fixed inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-50'
    : 'flex items-center justify-center p-8';

  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  return (
    <div className={containerClasses}>
      <div className="flex flex-col items-center gap-4">
        {/* Loading Visual */}
        {type === 'spinner' && (
          <motion.div
            className={`${sizeClasses[size]} border-4 border-gray-200 dark:border-gray-700 border-t-green-600 rounded-full`}
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          />
        )}

        {type === 'dots' && (
          <div className="flex gap-2">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className={`${size === 'sm' ? 'w-2 h-2' : size === 'md' ? 'w-3 h-3' : 'w-4 h-4'} bg-green-600 rounded-full`}
                animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.2
                }}
              />
            ))}
          </div>
        )}

        {type === 'pulse' && (
          <motion.div
            className={`${sizeClasses[size]} bg-green-600 rounded-full`}
            animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}

        {type === 'progress' && progress !== undefined && (
          <div className="w-64">
            <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-green-600"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
            <p className="text-center text-sm text-gray-600 dark:text-gray-400 mt-2">
              {Math.round(progress)}%
            </p>
          </div>
        )}

        {/* Message */}
        {message && (
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-gray-700 dark:text-gray-300 text-center max-w-md"
          >
            {message}
          </motion.p>
        )}
      </div>
    </div>
  );
}

// Skeleton Loading para listas
interface SkeletonProps {
  count?: number;
  className?: string;
}

export function Skeleton({ count = 1, className = '' }: SkeletonProps) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded ${className}`}
        />
      ))}
    </>
  );
}

// Skeleton para cards
export function SkeletonCard() {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-4">
      <Skeleton className="h-6 w-3/4" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <div className="flex gap-2">
        <Skeleton className="h-8 w-20" />
        <Skeleton className="h-8 w-20" />
      </div>
    </div>
  );
}

// Loading para tabelas
export function TableSkeleton({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} className="h-12 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

// Loading específico para investigação
export function InvestigationLoading({ stage }: { stage?: string }) {
  const stages = [
    { name: 'CAR', icon: '🌳' },
    { name: 'INCRA', icon: '📋' },
    { name: 'Receita Federal', icon: '🏛️' },
    { name: 'Diários Oficiais', icon: '📰' },
    { name: 'Cartórios', icon: '📜' },
    { name: 'SIGEF/SICAR', icon: '🗺️' }
  ];

  return (
    <div className="space-y-4">
      <div className="text-center">
        <Loading type="spinner" size="lg" />
        <h3 className="text-xl font-bold mt-4 text-gray-900 dark:text-white">
          Processando Investigação
        </h3>
        {stage && (
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Buscando dados em: {stage}
          </p>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-8">
        {stages.map((s) => (
          <motion.div
            key={s.name}
            className={`p-4 rounded-lg border-2 ${
              s.name === stage
                ? 'border-green-600 bg-green-50 dark:bg-green-900/20'
                : 'border-gray-200 dark:border-gray-700'
            }`}
            animate={s.name === stage ? { scale: [1, 1.05, 1] } : {}}
            transition={{ duration: 1, repeat: Infinity }}
          >
            <div className="text-3xl text-center mb-2">{s.icon}</div>
            <div className="text-sm text-center font-medium text-gray-700 dark:text-gray-300">
              {s.name}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
