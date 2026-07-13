import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? 'https://mgzwhqejmifnmxplmwfn.supabase.co'
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY ?? ''

export async function POST(request: NextRequest) {
  try {
    // Verificar que la service role key esté configurada
    if (!supabaseServiceKey) {
      return NextResponse.json(
        { error: 'Error de configuración: SUPABASE_SERVICE_ROLE_KEY no está configurada. Por favor agrégala al archivo .env.local' },
        { status: 500 }
      )
    }

    const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey, {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
      },
    })

    const body = await request.json()
    const { email, password, role, establecimientoId } = body

    if (!email || !password || !role || !establecimientoId) {
      return NextResponse.json(
        { error: 'Faltan campos requeridos' },
        { status: 400 }
      )
    }

    // Crear usuario sin enviar correo de confirmación
    const { data: authData, error: authError } = await supabaseAdmin.auth.admin.createUser({
      email: email.trim(),
      password,
      email_confirm: true,
      user_metadata: { role },
    })

    if (authError) {
      console.error('Error creating user:', authError)
      return NextResponse.json(
        { error: authError.message },
        { status: 400 }
      )
    }

    const userId = authData.user?.id
    if (!userId) {
      return NextResponse.json(
        { error: 'No se pudo crear el usuario' },
        { status: 500 }
      )
    }

    // Crear perfil
    const { error: profileError } = await supabaseAdmin
      .from('profiles')
      .upsert({
        id: userId,
        email: email.trim(),
        role,
        establecimiento_id: establecimientoId,
        is_active: true,
      },
      { onConflict: 'id' }
    )

    if (profileError) {
      console.error('Error creating profile:', profileError)
    }

    return NextResponse.json({ userId, email })
  } catch (error) {
    console.error('Error in create-user API:', error)
    return NextResponse.json(
      { error: 'Error interno del servidor: ' + (error instanceof Error ? error.message : String(error)) },
      { status: 500 }
    )
  }
}
