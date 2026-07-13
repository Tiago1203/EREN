-- Script para crear un usuario admin inicial automáticamente
-- Ejecutar esto en el SQL Editor de Supabase

-- Primero verificar si ya existe el usuario
DO $$
DECLARE
    user_id uuid;
BEGIN
    -- Buscar si ya existe el usuario
    SELECT id INTO user_id FROM auth.users WHERE email = 'admin@biomedico.com';
    
    IF user_id IS NULL THEN
        -- Si no existe, crear el usuario usando la función de Supabase
        -- Nota: Esto requiere que el usuario tenga permisos de auth
        -- Si falla, crea el usuario manualmente desde el dashboard
        RAISE NOTICE 'Por favor crea el usuario admin@biomedico.com manualmente desde Authentication → Users';
    ELSE
        -- Si existe, crear o actualizar el profile
        INSERT INTO public.profiles (id, email, nombre, role, establecimiento_id, is_active, created_at, updated_at)
        VALUES (
            user_id,
            'admin@biomedico.com',
            'Administrador',
            'admin',
            NULL,
            true,
            now(),
            now()
        )
        ON CONFLICT (id) DO UPDATE SET
            email = EXCLUDED.email,
            nombre = EXCLUDED.nombre,
            role = EXCLUDED.role,
            updated_at = now();
            
        RAISE NOTICE 'Profile admin creado/actualizado exitosamente';
    END IF;
END $$;

-- Verificar el resultado
SELECT p.*, u.email as auth_email 
FROM public.profiles p 
JOIN auth.users u ON p.id = u.id 
WHERE p.role = 'admin';
