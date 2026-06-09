# Server API Layer

Patterns from [api-contract.md](../../../docs/03-architecture/api-contract.md). MCP does not write application code.

---

## Error shape (required)

```typescript
type ApiError = {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
};

type ApiSuccess<T> = { data: T };
```

| Code | HTTP |
|------|------|
| `UNAUTHORIZED` | 401 |
| `FORBIDDEN` | 403 |
| `NOT_FOUND` | 404 |
| `VALIDATION_ERROR` | 400 |
| `INTERNAL_ERROR` | 500 |

---

## When to use what

| Pattern | Use for |
|---------|---------|
| **Server Component** + server client | Page data reads, lists, detail views |
| **Server Action** | Form mutations, deletes, revalidate |
| **Route Handler** | Webhooks, signed URLs, health check, third-party callbacks |
| **Client + browser client** | Realtime subscriptions, auth UI only |

Default: server-first. Client Supabase calls only when necessary.

---

## Server Component read

```typescript
import { createClient } from '@/lib/supabase/server';

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data: items, error } = await supabase
    .from('items')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) throw error;
  return <ItemList items={items ?? []} />;
}
```

RLS filters rows — do not skip `getUser()` on protected pages.

---

## Server Action mutation

```typescript
'use server';

import { createClient } from '@/lib/supabase/server';
import { revalidatePath } from 'next/cache';
import { z } from 'zod';

const schema = z.object({
  title: z.string().min(1).max(200),
});

export async function createItem(formData: FormData) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error('UNAUTHORIZED');

  const parsed = schema.safeParse({ title: formData.get('title') });
  if (!parsed.success) throw new Error('VALIDATION_ERROR');

  const { error } = await supabase.from('items').insert({
    title: parsed.data.title,
    user_id: user.id,
  });

  if (error) throw error;
  revalidatePath('/app/dashboard');
}
```

Always set `user_id` from `user.id` — belt-and-suspenders with RLS.

---

## Route Handler

```typescript
import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ data: { status: 'ok' } });
}

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    return NextResponse.json(
      { error: { code: 'UNAUTHORIZED', message: 'Sign in required' } },
      { status: 401 }
    );
  }
  // ...
}
```

Hackathon routes: `GET /api/health`, `POST /api/elevenlabs/signed-url` (if voice core).

---

## Typed Supabase client

After MCP `generate_typescript_types`:

```typescript
import type { Database } from '@/types/database.types';
import { createClient } from '@/lib/supabase/server';

// Pass Database generic when scaffolding supports it:
// createServerClient<Database>(...)
```

Regenerate types after every schema change.

---

## Demo mode (optional)

Env `DEMO_MODE=true` or `?demo=1`:

- Return fixture data from seed
- Skip live external APIs (ElevenLabs, etc.)
- Document for judges in README

---

## Checklist per endpoint

- [ ] `getUser()` before any write
- [ ] Zod validation on input
- [ ] `user_id` from auth, not request body
- [ ] Error shape matches contract
- [ ] `revalidatePath` / `revalidateTag` after mutations
- [ ] No secrets in client code
- [ ] RLS negative test still passes
