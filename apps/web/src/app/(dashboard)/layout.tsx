'use client'

import { useAuth } from '@/hooks/useAuth'
import { useRouter, usePathname } from 'next/navigation'
import { useEffect } from 'react'
import { NotificationBell } from '@/components/ui/Notifications'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { href: '/equipos', label: 'Equipos', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' },
  { href: '/mantenimientos', label: 'Mantenimientos', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
  { href: '/kpis', label: 'KPIs', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { href: '/establecimientos', label: 'Establecimientos', icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4', adminOnly: true },
]

function NavIcon({ d }: { d: string }) {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
      <path strokeLinecap="round" strokeLinejoin="round" d={d} />
    </svg>
  )
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, profile, loading, profileError, signOut, isAdmin } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    }
    // Proteger rutas solo admin
    if (!loading && user && !isAdmin && pathname === '/establecimientos') {
      router.push('/dashboard')
    }
  }, [user, loading, isAdmin, pathname, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--background)]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-[var(--muted)]">Cargando sesión...</p>
        </div>
      </div>
    )
  }

  if (!user) return null

  const handleSignOut = async () => {
    await signOut()
    router.push('/login')
  }

  return (
    <div className="min-h-screen flex bg-[var(--background)]">
      {/* Sidebar */}
      <aside className="hidden md:flex md:w-64 flex-col bg-[var(--sidebar)] text-[var(--sidebar-text)]">
        <div className="px-6 py-5 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-[var(--primary)] flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <div>
                <h1 className="text-sm font-semibold text-white leading-tight">BioMédico</h1>
                <p className="text-xs text-slate-400">Mantenimiento</p>
              </div>
            </div>
            <NotificationBell />
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems
            .filter((item) => !item.adminOnly || isAdmin)
            .map((item) => {
              const active = pathname === item.href
              return (
                <button
                  key={item.href}
                  onClick={() => router.push(item.href)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    active
                      ? 'bg-[var(--primary)] text-white'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <NavIcon d={item.icon} />
                  {item.label}
                </button>
              )
            })}
        </nav>

        <div className="px-4 py-4 border-t border-slate-700">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center text-xs font-medium text-white">
              {(profile?.nombre || profile?.email || 'U').charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {profile?.nombre || profile?.email}
              </p>
              <span className={`badge ${isAdmin ? 'badge-admin' : 'badge-establecimiento'} mt-0.5`}>
                {isAdmin ? 'Admin' : 'Establecimiento'}
              </span>
            </div>
          </div>
          <button
            onClick={handleSignOut}
            className="w-full text-left text-xs text-slate-400 hover:text-white transition-colors px-1"
          >
            Cerrar sesión
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <header className="md:hidden bg-[var(--card)] border-b border-[var(--card-border)] px-4 py-3 flex items-center justify-between">
          <h1 className="text-sm font-semibold">BioMédico</h1>
          <button onClick={handleSignOut} className="text-xs text-[var(--muted)]">Salir</button>
        </header>

        {/* Mobile nav */}
        <nav className="md:hidden flex border-b border-[var(--card-border)] bg-[var(--card)] overflow-x-auto">
          {navItems
            .filter((item) => !item.adminOnly || isAdmin)
            .map((item) => (
              <button
                key={item.href}
                onClick={() => router.push(item.href)}
                className={`flex-shrink-0 px-4 py-2.5 text-xs font-medium border-b-2 transition-colors ${
                  pathname === item.href
                    ? 'border-[var(--primary)] text-[var(--primary)]'
                    : 'border-transparent text-[var(--muted)]'
                }`}
              >
                {item.label}
              </button>
            ))}
        </nav>

        <main className="flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto">
          {profileError && (
            <div className="alert-warning mb-6">
              <strong>Perfil no disponible:</strong> {profileError}
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  )
}
