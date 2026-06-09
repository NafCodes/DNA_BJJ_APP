---
name: dna-express-api
description: >-
  Express API conventions for DNA BJJ backend: routes, middleware, CORS, auth,
  Supabase table mapping, error handling. Trigger on: Express routes, middleware,
  CORS, Railway, API endpoints, backend routes.
---

# DNA Express API

Docs: [api-contract.md](../../docs/03-architecture/api-contract.md) · [AGENTS.md](../../AGENTS.md)

## Entry point

[`src/index.js`](../../src/index.js) — mounts routers, exposes `GET /health`.

## Route map

| Mount | File | Auth | Methods |
|-------|------|------|---------|
| `/students` | `src/routes/students.js` | yes | GET, POST, PATCH /:id, DELETE /:id |
| `/stripes` | `src/routes/stripes.js` | yes | POST, DELETE /:id |
| `/attendance` | `src/routes/attendance.js` | yes | GET (?student_id, ?date), POST, DELETE /:id |
| `/health` | `src/index.js` | no | GET |

Waivers route intentionally not built — see project decisions in docs.

## Auth flow

1. Frontend logs in via Supabase Auth (anon key) — Phase 2
2. Frontend sends `Authorization: Bearer <access_token>` on API calls
3. `requireAuth` in `src/middleware/auth.js` calls `supabase.auth.getUser(token)`
4. On success, `req.user` is set; route handler proceeds

## Supabase client

[`src/lib/supabase.js`](../../src/lib/supabase.js) — `createClient(url, SUPABASE_SERVICE_ROLE_KEY)`.

Table names in `.from()` calls must match DB exactly:

```
students | stripes | attendance | waivers
```

## Adding a new route

1. Create `src/routes/<resource>.js` with `Router()`
2. Import `supabase` and `requireAuth`
3. Export default router
4. Mount in `src/index.js`: `app.use('/<resource>', router)`
5. Update `docs/03-architecture/api-contract.md`

## Phase 2 — CORS snippet

Install: `npm install cors`

```js
import cors from 'cors';

app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
}));
```

Add before route mounts in `src/index.js`. Set `CORS_ORIGIN` to Vercel URL in production.

## Verification

```bash
npm run dev
curl http://localhost:3000/health
# With coach JWT:
curl -H "Authorization: Bearer $TOKEN" http://localhost:3000/students
```
