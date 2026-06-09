---
name: supabase-backend
description: >-
  Supabase database work for DNA BJJ Express API: schema, RLS, migrations,
  MCP tools, auth patterns. Use MCP for remote DB ops; use dna-express-api
  skill for Express route wiring. Trigger on: Supabase, RLS, migrations,
  schema, database policies, seed data, backend, data model.
---

# Supabase Backend (DNA BJJ)

**MCP handles remote database operations.** Express route wiring is in [dna-express-api](../dna-express-api/SKILL.md).

Read [mcp-tools.md](mcp-tools.md) for MCP catalog. Docs: [schema.md](../../../docs/02-supabase/schema.md) · [rls-and-auth.md](../../../docs/02-supabase/rls-and-auth.md) · [api-contract.md](../../../docs/03-architecture/api-contract.md)

**Project ref:** `tjauifnaeirxxwkeqnxu` (NafCodes's Org). Re-authenticate Supabase MCP to that org — see [mcp-setup.md](../../../docs/02-supabase/mcp-setup.md).

---

## MCP vs code — who does what

| Task | Tool |
|------|------|
| Inspect schema, run SQL, apply DDL | **Supabase MCP** or Dashboard SQL editor |
| Security/perf advisors, logs | **Supabase MCP** |
| Express routes, auth middleware | **This repo** — `src/routes/*`, `src/middleware/auth.js` |
| RLS policy templates, migration files | [schema-rls.md](schema-rls.md) → `supabase/migrations/` |
| RLS audit queries | MCP `execute_sql` + [scripts/audit_rls.sql](scripts/audit_rls.sql) |

---

## Workflow A — Schema change

1. MCP `list_tables` (verbose) — confirm current state
2. Draft SQL per [schema-rls.md](schema-rls.md)
3. MCP `execute_sql` or Dashboard — iterate DDL
4. MCP `get_advisors` type=`security` — fix findings
5. Save final SQL to `supabase/migrations/<timestamp>_<name>.sql`
6. Update Express routes if columns changed
7. Update `docs/02-supabase/schema.md`

---

## Workflow B — Auth (this project)

- **Backend:** `requireAuth` validates JWT via `supabase.auth.getUser(token)` — see `src/middleware/auth.js`
- **Frontend (Phase 2):** `@supabase/supabase-js` with anon key in `GymMangment_app_demo`
- Coach accounts created manually in Supabase Dashboard → Authentication → Users
- Backend uses **service role** for DB — Express middleware is the auth gate

Do not use Next.js SSR patterns from [ssr-auth.md](ssr-auth.md) in this repo — that file is legacy reference only.

---

## Workflow C — Debug

1. MCP `get_logs` — auth, postgres, api
2. MCP `get_advisors` security + performance
3. MCP `execute_sql` — [scripts/audit_rls.sql](scripts/audit_rls.sql)
4. Local: `npm run dev` + test routes with coach JWT

---

## Tables (lowercase only)

| Table | Express route |
|-------|---------------|
| `students` | `/students` |
| `stripes` | `/stripes` |
| `attendance` | `/attendance` |
| `waivers` | not wired yet |

Obsolete: `Students_table`, `Strips`, `Attendance`, `Waivers`.

---

## Hard rules

- RLS enabled on all tables
- Never expose `SUPABASE_SERVICE_ROLE_KEY` to frontend
- Never commit `.env`
- ≤5 files per edit chunk ([AGENTS.md](../../../AGENTS.md))

---

## After schema changes

```bash
npm run dev
curl http://localhost:3000/health
```

Re-run MCP `get_advisors` type=`security`.
