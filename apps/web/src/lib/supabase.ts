import { createBrowserClient, createServerClient } from '@supabase/ssr'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? 'https://mgzwhqejmifnmxplmwfn.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ''

if (!supabaseAnonKey) {
  throw new Error('Missing NEXT_PUBLIC_SUPABASE_ANON_KEY environment variable')
}

export const supabase = createBrowserClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
  cookieOptions: {
    name: 'sb-auth-token',
    domain: undefined,
    path: '/',
    secure: process.env.NODE_ENV === 'production',
  },
})

export function createSupabaseServerClient(cookieStore: { getAll: () => Array<{ name: string; value: string }>; setAll: (cookies: Array<{ name: string; value: string; options?: Record<string, unknown> }>) => void }) {
  return createServerClient(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll()
      },
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value, options }) => cookieStore.setAll([{ name, value, options }]))
      },
    },
  })
}

// Tipos de base de datos según estructura real
export type Database = {
  public: {
    Tables: {
      establecimientos: {
        Row: {
          id: number
          ruc: string
          nombre_comercial: string
          tipologia: string
          direccion: string | null
          responsable_tecnico_cedula: string
          user_id: string | null
          url_certificado_acess: string | null
        }
        Insert: {
          id?: number
          ruc: string
          nombre_comercial: string
          tipologia: string
          direccion?: string
          responsable_tecnico_cedula: string
          user_id?: string
          url_certificado_acess?: string
        }
        Update: {
          ruc?: string
          nombre_comercial?: string
          tipologia?: string
          direccion?: string
          responsable_tecnico_cedula?: string
          user_id?: string
          url_certificado_acess?: string
        }
      }
      equipos: {
        Row: {
          id: number
          establecimiento_id: number
          codigo_unico: string
          nombre_dispositivo: string
          marca: string
          modelo: string
          numero_serie: string
          area_ubicacion: string
          criticidad: string
          estado_final: string
          fecha_proxima_calibracion: string | null
          url_manual_tecnico: string | null
          imp: number | null
        }
        Insert: {
          id?: number
          establecimiento_id: number
          codigo_unico: string
          nombre_dispositivo: string
          marca: string
          modelo: string
          numero_serie: string
          area_ubicacion: string
          criticidad: string
          estado_final?: string
          fecha_proxima_calibracion?: string
          url_manual_tecnico?: string
          imp?: number
        }
        Update: {
          codigo_unico?: string
          nombre_dispositivo?: string
          marca?: string
          modelo?: string
          numero_serie?: string
          area_ubicacion?: string
          criticidad?: string
          estado_final?: string
          fecha_proxima_calibracion?: string
          url_manual_tecnico?: string
          imp?: number
        }
      }
      eventos_mantenimiento: {
        Row: {
          id: number
          equipo_id: number
          tipo_evento: string
          fecha_ejecucion: string
          ingeniero_responsable: string
          descripcion_trabajo: string
          repuestos_cambiados: string | null
          error_porcentual: number | null
          incertidumbre: number | null
          estado_final: string
          url_informe_mantenimiento: string | null
        }
        Insert: {
          id?: number
          equipo_id: number
          tipo_evento: string
          fecha_ejecucion?: string
          ingeniero_responsable: string
          descripcion_trabajo: string
          repuestos_cambiados?: string
          error_porcentual?: number
          incertidumbre?: number
          estado_final?: string
          url_informe_mantenimiento?: string
        }
        Update: {
          tipo_evento?: string
          fecha_ejecucion?: string
          ingeniero_responsable?: string
          descripcion_trabajo?: string
          repuestos_cambiados?: string
          error_porcentual?: number
          incertidumbre?: number
          estado_final?: string
          url_informe_mantenimiento?: string
        }
      }
      logs_auditoria: {
        Row: {
          id: number
          usuario: string
          accion: string
          fecha_hora: string
          ip_origen: string | null
        }
        Insert: any
        Update: any
      }
      profiles: {
        Row: {
          id: string
          email: string
          nombre: string | null
          role: 'admin' | 'establecimiento'
          establecimiento_id: number | null
          is_active: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          email: string
          nombre?: string
          role: 'admin' | 'establecimiento'
          establecimiento_id?: number
          is_active?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          email?: string
          nombre?: string
          role?: 'admin' | 'establecimiento'
          establecimiento_id?: number
          is_active?: boolean
          updated_at?: string
        }
      }
    }
  }
}
