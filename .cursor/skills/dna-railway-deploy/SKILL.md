---
name: dna-railway-deploy
description: >-
  Deploy DNA BJJ Express API to Railway manually. Env vars, health check,
  GitHub connect. Trigger on: deploy, Railway, production URL, hosting backend.
---

# DNA Railway Deploy

Manual deploy for Phase 2 — no GitHub Actions auto-deploy in Phase 1.

Docs: [env-and-secrets.md](../../docs/01-setup/env-and-secrets.md)

## Prerequisites

- Backend passes local `/health` check
- GitHub repo `NafCodes/DNA_BJJ_APP` pushed to `main`
- Railway account with GitHub access

## Steps

1. Go to [railway.app](https://railway.app) → sign in with GitHub
2. **New Project** → **Deploy from GitHub repo** → select `DNA_BJJ_APP`
3. Railway auto-detects Node.js — start command: `npm start`
4. **Variables** tab — add:

| Variable | Value |
|----------|-------|
| `SUPABASE_URL` | `https://tjauifnaeirxxwkeqnxu.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | from Supabase Dashboard (server only) |
| `PORT` | `3000` |
| `CORS_ORIGIN` | Vercel frontend URL (after frontend deploy) |

5. Deploy — copy public URL (e.g. `https://dna-bjj-api-production.up.railway.app`)
6. Verify: `curl https://<railway-url>/health` → `{"status":"ok"}`

## Frontend env (after Railway deploy)

In Vercel (frontend repo):

```
VITE_API_URL=https://<railway-url>
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Build fails | Check `package.json` has `"start": "node src/index.js"` |
| Health 502 | Check env vars set; check Railway logs |
| Frontend CORS errors | Add `cors` middleware + set `CORS_ORIGIN` to exact Vercel URL |
| DB errors on routes | Verify service role key; check Supabase project is active |

## Phase 2 — GitHub Actions deploy (optional)

Add `RAILWAY_TOKEN` to GitHub secrets and a deploy workflow — not configured in Phase 1.

## Post-deploy checklist

- [ ] `/health` returns 200 on Railway URL
- [ ] Coach JWT + GET `/students` works
- [ ] `CORS_ORIGIN` matches frontend URL
- [ ] No secrets in repo or logs
