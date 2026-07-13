-- Script para agregar campo de frecuencia de mantenimiento en tabla equipos
-- Ejecutar esto en el SQL Editor de Supabase

-- Agregar columna de frecuencia de mantenimiento (en días)
ALTER TABLE equipos 
ADD COLUMN IF NOT EXISTS frecuencia_mantenimiento INTEGER;

-- Agregar columna de fecha del último mantenimiento
ALTER TABLE equipos 
ADD COLUMN IF NOT EXISTS fecha_ultimo_mantenimiento DATE;

-- Verificar los cambios
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'equipos' 
AND column_name IN ('frecuencia_mantenimiento', 'fecha_ultimo_mantenimiento');
