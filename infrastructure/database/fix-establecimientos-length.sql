-- Script para corregir los límites de caracteres en la tabla establecimientos
-- Ejecutar esto en el SQL Editor de Supabase

-- Aumentar el límite de RUC a 13 caracteres (formato ecuatoriano)
ALTER TABLE establecimientos 
ALTER COLUMN ruc TYPE varchar(13);

-- Aumentar el límite de responsable_tecnico_cedula a 13 caracteres (para cédulas o RUC)
ALTER TABLE establecimientos 
ALTER COLUMN responsable_tecnico_cedula TYPE varchar(13);

-- Verificar los cambios
SELECT 
    column_name, 
    data_type, 
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'establecimientos' 
AND column_name IN ('ruc', 'responsable_tecnico_cedula');
