import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { designSystem } from '@/lib/design-system';
import React from 'react';

// ==================== CARD VARIANTS ====================

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'elevated' | 'flat' | 'outlined' | 'glass';
  hover?: boolean;
  children: React.ReactNode;
}

export const Card = ({ 
  variant = 'elevated', 
  hover = true, 
  className, 
  children, 
  ...props 
}: CardProps) => {
  const variants = {
    elevated: 'bg-white dark:bg-gray-900 shadow-lg border border-gray-200 dark:border-gray-800',
    flat: 'bg-gray-50 dark:bg-gray-800',
    outlined: 'bg-transparent border-2 border-gray-200 dark:border-gray-700',
    glass: 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-white/20 dark:border-gray-800/20',
  };

  return (
    <motion.div
      className={cn(
        'rounded-xl p-6 transition-all duration-300',
        variants[variant],
        hover && 'hover:shadow-2xl hover:scale-[1.02] cursor-pointer',
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      {...props}
    >
      {children}
    </motion.div>
  );
};

// ==================== STATS CARD ====================

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    type: 'increase' | 'decrease';
  };
  icon?: React.ReactNode;
  trend?: number[];
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
}

export const StatsCard = ({ 
  title, 
  value, 
  change, 
  icon, 
  trend,
  color = 'primary' 
}: StatsCardProps) => {
  const colors = {
    primary: 'from-green-500 to-emerald-600',
    secondary: 'from-blue-500 to-indigo-600',
    success: 'from-green-500 to-teal-600',
    warning: 'from-amber-500 to-orange-600',
    error: 'from-red-500 to-rose-600',
  };

  return (
    <Card variant="glass" className="relative overflow-hidden group">
      {/* Background Gradient */}
      <div className={cn(
        "absolute inset-0 bg-gradient-to-br opacity-5 group-hover:opacity-10 transition-opacity",
        colors[color]
      )} />
      
      <div className="relative">
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              {title}
            </p>
            <h3 className="text-3xl font-bold text-gray-900 dark:text-white">
              {value}
            </h3>
          </div>
          
          {icon && (
            <div className={cn(
              "p-3 rounded-xl bg-gradient-to-br shadow-lg",
              colors[color]
            )}>
              <div className="text-white">
                {icon}
              </div>
            </div>
          )}
        </div>

        {change && (
          <div className="flex items-center gap-2">
            <span className={cn(
              "flex items-center gap-1 text-sm font-semibold",
              change.type === 'increase' ? 'text-green-600' : 'text-red-600'
            )}>
              {change.type === 'increase' ? '↗' : '↘'}
              {Math.abs(change.value)}%
            </span>
            <span className="text-xs text-gray-500">vs. último mês</span>
          </div>
        )}

        {trend && (
          <div className="mt-4 h-12">
            {/* Mini sparkline aqui */}
            <svg className="w-full h-full" viewBox="0 0 100 30">
              <path
                d={`M 0 ${30 - trend[0]} ${trend.map((v, i) => `L ${(i / (trend.length - 1)) * 100} ${30 - v}`).join(' ')}`}
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                className="text-green-500 opacity-50"
              />
            </svg>
          </div>
        )}
      </div>
    </Card>
  );
};

// ==================== METRIC CARD ====================

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  color?: string;
  suffix?: string;
}

export const MetricCard = ({ 
  label, 
  value, 
  icon, 
  color = 'bg-blue-500',
  suffix 
}: MetricCardProps) => {
  return (
    <div className="flex items-center gap-4 p-4 bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 hover:shadow-lg transition-all duration-300">
      <div className={cn("p-3 rounded-lg", color)}>
        <div className="text-white w-6 h-6">
          {icon}
        </div>
      </div>
      <div className="flex-1">
        <p className="text-sm text-gray-600 dark:text-gray-400">{label}</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">
          {value}{suffix && <span className="text-sm text-gray-500 ml-1">{suffix}</span>}
        </p>
      </div>
    </div>
  );
};

