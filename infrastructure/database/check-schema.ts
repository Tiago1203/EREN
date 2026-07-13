import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://mgzwhqejmifnmxplmwfn.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1nendocWVqbWlmbm14cGxtd2ZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI0MDEzNjYsImV4cCI6MjA5Nzk3NzM2Nn0.IcBI6d_BqX8uu7qGkN18etbwvSwZwm6Tl5j2jukMykE'

const supabase = createClient(supabaseUrl, supabaseAnonKey)

async function checkSchema() {
  console.log('=== OBTENIENDO ESTRUCTURA DE TABLAS DESDE INFORMATION_SCHEMA ===\n')
  
  try {
    const { data, error } = await supabase
      .rpc('get_table_structure', { table_name: 'equipos' })
    
    if (error) {
      console.log('❌ No se puede usar RPC, intentando consulta directa a information_schema...')
    }
  } catch (e) {
    console.log('❌ RPC no disponible')
  }

  // Intentar consultar information_schema directamente
  try {
    const { data, error } = await supabase
      .from('information_schema.columns')
      .select('table_name, column_name, data_type, is_nullable')
      .in('table_name', ['establecimientos', 'equipos', 'eventos_mantenimiento', 'profiles'])
      .order('table_name, ordinal_position')
    
    if (error) {
      console.log(`❌ Error consultando information_schema: ${error.message}`)
      console.log('   El cliente anon no tiene acceso a information_schema')
    } else {
      console.log('✅ Estructura de tablas:')
      const tables: any = {}
      data?.forEach((col: any) => {
        if (!tables[col.table_name]) {
          tables[col.table_name] = []
        }
        tables[col.table_name].push(col)
      })
      
      Object.keys(tables).forEach(tableName => {
        console.log(`\n📋 ${tableName}:`)
        tables[tableName].forEach((col: any) => {
          console.log(`   - ${col.column_name}: ${col.data_type} ${col.is_nullable === 'YES' ? '(nullable)' : '(NOT NULL)'}`)
        })
      })
    }
  } catch (e: any) {
    console.log(`❌ Error: ${e.message}`)
  }
  
  console.log('\n=== VERIFICANDO POLÍTICAS RLS ===')
  console.log('Intentando consultar datos para verificar RLS...\n')
  
  try {
    const { data: equiposData, error: equiposError } = await supabase
      .from('equipos')
      .select('*')
    
    if (equiposError) {
      console.log(`❌ Equipos sin auth: ${equiposError.message}`)
      console.log('   Esto indica que RLS está activo y bloqueando acceso anónimo')
    } else {
      console.log(`✅ Equipos sin auth: ${equiposData?.length || 0} registros`)
      console.log('   RLS podría permitir lectura pública o estar desactivado')
    }
  } catch (e: any) {
    console.log(`❌ Error verificando RLS: ${e.message}`)
  }
}

checkSchema()
