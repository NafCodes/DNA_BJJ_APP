# Schema & RLS

Conventions from [data-model.md](../../../docs/03-architecture/data-model.md). Use MCP for execution; save SQL in repo for judges.

---

## Table template

Replace `<table>` and columns with PRD entities.

```sql
create table public.<table> (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  -- columns...
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.<table> enable row level security;

create policy "<table>_select_own"
  on public.<table> for select to authenticated
  using (auth.uid() = user_id);

create policy "<table>_insert_own"
  on public.<table> for insert to authenticated
  with check (auth.uid() = user_id);

create policy "<table>_update_own"
  on public.<table> for update to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "<table>_delete_own"
  on public.<table> for delete to authenticated
  using (auth.uid() = user_id);

create index on public.<table> (user_id);
```

**Postgres gotcha:** UPDATE requires a SELECT policy — the template includes one.

---

## profiles (common first table)

```sql
create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text,
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

create policy "profiles_select_own"
  on public.profiles for select to authenticated
  using (auth.uid() = id);

create policy "profiles_insert_own"
  on public.profiles for insert to authenticated
  with check (auth.uid() = id);

create policy "profiles_update_own"
  on public.profiles for update to authenticated
  using (auth.uid() = id)
  with check (auth.uid() = id);
```

Trigger on signup (optional):

```sql
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data->>'display_name', 'User'));
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
```

Keep `security definer` functions out of exposed misuse — this pattern is standard for signup.

---

## Storage buckets

Run via MCP `execute_sql` after creating bucket in dashboard or:

```sql
-- Policies via storage.objects — see Supabase storage docs
-- avatars: authenticated users read/write own folder {user_id}/*
```

| Bucket | Public read | Write |
|--------|-------------|-------|
| `avatars` | No | Own `{user_id}/*` only |
| `assets` | Yes | Authenticated own prefix |

Storage upsert needs INSERT + SELECT + UPDATE policies.

---

## MCP workflow

1. `list_tables` verbose — avoid duplicate tables
2. `execute_sql` — run table + RLS SQL
3. `get_advisors` security — fix all issues
4. `execute_sql` — run [audit_rls.sql](scripts/audit_rls.sql) queries one by one
5. Copy final SQL → `supabase/migrations/<timestamp>_<name>.sql`
6. `generate_typescript_types` → `types/database.types.ts`

---

## Lovable schema audit

Lovable often ships:

- RLS disabled
- `using (true)` policies
- Policies checking client-supplied columns

**Fix before demo.** Run audit SQL after every import.

---

## Demo seed

`supabase/seed.sql` — deterministic golden-path data:

```sql
-- Use fixed UUIDs for demo users if auth users exist
-- insert into public.items (id, user_id, title) values (...);
```

Or `scripts/seed-demo.ts` using service role **locally only** — never in client bundle.

---

## Negative test (blocking)

MCP cannot run this — manual in browser or test script with two sessions:

1. User A signs in → creates row R
2. User B signs in → queries R by ID
3. **Must get zero rows** (or error). If B sees A's data, RLS is broken — stop and fix.

Document pass/fail in PR or decisions.md before calling security done.

---

## Red flags in audit output

| Finding | Action |
|---------|--------|
| Table in `public` without RLS | `enable row level security` |
| Policy `using (true)` | Replace with `auth.uid() = user_id` |
| No policies on RLS-enabled table | Add four policies |
| View without `security_invoker` | Fix or revoke anon/authenticated access |
