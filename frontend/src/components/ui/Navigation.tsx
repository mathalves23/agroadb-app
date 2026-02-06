import React from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  Bell, 
  Settings, 
  User, 
  Menu,
  X,
  Sun,
  Moon,
  ChevronDown,
  Home,
  FileText,
  BarChart3,
  Users,
  Shield,
  Database,
  HelpCircle,
  LogOut
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Avatar, Button, Badge, Input, Dropdown } from './Controls';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { Link, useLocation } from 'react-router-dom';

// ==================== TOP NAVIGATION ====================

export const TopNav = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [searchQuery, setSearchQuery] = React.useState('');

  const notifications = [
    { id: '1', title: 'Nova investigação criada', time: '5 min atrás', unread: true },
    { id: '2', title: 'Relatório pronto', time: '1 hora atrás', unread: true },
    { id: '3', title: 'Sistema atualizado', time: '2 horas atrás', unread: false },
  ];

  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="sticky top-0 z-40 w-full bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200 dark:border-gray-800"
    >
      <div className="container mx-auto px-4 h-16 flex items-center justify-between gap-4">
        {/* Logo & Brand */}
        <Link to="/dashboard" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-green-500/30 group-hover:shadow-xl group-hover:shadow-green-500/40 transition-all">
            <span className="text-2xl">🌾</span>
          </div>
          <div className="hidden sm:block">
            <h1 className="text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              AgroADB
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Inteligência Patrimonial
            </p>
          </div>
        </Link>

        {/* Search Bar */}
        <div className="flex-1 max-w-2xl hidden lg:block">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar investigações, propriedades, empresas..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-10 pl-10 pr-4 rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 transition-all"
            />
            <kbd className="absolute right-3 top-1/2 -translate-y-1/2 px-2 py-1 text-xs font-semibold text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded">
              ⌘K
            </kbd>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            {theme === 'dark' ? (
              <Sun className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            ) : (
              <Moon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            )}
          </button>

          {/* Notifications */}
          <Dropdown
            trigger={
              <button className="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white dark:ring-gray-900" />
                )}
              </button>
            }
            items={notifications.map(notif => ({
              id: notif.id,
              label: notif.title,
              icon: notif.unread ? <span className="w-2 h-2 bg-blue-500 rounded-full" /> : undefined,
              onClick: () => {},
            }))}
            position="bottom-right"
          />

          {/* User Menu */}
          <Dropdown
            trigger={
              <button className="flex items-center gap-2 p-1.5 pr-3 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                <Avatar
                  src={user?.avatar}
                  name={user?.full_name}
                  size="sm"
                  status="online"
                />
                <span className="hidden sm:block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {user?.full_name}
                </span>
                <ChevronDown className="w-4 h-4 text-gray-400" />
              </button>
            }
            items={[
              {
                id: 'profile',
                label: 'Meu Perfil',
                icon: <User className="w-4 h-4" />,
                onClick: () => {},
              },
              {
                id: 'settings',
                label: 'Configurações',
                icon: <Settings className="w-4 h-4" />,
                onClick: () => {},
              },
              {
                id: 'help',
                label: 'Ajuda',
                icon: <HelpCircle className="w-4 h-4" />,
                onClick: () => {},
              },
              {
                id: 'logout',
                label: 'Sair',
                icon: <LogOut className="w-4 h-4" />,
                onClick: logout,
                danger: true,
              },
            ]}
            position="bottom-right"
          />
        </div>
      </div>
    </motion.header>
  );
};

// ==================== SIDEBAR NAVIGATION ====================

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
  badge?: number;
  children?: NavItem[];
}

