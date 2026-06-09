# Supabase MCP Tools

Server: `plugin-supabase-supabase` (OAuth — user must authenticate in Cursor if tools are missing).

Call via Cursor MCP. Every tool requires `project_id` unless noted.

---

## Project & org

| Tool | Use when |
|------|----------|
| `list_organizations` | Find org slug/id |
| `get_organization` | Org details |
| `list_projects` | **Start here** — get `project_id` |
| `get_project` | Project status, region, DB host |
| `create_project` | New project (confirm cost first) |
| `get_cost` / `confirm_cost` | Before creating paid resources |
| `pause_project` / `restore_project` | Cost control after hackathon |

---

## Database

| Tool | Use when |
|------|----------|
| `list_tables` | Before any schema work (`verbose: true` for columns/FKs) |
| `execute_sql` | Ad-hoc SQL, RLS audit queries, prototyping DDL |
| `apply_migration` | Named DDL migration on **remote** (use carefully — see below) |
| `list_migrations` | See applied migration history |
| `list_extensions` | Check pg_vector, pg_cron, etc. |

### execute_sql vs apply_migration

| | `execute_sql` | `apply_migration` |
|--|---------------|-------------------|
| Best for | Iterating schema, audits, reads | Final committed DDL on remote |
| Migration file in repo | You write manually | Name + SQL stored remotely |
| Hackathon speed | Prefer for iteration | Use when ready to lock in |

**Pattern:** iterate with `execute_sql` → copy final SQL to `supabase/migrations/` → optionally `apply_migration` with same SQL for remote history.

---

## Security & observability

| Tool | Use when |
|------|----------|
| `get_advisors` type=`security` | **After every DDL change** — missing RLS, exposed views, etc. |
| `get_advisors` type=`performance` | Missing indexes, slow query hints |
| `get_logs` | Debug auth failures, 500s, edge errors |

---

## Client config (safe for .env.local)

| Tool | Use when |
|------|----------|
| `get_project_url` | `NEXT_PUBLIC_SUPABASE_URL` |
| `get_publishable_keys` | `NEXT_PUBLIC_SUPABASE_ANON_KEY` |

Never paste `service_role` into client env or MCP output into committed files.

---

## Types & docs

| Tool | Use when |
|------|----------|
| `generate_typescript_types` | After schema change → `types/database.types.ts` |
| `search_docs` | Unsure of API — prefer over training data |

---

## Edge functions

| Tool | Use when |
|------|----------|
| `list_edge_functions` | See what's deployed |
| `get_edge_function` | Read function source |
| `deploy_edge_function` | Ship secrets-handling logic |

---

## Branching (optional)

| Tool | Use when |
|------|----------|
| `create_branch` / `list_branches` / `merge_branch` / `delete_branch` / `reset_branch` / `rebase_branch` | Preview DB branches — skip unless team uses Supabase branching |

---

## What MCP does **not** do

These are **code in this repo** — use [ssr-auth.md](ssr-auth.md) and [server-api.md](server-api.md):

- Next.js `middleware.ts` session refresh
- `@supabase/ssr` server/browser clients
- Server Actions and Route Handlers
- OAuth callback route
- Zod validation at API boundary
- `revalidatePath` after mutations
- Demo seed scripts (`supabase/seed.sql`)
- Browser negative test (User A vs User B)
- Vercel env var configuration

---

## Recommended call order (new feature)

```
list_projects
  → list_tables (verbose)
  → execute_sql (DDL + RLS)
  → get_advisors (security)
  → execute_sql (audit_rls.sql)
  → generate_typescript_types
  → [write Next.js code]
  → get_logs (if errors)
```
