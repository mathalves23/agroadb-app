import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

export default function Layout() {
  return (
    <div className="min-h-screen bg-[#f8f9fb]">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6 lg:p-8 max-w-[1440px]" role="main" aria-label="Conteúdo principal">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
