-- =============================================================================
-- FIX: permission denied for function is_admin / belongs_to_user_establecimiento
-- Ejecutar en Supabase → SQL Editor
-- =============================================================================

-- 1. Otorgar EXECUTE en funciones helper usadas por las políticas RLS
DO $$
DECLARE
  fn RECORD;
BEGIN
  FOR fn IN
    SELECT p.oid::regprocedure AS func_sig
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname = 'public'
      AND p.proname IN (
        'is_admin',
        'belongs_to_user_establecimiento',
        'equipo_belongs_to_user',
        'get_user_establecimiento_id'
      )
  LOOP
    EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO authenticated', fn.func_sig);
    EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO anon', fn.func_sig);
    RAISE NOTICE 'Granted EXECUTE on %', fn.func_sig;
  END LOOP;
END $$;

-- 2. Si las funciones no existen, crearlas (idempotente; nombres de params deben coincidir)
CREATE OR REPLACE FUNCTION public.get_user_establecimiento_id()
RETURNS integer
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT establecimiento_id FROM public.profiles WHERE id = auth.uid();
$$;

CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.profiles
    WHERE id = auth.uid() AND role = 'admin' AND is_active = true
  );
$$;

CREATE OR REPLACE FUNCTION public.belongs_to_user_establecimiento(row_establecimiento_id integer)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT public.is_admin()
    OR EXISTS (
      SELECT 1 FROM public.profiles
      WHERE id = auth.uid() AND establecimiento_id = row_establecimiento_id AND is_active = true
    );
$$;

CREATE OR REPLACE FUNCTION public.equipo_belongs_to_user(equipo_id_param integer)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT public.is_admin()
    OR EXISTS (
      SELECT 1 FROM public.equipos e
      JOIN public.profiles p ON p.establecimiento_id = e.establecimiento_id
      WHERE e.id = equipo_id_param AND p.id = auth.uid() AND p.is_active = true
    );
$$;

-- 3. Re-otorgar permisos tras crear/reemplazar funciones
GRANT EXECUTE ON FUNCTION public.get_user_establecimiento_id() TO authenticated, anon;
GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated, anon;
GRANT EXECUTE ON FUNCTION public.belongs_to_user_establecimiento(integer) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION public.equipo_belongs_to_user(integer) TO authenticated, anon;

-- 4. Asegurar que profiles tenga RLS y políticas correctas
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can read own profile" ON public.profiles;
CREATE POLICY "Users can read own profile"
  ON public.profiles FOR SELECT
  TO authenticated
  USING (id = auth.uid() OR public.is_admin());

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
  ON public.profiles FOR UPDATE
  TO authenticated
  USING (id = auth.uid())
  WITH CHECK (id = auth.uid());

DROP POLICY IF EXISTS "Admins manage profiles" ON public.profiles;
CREATE POLICY "Admins manage profiles"
  ON public.profiles FOR ALL
  TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- 5. Trigger: crear profile automáticamente al registrarse
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  INSERT INTO public.profiles (id, email, role, is_active)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_app_meta_data->>'role', 'establecimiento'),
    true
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 6. Asegurar profile del admin existente
INSERT INTO public.profiles (id, email, nombre, role, is_active)
SELECT id, email, 'Administrador', 'admin', true
FROM auth.users
WHERE email = 'admin@biomedico.com'
ON CONFLICT (id) DO UPDATE SET
  role = 'admin',
  is_active = true,
  updated_at = now();

-- 7. Verificación
SELECT 'profiles' AS tabla, count(*) FROM public.profiles
UNION ALL SELECT 'establecimientos', count(*) FROM public.establecimientos
UNION ALL SELECT 'equipos', count(*) FROM public.equipos;
