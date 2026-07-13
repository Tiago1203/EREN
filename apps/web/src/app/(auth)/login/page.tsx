'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { signIn } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const { error } = await signIn(email, password)

      if (error) {
        setError(
          error.message === 'Invalid login credentials'
            ? 'Credenciales incorrectas. Verifique su email y contraseña.'
            : error.message
        )
        setLoading(false)
        return
      }

      router.push('/dashboard')
      router.refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado al iniciar sesión')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Panel izquierdo decorativo */}
      <div className="hidden lg:flex lg:w-1/2 bg-[var(--sidebar)] relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-64 h-64 rounded-full bg-[var(--primary)] blur-3xl" />
          <div className="absolute bottom-20 right-20 w-48 h-48 rounded-full bg-blue-500 blur-3xl" />
        </div>
        <div className="relative z-10 flex flex-col justify-center px-16">
          <div className="w-12 h-12 rounded-xl bg-[var(--primary)] flex items-center justify-center mb-6">
            <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-white mb-3">
            Sistema de Mantenimiento Biomédico
          </h1>
          <p className="text-slate-400 text-lg leading-relaxed max-w-md">
            Gestione equipos médicos, calibraciones y mantenimientos de su establecimiento de salud.
          </p>
          <ul className="mt-8 space-y-3 text-slate-400 text-sm">
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--primary)]" />
              Control de equipos y criticidad
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--primary)]" />
              Registro de mantenimientos y calibraciones
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--primary)]" />
              Gestión multi-establecimiento
            </li>
          </ul>
        </div>
      </div>

      {/* Formulario */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="lg:hidden mb-8 text-center">
            <h2 className="text-2xl font-bold text-[var(--foreground)]">BioMédico</h2>
            <p className="text-[var(--muted)] text-sm mt-1">Mantenimiento</p>
          </div>

          <div className="card p-8">
            <h2 className="text-xl font-semibold text-[var(--foreground)] mb-1">
              Iniciar sesión
            </h2>
            <p className="text-sm text-[var(--muted)] mb-6">
              Ingrese sus credenciales para acceder al sistema
            </p>

            <form onSubmit={handleSubmit} className="space-y-5">
              {error && <div className="alert-error">{error}</div>}

              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-1.5">
                  Correo electrónico
                </label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  className="input-field"
                  placeholder="usuario@ejemplo.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium mb-1.5">
                  Contraseña
                </label>
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  className="input-field"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              <button type="submit" disabled={loading} className="btn-primary w-full py-2.5">
                {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
              </button>
            </form>
          </div>

          <p className="text-center text-xs text-[var(--muted)] mt-6">
            Sistema de gestión biomédica &copy; {new Date().getFullYear()}
          </p>
        </div>
      </div>
    </div>
  )
}
