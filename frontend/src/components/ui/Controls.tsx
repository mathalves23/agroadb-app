import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

// ==================== BUTTON ====================

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'solid' | 'outline' | 'ghost' | 'soft' | 'gradient';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

export const Button = ({
  variant = 'solid',
  size = 'md',
  color = 'primary',
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  className,
  children,
  disabled,
  ...props
}: ButtonProps) => {
  const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const sizes = {
    xs: 'h-8 px-3 text-xs gap-1.5',
    sm: 'h-9 px-4 text-sm gap-2',
    md: 'h-10 px-5 text-sm gap-2',
    lg: 'h-11 px-6 text-base gap-2.5',
    xl: 'h-12 px-8 text-lg gap-3',
  };

  const colors = {
    primary: {
      solid: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 shadow-lg shadow-green-500/30 hover:shadow-xl hover:shadow-green-500/40',
      outline: 'border-2 border-green-600 text-green-600 hover:bg-green-50 dark:hover:bg-green-950 focus:ring-green-500',
      ghost: 'text-green-600 hover:bg-green-50 dark:hover:bg-green-950',
      soft: 'bg-green-50 dark:bg-green-950 text-green-600 hover:bg-green-100 dark:hover:bg-green-900',
      gradient: 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-600 hover:to-emerald-700 shadow-lg shadow-green-500/30',
    },
    secondary: {
      solid: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 shadow-lg shadow-blue-500/30',
      outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950 focus:ring-blue-500',
      ghost: 'text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950',
      soft: 'bg-blue-50 dark:bg-blue-950 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900',
      gradient: 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:from-blue-600 hover:to-indigo-700 shadow-lg shadow-blue-500/30',
    },
    success: {
      solid: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 shadow-lg shadow-green-500/30',
      outline: 'border-2 border-green-600 text-green-600 hover:bg-green-50 focus:ring-green-500',
      ghost: 'text-green-600 hover:bg-green-50',
      soft: 'bg-green-50 text-green-600 hover:bg-green-100',
      gradient: 'bg-gradient-to-r from-green-500 to-teal-600 text-white shadow-lg shadow-green-500/30',
    },
    warning: {
      solid: 'bg-amber-600 text-white hover:bg-amber-700 focus:ring-amber-500 shadow-lg shadow-amber-500/30',
      outline: 'border-2 border-amber-600 text-amber-600 hover:bg-amber-50 focus:ring-amber-500',
      ghost: 'text-amber-600 hover:bg-amber-50',
      soft: 'bg-amber-50 text-amber-600 hover:bg-amber-100',
      gradient: 'bg-gradient-to-r from-amber-500 to-orange-600 text-white shadow-lg shadow-amber-500/30',
    },
    error: {
      solid: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 shadow-lg shadow-red-500/30',
      outline: 'border-2 border-red-600 text-red-600 hover:bg-red-50 focus:ring-red-500',
      ghost: 'text-red-600 hover:bg-red-50',
      soft: 'bg-red-50 text-red-600 hover:bg-red-100',
      gradient: 'bg-gradient-to-r from-red-500 to-rose-600 text-white shadow-lg shadow-red-500/30',
    },
  };

  return (
    <motion.button
      whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
      whileTap={{ scale: disabled || loading ? 1 : 0.98 }}
      className={cn(
        baseStyles,
        sizes[size],
        colors[color][variant],
        fullWidth && 'w-full',
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      )}
      {!loading && icon && iconPosition === 'left' && icon}
      {children}
      {!loading && icon && iconPosition === 'right' && icon}
    </motion.button>
  );
};

