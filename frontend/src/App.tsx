import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import { Suspense, lazy, useState, useEffect } from 'react'
import { useAuthStore } from './stores/authStore'
import Layout from './components/Layout'
import { OnboardingTour } from './components/Onboarding'

// Lazy-loaded pages
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const InvestigationsPage = lazy(() => import('./pages/InvestigationsPage'))
const InvestigationDetailPage = lazy(() => import('./pages/InvestigationDetailPage'))
const NewInvestigationPage = lazy(() => import('./pages/NewInvestigationPage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))
const ProfilePage = lazy(() => import('./pages/ProfilePage'))
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'))

function SuspenseFallback() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]" role="status" aria-label="Carregando página">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-3 border-emerald-200 border-t-emerald-600 rounded-full animate-spin" />
        <span className="text-sm text-gray-500">Carregando...</span>
      </div>
    </div>
  )
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

const router = createBrowserRouter(
  [
    { path: '/login', element: <Suspense fallback={<SuspenseFallback />}><LoginPage /></Suspense> },
    { path: '/register', element: <Suspense fallback={<SuspenseFallback />}><RegisterPage /></Suspense> },
    {
      path: '/',
      element: (
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      ),
      children: [
        { index: true, element: <Navigate to="/dashboard" replace /> },
        { path: 'dashboard', element: <Suspense fallback={<SuspenseFallback />}><DashboardPage /></Suspense> },
        { path: 'investigations', element: <Suspense fallback={<SuspenseFallback />}><InvestigationsPage /></Suspense> },
        { path: 'investigations/new', element: <Suspense fallback={<SuspenseFallback />}><NewInvestigationPage /></Suspense> },
        { path: 'investigations/:id', element: <Suspense fallback={<SuspenseFallback />}><InvestigationDetailPage /></Suspense> },
        { path: 'settings', element: <Suspense fallback={<SuspenseFallback />}><SettingsPage /></Suspense> },
        { path: 'profile', element: <Suspense fallback={<SuspenseFallback />}><ProfilePage /></Suspense> },
        { path: 'notifications', element: <Suspense fallback={<SuspenseFallback />}><NotificationsPage /></Suspense> },
      ],
    },
  ]
)

function App() {
  const { isAuthenticated } = useAuthStore()
  const [showTour, setShowTour] = useState(false)

  useEffect(() => {
    // Só mostrar o tour se o usuário estiver autenticado
    if (isAuthenticated) {
      const tourCompleted = localStorage.getItem('tour_completed')
      if (!tourCompleted) {
        // Aguardar um pouco para garantir que a página carregou
        const timer = setTimeout(() => {
          setShowTour(true)
        }, 1500)
        return () => clearTimeout(timer)
      }
    }
  }, [isAuthenticated])

  return (
    <>
      <RouterProvider router={router} />
      {isAuthenticated && <OnboardingTour run={showTour} />}
    </>
  )
}

export default App