// ==================== FEATURE CARD ====================

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const FeatureCard = ({ icon, title, description, action }: FeatureCardProps) => {
  return (
    <motion.div
      className="group p-6 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 hover:border-green-500 dark:hover:border-green-500 transition-all duration-300 hover:shadow-2xl"
      whileHover={{ y: -5 }}
    >
      <div className="flex flex-col h-full">
        <div className="mb-4 p-4 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 w-fit">
          <div className="text-white w-6 h-6">
            {icon}
          </div>
        </div>
        
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 group-hover:text-green-600 transition-colors">
          {title}
        </h3>
        
        <p className="text-gray-600 dark:text-gray-400 mb-4 flex-1">
          {description}
        </p>

        {action && (
          <button
            onClick={action.onClick}
            className="mt-auto text-green-600 dark:text-green-500 font-semibold hover:gap-2 flex items-center gap-1 transition-all group-hover:translate-x-1"
          >
            {action.label}
            <span>→</span>
          </button>
        )}
      </div>
    </motion.div>
  );
};

// ==================== ALERT CARD ====================

interface AlertCardProps {
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  onClose?: () => void;
}

export const AlertCard = ({ type, title, message, onClose }: AlertCardProps) => {
  const styles = {
    info: {
      bg: 'bg-blue-50 dark:bg-blue-950/30',
      border: 'border-blue-200 dark:border-blue-800',
      icon: 'text-blue-600',
      title: 'text-blue-900 dark:text-blue-100',
    },
    success: {
      bg: 'bg-green-50 dark:bg-green-950/30',
      border: 'border-green-200 dark:border-green-800',
      icon: 'text-green-600',
      title: 'text-green-900 dark:text-green-100',
    },
    warning: {
      bg: 'bg-amber-50 dark:bg-amber-950/30',
      border: 'border-amber-200 dark:border-amber-800',
      icon: 'text-amber-600',
      title: 'text-amber-900 dark:text-amber-100',
    },
    error: {
      bg: 'bg-red-50 dark:bg-red-950/30',
      border: 'border-red-200 dark:border-red-800',
      icon: 'text-red-600',
      title: 'text-red-900 dark:text-red-100',
    },
  };

  const style = styles[type];

  return (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 50 }}
      className={cn(
        "p-4 rounded-xl border-l-4 relative",
        style.bg,
        style.border
      )}
    >
      <div className="flex gap-3">
        <div className={cn("mt-0.5", style.icon)}>
          {type === 'info' && '📘'}
          {type === 'success' && '✅'}
          {type === 'warning' && '⚠️'}
          {type === 'error' && '❌'}
        </div>
        <div className="flex-1">
          <h4 className={cn("font-semibold mb-1", style.title)}>
            {title}
          </h4>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {message}
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            ✕
          </button>
        )}
      </div>
    </motion.div>
  );
};

// ==================== TIMELINE CARD ====================

interface TimelineItem {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  icon?: React.ReactNode;
  type?: 'info' | 'success' | 'warning' | 'error';
}

interface TimelineCardProps {
  items: TimelineItem[];
}

export const TimelineCard = ({ items }: TimelineCardProps) => {
  const typeColors = {
    info: 'bg-blue-500',
    success: 'bg-green-500',
    warning: 'bg-amber-500',
    error: 'bg-red-500',
  };

  return (
    <Card>
      <div className="space-y-6">
        {items.map((item, index) => (
          <div key={item.id} className="relative flex gap-4">
            {/* Timeline line */}
            {index !== items.length - 1 && (
              <div className="absolute left-4 top-10 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" />
            )}
            
            {/* Icon */}
            <div className={cn(
              "relative z-10 flex items-center justify-center w-8 h-8 rounded-full",
              typeColors[item.type || 'info']
            )}>
              {item.icon || '📍'}
            </div>

            {/* Content */}
            <div className="flex-1 pb-6">
              <div className="flex items-start justify-between mb-1">
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  {item.title}
                </h4>
                <span className="text-xs text-gray-500">
                  {item.timestamp}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {item.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

// ==================== EMPTY STATE ====================

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export const EmptyState = ({ icon, title, description, action }: EmptyStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      {icon && (
        <div className="mb-4 text-6xl opacity-20">
          {icon}
        </div>
      )}
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        {title}
      </h3>
      <p className="text-gray-600 dark:text-gray-400 text-center max-w-md mb-6">
        {description}
      </p>
      {action && (
        <button
          onClick={action.onClick}
          className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all duration-300 hover:scale-105"
        >
          {action.label}
        </button>
      )}
    </div>
  );
};
