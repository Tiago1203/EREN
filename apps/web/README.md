# @eren/web

The **web interface** for EREN — the human-facing entry point into the
Cognitive Operating System. Built with Next.js.

This app was migrated from the repository root into the monorepo at
`apps/web/` without changing its behaviour.

## Develop

From the **repository root** (recommended — uses npm workspaces):

```bash
npm install            # installs all workspaces
npm run dev            # runs @eren/web dev server
npm run build          # builds @eren/web
npm run lint           # lints @eren/web
```

Or scoped directly to this workspace:

```bash
npm run dev --workspace @eren/web
```

## Environment

Copy the required Supabase variables into `apps/web/.env.local` (not committed):

```
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...   # server-only, for admin routes
```

## Layout

- `src/app/` — Next.js App Router (routes, layouts, API route handlers).
- `src/components/` — React components.
- `src/hooks/`, `src/lib/` — client hooks and data/access helpers.
- `middleware.ts` — auth/session middleware.
- `public/` — static assets.
