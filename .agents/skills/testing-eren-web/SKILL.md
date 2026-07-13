---
name: testing-eren-web
description: Boot and smoke-test the EREN web app (apps/web / @eren/web, Next.js + Supabase) end-to-end. Use when verifying the web UI still builds and renders, especially after structural/monorepo changes.
---

# Testing EREN web (apps/web)

EREN is an **npm-workspaces monorepo**. The web UI lives in `apps/web`
(package name `@eren/web`); root scripts proxy to it.

## Run the app locally
From the **repo root**:
```bash
npm install
npm run dev     # proxies to @eren/web -> next dev on http://localhost:3000
npm run build   # compile + typecheck (proxies to @eren/web)
npm run lint    # eslint (has PRE-EXISTING errors in src/lib/*, unrelated to most changes)
```

## Required env (or the app throws at boot)
`apps/web/src/lib/supabase.ts` throws if `NEXT_PUBLIC_SUPABASE_ANON_KEY` is
missing, and `next build` static-prerender fails without it. Create
`apps/web/.env.local` (gitignored):
```
NEXT_PUBLIC_SUPABASE_URL=<project url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon key>
```
The URL + anon key are also hard-coded in `infrastructure/database/check-schema.ts`
and can be reused for a local boot/render smoke test. (These keys should ideally
be rotated and env-only — treat their presence in the repo as tech debt.)

## Golden-path smoke test (no login required)
Proves routing, the `@/*` tsconfig alias, Tailwind (`postcss.config.mjs`) and
middleware all work:
1. Visit `http://localhost:3000/` → must redirect to `/login`.
2. `/login` must render **fully styled** (dark left panel "Sistema de
   Mantenimiento Biomédico" + card "Iniciar sesión"); inputs must accept text.
3. Visit `/dashboard` with no session → must redirect back to `/login`
   (client guard in `apps/web/src/app/(dashboard)/layout.tsx` via `@/hooks/useAuth`).
4. Check the dev log for `Module not found` / `Can't resolve '@/...'` (should be none)
   and the browser console (only React DevTools info + `[HMR] connected` is normal).

Testing the authenticated dashboard/equipos/KPIs pages requires a real Supabase
user; without credentials, stop at the auth-guard redirect.

## Gotchas
- Node 20 works but emits deprecation warnings; Next 16 & supabase-js prefer Node ≥22.
- `next dev` uses Turbopack; first `/` request is slow (~2s compile), subsequent fast.
- If the app returns 200 on a protected route via `curl`, that's expected: the
  guard is client-side, so verify the redirect in a real browser, not curl.

## Devin Secrets Needed
- None strictly required for the smoke test (anon key is available in-repo).
- For authenticated testing: a valid Supabase **user email/password**, and
  optionally `SUPABASE_SERVICE_ROLE_KEY` for the `/api/create-user` route.
