'use client'

import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { User } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'

export interface Profile {
  id: string
  email: string
  nombre: string | null
  role: 'admin' | 'establecimiento'
  establecimiento_id: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}

interface AuthContextType {
  user: User | null
  profile: Profile | null
  loading: boolean
  profileError: string | null
  signIn: (email: string, password: string) => ReturnType<typeof supabase.auth.signInWithPassword>
  signOut: () => Promise<void>
  isAdmin: boolean
  isEstablecimiento: boolean
  establecimientoId: number | null
  refreshProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [loading, setLoading] = useState(true)
  const [profileError, setProfileError] = useState<string | null>(null)

  const fetchProfile = useCallback(async (userId: string, userEmail?: string) => {
    setProfileError(null)
    try {
      let { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single()

      if (error?.code === 'PGRST116' && userEmail) {
        const fallback = await supabase.from('profiles').select('*').eq('email', userEmail).maybeSingle()
        data = fallback.data
        error = fallback.error
      }

      if (error) {
        if (error.code === 'PGRST116') {
          setProfileError('No se encontró perfil de usuario. Contacte al administrador.')
        } else {
          setProfileError(
            error.message.includes('permission denied')
              ? 'Error de permisos en la base de datos. Ejecute scripts/fix-rls-permissions.sql en Supabase.'
              : error.message
          )
        }
        setProfile(null)
        return
      }

      let resolvedProfile = data
      if (resolvedProfile?.role === 'establecimiento' && !resolvedProfile.establecimiento_id) {
        const { data: establecimiento } = await supabase
          .from('establecimientos')
          .select('id')
          .eq('user_id', userId)
          .maybeSingle()

        if (establecimiento?.id) {
          const { data: updatedProfile } = await supabase
            .from('profiles')
            .update({ establecimiento_id: establecimiento.id })
            .eq('id', userId)
            .select('*')
            .single()

          resolvedProfile = updatedProfile ?? resolvedProfile
        }
      }

      setProfile(resolvedProfile)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido al cargar perfil'
      setProfileError(message)
      setProfile(null)
    }
  }, [])

  const refreshProfile = useCallback(async () => {
    if (user) {
      await fetchProfile(user.id, user.email)
    }
  }, [user, fetchProfile])

  useEffect(() => {
    let mounted = true

    const initAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (!mounted) return

      setUser(session?.user ?? null)
      if (session?.user) {
        await fetchProfile(session.user.id, session.user.email)
      }
      if (mounted) setLoading(false)
    }

    initAuth()

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (_event, session) => {
        if (!mounted) return
        setUser(session?.user ?? null)
        if (session?.user) {
          await fetchProfile(session.user.id, session.user.email)
        } else {
          setProfile(null)
          setProfileError(null)
        }
        if (mounted) setLoading(false)
      }
    )

    return () => {
      mounted = false
      subscription.unsubscribe()
    }
  }, [fetchProfile])

  const signIn = async (email: string, password: string) => {
    return supabase.auth.signInWithPassword({ email, password })
  }

  const signOut = async () => {
    await supabase.auth.signOut()
    setProfile(null)
    setProfileError(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        loading,
        profileError,
        signIn,
        signOut,
        isAdmin: profile?.role === 'admin',
        isEstablecimiento: profile?.role === 'establecimiento',
        establecimientoId: profile?.establecimiento_id ?? null,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Alias para compatibilidad
export const useAuthContext = useAuth
