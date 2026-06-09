-- RLS audit queries for Supabase MCP execute_sql
-- Run each query separately. Zero rows = good for red-flag queries.

-- 1. Public tables WITHOUT row level security enabled
select
  n.nspname as schema,
  c.relname as table_name
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where c.relkind = 'r'
  and n.nspname = 'public'
  and c.relrowsecurity = false
  and c.relname not like 'pg_%'
order by 1, 2;

-- 2. RLS-enabled tables with NO policies (blocks all access for anon/authenticated)
select
  schemaname,
  tablename
from pg_tables t
where schemaname = 'public'
  and exists (
    select 1 from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
    where c.relname = t.tablename
      and n.nspname = t.schemaname
      and c.relrowsecurity = true
  )
  and not exists (
    select 1 from pg_policies p
    where p.schemaname = t.schemaname
      and p.tablename = t.tablename
  );

-- 3. Policies with permissive USING (true) — common Lovable mistake
select
  schemaname,
  tablename,
  policyname,
  cmd,
  qual as using_expression,
  with_check
from pg_policies
where schemaname = 'public'
  and (
    qual = 'true'
    or with_check = 'true'
  );

-- 4. All policies for review (export and eyeball auth.uid() usage)
select
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual as using_expression,
  with_check
from pg_policies
where schemaname = 'public'
order by tablename, policyname;

-- 5. Tables missing user_id column (heuristic — user-owned data should have it)
select
  table_name
from information_schema.tables t
where t.table_schema = 'public'
  and t.table_type = 'BASE TABLE'
  and t.table_name not in ('schema_migrations')
  and not exists (
    select 1 from information_schema.columns c
    where c.table_schema = t.table_schema
      and c.table_name = t.table_name
      and c.column_name in ('user_id', 'id')
  );
