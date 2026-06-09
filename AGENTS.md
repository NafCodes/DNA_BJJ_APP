# AGENTS.md — DNA BJJ Backend

Guidance for AI agents working in this repository.

## Project purpose

Express API for a BJJ club management app. Coaches manage students, attendance, and belt stripes. Students only interact via QR waiver signing (handled in the frontend repo, Phase 2).

This repo is the **backend only**. The React demo UI lives in a separate repo: `GymMangment_app_demo` (`NafCodes/GymMangment_app_demo`).

## Stack

| Layer | Technology |
|-------|------------|
| Runtime | Node.js 20+ (ESM) |
| Framework | Express 4 |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth — JWT validated in `src/middleware/auth.js` |
| Target hosting | Railway |

## Repository layout

```
src/
  index.js              Express app entry — mounts routes, /health
  lib/supabase.js       Supabase client (service_role key)
  middleware/auth.js    requireAuth — validates Bearer JWT
  routes/
    students.js         GET/POST/PATCH/DELETE /students
    stripes.js          POST/DELETE /stripes
    attendance.js       GET/POST/DELETE /attendance
```

Dead files at repo root (`auth.js`, `index.js`, `supabase.js`) are superseded by `src/` — do not edit them; delete in Phase 2.

## Hard rules

1. **Never commit `.env`** — use `.env.example` for documentation only.
2. **`SUPABASE_SERVICE_ROLE_KEY` is server-only** — never expose in frontend or client bundles.
3. **`SUPABASE_ANON_KEY` is for frontend auth only** (Phase 2) — not used by this Express app today.
4. **Table names are lowercase:** `students`, `stripes`, `attendance`, `waivers` — not the old PascalCase names.
5. **Protected routes** use `requireAuth` middleware. Waivers route is intentionally not built yet.
6. **Error shape:** `{ error: string }` with appropriate HTTP status codes.
7. **≤5 files per edit chunk** — commit between logical chunks when asked.

## Cross-repo pointer

| Repo | Path (local) | Role |
|------|--------------|------|
| DNA_BJJ_APP | this repo | Express API |
| GymMangment_app_demo | `../GymMangment_app_demo` | React + Vite demo (localStorage today) |

Frontend wiring (login, API client, replace localStorage) is **Phase 2**. See `.cursor/skills/dna-frontend-bridge/SKILL.md`.

## Phase boundaries

| Phase | Scope |
|-------|-------|
| **Phase 1 (current)** | CI, docs, `.cursor/` setup, `.env.example` |
| **Phase 2** | CORS, Railway deploy, frontend auth, API wiring, seed data |
| **Phase 3** | waivers route, tests, monitoring, production hardening |

## Documentation

Start at [`docs/README.md`](docs/README.md). Architecture and API contract: [`docs/03-architecture/`](docs/03-architecture/).

## Verification after backend changes

```bash
npm run dev
curl http://localhost:3000/health   # expect {"status":"ok"}
```