export const Sidebar = () => {
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = React.useState(false);
  const [expandedItems, setExpandedItems] = React.useState<string[]>([]);

  const navItems: NavItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <Home className="w-5 h-5" />,
      path: '/dashboard',
    },
    {
      id: 'investigations',
      label: 'Investigações',
      icon: <FileText className="w-5 h-5" />,
      path: '/investigations',
      badge: 12,
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: <BarChart3 className="w-5 h-5" />,
      path: '/analytics',
    },
    {
      id: 'database',
      label: 'Banco de Dados',
      icon: <Database className="w-5 h-5" />,
      path: '/database',
      children: [
        {
          id: 'properties',
          label: 'Propriedades',
          icon: <span>🏡</span>,
          path: '/database/properties',
        },
        {
          id: 'companies',
          label: 'Empresas',
          icon: <span>🏢</span>,
          path: '/database/companies',
        },
      ],
    },
    {
      id: 'team',
      label: 'Equipe',
      icon: <Users className="w-5 h-5" />,
      path: '/team',
    },
    {
      id: 'security',
      label: 'Segurança',
      icon: <Shield className="w-5 h-5" />,
      path: '/security',
    },
  ];

  const toggleExpand = (id: string) => {
    setExpandedItems(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <motion.aside
      initial={{ x: -300 }}
      animate={{ x: 0, width: isCollapsed ? 80 : 280 }}
      transition={{ type: 'spring', damping: 30, stiffness: 300 }}
      className="fixed left-0 top-16 bottom-0 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 z-30 overflow-y-auto"
    >
      <div className="p-4">
        {/* Collapse Toggle */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full mb-4 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center justify-center"
        >
          {isCollapsed ? <Menu className="w-5 h-5" /> : <X className="w-5 h-5" />}
        </button>

        {/* Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item) => (
            <NavItemComponent
              key={item.id}
              item={item}
              isCollapsed={isCollapsed}
              isActive={isActive(item.path)}
              isExpanded={expandedItems.includes(item.id)}
              onToggleExpand={() => toggleExpand(item.id)}
            />
          ))}
        </nav>
      </div>

      {/* Footer */}
      {!isCollapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-800 bg-gradient-to-t from-gray-50 dark:from-gray-950">
          <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
            <p className="font-semibold">AgroADB v1.0.0</p>
            <p>© 2026 Todos os direitos reservados</p>
          </div>
        </div>
      )}
    </motion.aside>
  );
};

// Helper component for nav items
const NavItemComponent = ({
  item,
  isCollapsed,
  isActive,
  isExpanded,
  onToggleExpand,
}: {
  item: NavItem;
  isCollapsed: boolean;
  isActive: boolean;
  isExpanded: boolean;
  onToggleExpand: () => void;
}) => {
  const hasChildren = item.children && item.children.length > 0;

  return (
    <div>
      <Link
        to={item.path}
        onClick={(e) => {
          if (hasChildren) {
            e.preventDefault();
            onToggleExpand();
          }
        }}
        className={cn(
          'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative',
          isActive
            ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg shadow-green-500/30'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
        )}
      >
        <span className={cn(
          'transition-transform group-hover:scale-110',
          isActive && 'text-white'
        )}>
          {item.icon}
        </span>

        {!isCollapsed && (
          <>
            <span className="flex-1 font-medium text-sm">{item.label}</span>
            {item.badge && (
              <Badge size="sm" color={isActive ? 'secondary' : 'primary'}>
                {item.badge}
              </Badge>
            )}
            {hasChildren && (
              <ChevronDown
                className={cn(
                  'w-4 h-4 transition-transform',
                  isExpanded && 'rotate-180'
                )}
              />
            )}
          </>
        )}

        {isActive && (
          <motion.div
            layoutId="activeTab"
            className="absolute inset-0 bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg -z-10"
            transition={{ type: 'spring', duration: 0.5 }}
          />
        )}
      </Link>

      {/* Children */}
      {hasChildren && isExpanded && !isCollapsed && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="ml-6 mt-1 space-y-1 border-l-2 border-gray-200 dark:border-gray-800 pl-4"
        >
          {item.children?.map((child) => (
            <Link
              key={child.id}
              to={child.path}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {child.icon}
              <span>{child.label}</span>
            </Link>
          ))}
        </motion.div>
      )}
    </div>
  );
};

// ==================== BREADCRUMBS ====================

interface BreadcrumbItem {
  label: string;
  path?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

export const Breadcrumbs = ({ items }: BreadcrumbsProps) => {
  return (
    <nav className="flex items-center gap-2 text-sm">
      <Home className="w-4 h-4 text-gray-400" />
      {items.map((item, index) => (
        <React.Fragment key={index}>
          <ChevronDown className="w-4 h-4 text-gray-400 rotate-[-90deg]" />
          {item.path ? (
            <Link
              to={item.path}
              className="text-gray-600 dark:text-gray-400 hover:text-green-600 dark:hover:text-green-500 transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-gray-900 dark:text-white font-medium">
              {item.label}
            </span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

// ==================== PAGE HEADER ====================

interface PageHeaderProps {
  title: string;
  description?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
}

export const PageHeader = ({ title, description, breadcrumbs, actions }: PageHeaderProps) => {
  return (
    <div className="mb-8">
      {breadcrumbs && (
        <div className="mb-4">
          <Breadcrumbs items={breadcrumbs} />
        </div>
      )}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {title}
          </h1>
          {description && (
            <p className="text-gray-600 dark:text-gray-400">
              {description}
            </p>
          )}
        </div>
        {actions && (
          <div className="flex items-center gap-2">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
};
