import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://mgzwhqejmifnmxplmwfn.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

const supabase = createClient(supabaseUrl, supabaseAnonKey)

const tables = [
  'profiles',
  'establecimientos',
  'equipos',
  'eventos_mantenimiento',
  'logs_auditoria',
] as const

async function probeTable(name: string, authenticated = false) {
  const { data, error, count } = await supabase
    .from(name)
    .select('*', { count: 'exact', head: false })
    .limit(3)

  const label = authenticated ? 'AUTH' : 'ANON'
  if (error) {
    console.log(`  [${label}] ${name}: ERROR - ${error.code} | ${error.message} | ${error.details || ''}`)
  } else {
    console.log(`  [${label}] ${name}: OK - count=${count ?? data?.length ?? 0}`)
    if (data && data.length > 0) {
      console.log(`    columns: ${Object.keys(data[0]).join(', ')}`)
      console.log(`    sample: ${JSON.stringify(data[0]).slice(0, 200)}`)
    }
  }
}

async function main() {
  console.log('=== SUPABASE DIAGNOSTIC ===\n')
  console.log(`URL: ${supabaseUrl}`)
  console.log(`Key length: ${supabaseAnonKey.length}\n`)

  console.log('--- Anonymous access ---')
  for (const table of tables) {
    await probeTable(table, false)
  }

  // Try login as admin if exists
  const testEmail = process.env.TEST_EMAIL || 'admin@biomedico.com'
  const testPassword = process.env.TEST_PASSWORD || 'admin123456'

  console.log(`\n--- Attempting login: ${testEmail} ---`)
  const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
    email: testEmail,
    password: testPassword,
  })

  if (authError) {
    console.log(`Login failed: ${authError.message}`)
  } else {
    console.log(`Login OK - user id: ${authData.user?.id}`)
    console.log(`Email: ${authData.user?.email}`)

    console.log('\n--- Authenticated access ---')
    for (const table of tables) {
      await probeTable(table, true)
    }

    // Specific profile fetch like the app does
    const userId = authData.user!.id
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .single()

    console.log('\n--- Profile .single() fetch (app pattern) ---')
    if (profileError) {
      console.log(`ERROR: code=${profileError.code} message=${profileError.message} details=${profileError.details} hint=${profileError.hint}`)
    } else {
      console.log('Profile:', JSON.stringify(profile, null, 2))
    }
  }

  await supabase.auth.signOut()
}

main().catch(console.error)
