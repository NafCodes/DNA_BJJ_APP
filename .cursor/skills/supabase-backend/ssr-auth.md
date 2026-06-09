# SSR Auth — Next.js + @supabase/ssr

MCP cannot write these files. Implement after Lovable UI import or when adding auth.

Env (`.env.local`, never commit):

```env
NEXT_PUBLIC_SUPABASE_URL=<from MCP get_project_url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<from MCP get_publishable_keys>
```

---

## File checklist

| File | Purpose |
|------|---------|
| `lib/supabase/server.ts` | RSC, Server Actions, Route Handlers |
| `lib/supabase/client.ts` | Client components (auth UI, realtime) |
| `lib/supabase/middleware.ts` | Session refresh helper for middleware |
| `middleware.ts` | Cookie refresh + route protection |
| `app/auth/callback/route.ts` | Exchange code for session |

Install if missing: `@supabase/ssr` `@supabase/supabase-js`

---

## lib/supabase/server.ts

```typescript
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            );
          } catch {
            // Called from Server Component — middleware handles refresh
          }
        },
      },
    }
  );
}
```

---

## lib/supabase/client.ts

```typescript
'use client';

import { createBrowserClient } from '@supabase/ssr';

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
```

---

## lib/supabase/middleware.ts

```typescript
import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  await supabase.auth.getUser();
  return supabaseResponse;
}
```

---

## middleware.ts (root)

```typescript
import { type NextRequest, NextResponse } from 'next/server';
import { updateSession } from '@/lib/supabase/middleware';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const publicPaths = ['/', '/login', '/auth/callback'];
  const isPublic =
    publicPaths.some((p) => pathname === p || pathname.startsWith('/auth/')) ||
    pathname.startsWith('/_next') ||
    pathname.includes('.');

  const response = await updateSession(request);

  if (!isPublic && pathname.startsWith('/app')) {
    const supabase = /* re-check user via cookie or pass from updateSession */;
    // Simple pattern: redirect if no session cookie present
    // Prefer: call getUser in updateSession and set x-user header
  }

  return response;
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
```

**Protected routes:** `app/(app)/*` per [security.md](../../../docs/03-architecture/security.md). Redirect unauthenticated users to `/login`.

---

## app/auth/callback/route.ts

```typescript
import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get('code');
  const next = searchParams.get('next') ?? '/app';

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      return NextResponse.redirect(`${origin}${next}`);
    }
  }

  return NextResponse.redirect(`${origin}/login?error=auth`);
}
```

---

## Migration from Lovable client auth

| Lovable | This repo |
|---------|-----------|
| `createClient(url, anonKey)` in component | `createClient()` from `@/lib/supabase/client` or `server` |
| `supabase.auth.onAuthStateChange` in App | Server session + middleware refresh |
| Protected `<Route>` | Middleware + `app/(app)/` layout |
| `useEffect` + `getSession()` | Server: `getUser()`; client: browser client sparingly |

Files flagged in `_lovable_review/` during UI import — fix here.

---

## Verification

1. Sign in → session cookie set
2. Refresh protected page → still authenticated
3. Sign out → protected routes redirect to `/login`
4. MCP `get_logs` service=`auth` if callback fails
