---
name: deploy-gate
description: >-
  Deploy hackathon app to Vercel with env vars, build verification, and Copilot
  review gate. Use when asked to: deploy, Vercel preview, production URL, CI
  gate, pre-deploy review, ship for judges.
---

# Deploy Gate

Follow [docs/03-architecture/cicd-deploy.md](../../docs/03-architecture/cicd-deploy.md).

Deploy only after: RLS negative test · `npm run build` clean · lovable-import validate passed.

---

## Step 1 — Pre-deploy checklist

- [ ] `npm run build` exits 0
- [ ] MCP `get_advisors` security — no critical RLS issues
- [ ] `.env.local` not staged; Vercel env vars set
- [ ] Preview URL route loads golden path
- [ ] Demo seed / `DEMO_MODE` if external APIs used

---

## Step 2 — Copilot review gate

```bash
copilot -p "Review staged changes for auth bypass, exposed secrets, missing RLS assumptions, and client-side service_role usage" --allow-tool='shell(git)'
```

Fix real findings. Re-stage. Do not deploy with open security issues.

---

## Step 3 — Env vars (Vercel dashboard)

| Variable | Scope |
|----------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | Production + Preview |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Production + Preview |
| `SUPABASE_SERVICE_ROLE_KEY` | Server only |
| `ELEVENLABS_API_KEY` | Server only (if voice) |
| `DEMO_MODE` | Preview optional |

```bash
vercel env pull .env.local
```

---

## Step 4 — Deploy

```bash
git push origin main
```

Or preview:

```bash
vercel deploy
```

Production (explicit):

```bash
vercel --prod
```

Hook will **ask** before `vercel --prod` — confirm checklist first.

---

## Step 5 — Post-deploy

- [ ] Open preview URL — golden path works logged out/in
- [ ] Tag `demo-ready` before judging
- [ ] README: preview URL + one-line pitch + how to run locally
- [ ] Record backup demo video (PLAYBOOK Block 9)

---

## Hard rules

- No force-push to `main`
- No `NEXT_PUBLIC_*` for secrets
- No deploy with failing build or open RLS audit findings
