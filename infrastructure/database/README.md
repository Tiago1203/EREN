# infrastructure/database

Database schema, migration and diagnostic scripts for EREN's Supabase/Postgres
backend. These files were moved here from the former top-level `scripts/`
directory during the monorepo restructure; their contents are unchanged.

## Contents

| File | Purpose |
| --- | --- |
| `analyze-database.sql` | Inspect current database structure. |
| `check-schema.ts` | Query and report table structure via the Supabase client. |
| `diagnose-db.ts` | Diagnostic checks against the database. |
| `add-frecuencia-mantenimiento.sql` | Add maintenance-frequency column. |
| `create-admin-user.sql` | Create an admin user. |
| `fix-establecimientos-length.sql` | Fix column length for establecimientos. |
| `fix-rls-permissions.sql` | Adjust Row Level Security permissions. |
| `temp-create-users.js` | One-off script to seed demo users. |

## Notes

- The `.ts`/`.js` scripts use `@supabase/supabase-js`; run them with the
  workspace dependencies installed (`npm install` at the repo root).
- **Security:** some of these scripts historically contained hard-coded
  Supabase keys. Rotate any exposed keys and load credentials from environment
  variables instead of committing them.