// ==================== INPUT ====================

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  variant?: 'outline' | 'filled' | 'flushed';
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, leftIcon, rightIcon, variant = 'outline', className, ...props }, ref) => {
    const variants = {
      outline: 'border-2 border-gray-300 dark:border-gray-700 focus:border-green-500 dark:focus:border-green-500 bg-white dark:bg-gray-900',
      filled: 'border-0 bg-gray-100 dark:bg-gray-800 focus:bg-white dark:focus:bg-gray-900',
      flushed: 'border-0 border-b-2 border-gray-300 dark:border-gray-700 rounded-none focus:border-green-500 dark:focus:border-green-500',
    };

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            className={cn(
              'w-full h-10 px-4 rounded-xl text-gray-900 dark:text-white placeholder:text-gray-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-green-500/20',
              variants[variant],
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-red-500 focus:border-red-500 focus:ring-red-500/20',
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

// ==================== BADGE ====================

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'solid' | 'outline' | 'soft';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'gray';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
  className?: string;
}

export const Badge = ({ 
  children, 
  variant = 'soft', 
  color = 'primary', 
  size = 'md',
  dot = false,
  className 
}: BadgeProps) => {
  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5',
  };

  const colors = {
    primary: {
      solid: 'bg-green-600 text-white',
      outline: 'border border-green-600 text-green-600',
      soft: 'bg-green-50 dark:bg-green-950 text-green-600 dark:text-green-400',
    },
    secondary: {
      solid: 'bg-blue-600 text-white',
      outline: 'border border-blue-600 text-blue-600',
      soft: 'bg-blue-50 dark:bg-blue-950 text-blue-600 dark:text-blue-400',
    },
    success: {
      solid: 'bg-green-600 text-white',
      outline: 'border border-green-600 text-green-600',
      soft: 'bg-green-50 dark:bg-green-950 text-green-600 dark:text-green-400',
    },
    warning: {
      solid: 'bg-amber-600 text-white',
      outline: 'border border-amber-600 text-amber-600',
      soft: 'bg-amber-50 dark:bg-amber-950 text-amber-600 dark:text-amber-400',
    },
    error: {
      solid: 'bg-red-600 text-white',
      outline: 'border border-red-600 text-red-600',
      soft: 'bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400',
    },
    gray: {
      solid: 'bg-gray-600 text-white',
      outline: 'border border-gray-600 text-gray-600',
      soft: 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400',
    },
  };

  return (
    <span className={cn(
      'inline-flex items-center gap-1.5 font-medium rounded-full whitespace-nowrap',
      sizes[size],
      colors[color][variant],
      className
    )}>
      {dot && <span className="w-1.5 h-1.5 rounded-full bg-current" />}
      {children}
    </span>
  );
};

// ==================== AVATAR ====================

interface AvatarProps {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  status?: 'online' | 'offline' | 'away' | 'busy';
  className?: string;
}

export const Avatar = ({ 
  src, 
  alt, 
  name, 
  size = 'md', 
  status,
  className 
}: AvatarProps) => {
  const sizes = {
    xs: 'w-6 h-6 text-xs',
    sm: 'w-8 h-8 text-sm',
    md: 'w-10 h-10 text-base',
    lg: 'w-12 h-12 text-lg',
    xl: 'w-16 h-16 text-2xl',
    '2xl': 'w-20 h-20 text-3xl',
  };

  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-gray-400',
    away: 'bg-amber-500',
    busy: 'bg-red-500',
  };

  const getInitials = (name?: string) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className={cn('relative inline-block', className)}>
      <div className={cn(
        'rounded-full overflow-hidden bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-white font-semibold',
        sizes[size]
      )}>
        {src ? (
          <img src={src} alt={alt || name} className="w-full h-full object-cover" />
        ) : (
          <span>{getInitials(name)}</span>
        )}
      </div>
      {status && (
        <span className={cn(
          'absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white dark:border-gray-900',
          statusColors[status]
        )} />
      )}
    </div>
  );
};

// ==================== TOOLTIP ====================

interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export const Tooltip = ({ content, children, position = 'top' }: TooltipProps) => {
  const [isVisible, setIsVisible] = React.useState(false);

  const positions = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className={cn(
            'absolute z-50 px-3 py-2 text-sm text-white bg-gray-900 dark:bg-gray-800 rounded-lg shadow-lg whitespace-nowrap pointer-events-none',
            positions[position]
          )}
        >
          {content}
          <div className="absolute w-2 h-2 bg-gray-900 dark:bg-gray-800 rotate-45" 
            style={{
              [position === 'top' ? 'bottom' : position === 'bottom' ? 'top' : position === 'left' ? 'right' : 'left']: '-4px',
              left: position === 'top' || position === 'bottom' ? '50%' : undefined,
              top: position === 'left' || position === 'right' ? '50%' : undefined,
              transform: position === 'top' || position === 'bottom' ? 'translateX(-50%)' : 'translateY(-50%)',
            }}
          />
        </motion.div>
      )}
    </div>
  );
};

// ==================== PROGRESS ====================

interface ProgressProps {
  value: number;
  max?: number;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export const Progress = ({ 
  value, 
  max = 100, 
  color = 'primary', 
  size = 'md',
  showLabel = false,
  className 
}: ProgressProps) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const colors = {
    primary: 'bg-gradient-to-r from-green-500 to-emerald-600',
    secondary: 'bg-gradient-to-r from-blue-500 to-indigo-600',
    success: 'bg-gradient-to-r from-green-500 to-teal-600',
    warning: 'bg-gradient-to-r from-amber-500 to-orange-600',
    error: 'bg-gradient-to-r from-red-500 to-rose-600',
  };

  return (
    <div className={cn('w-full', className)}>
      <div className={cn(
        'w-full bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden',
        sizes[size]
      )}>
        <motion.div
          className={cn('h-full rounded-full', colors[color])}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
      {showLabel && (
        <div className="mt-1 text-sm text-gray-600 dark:text-gray-400 text-right">
          {percentage.toFixed(0)}%
        </div>
      )}
    </div>
  );
};
