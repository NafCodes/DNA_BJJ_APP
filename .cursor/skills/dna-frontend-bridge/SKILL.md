---
name: dna-frontend-bridge
description: >-
  Wire GymMangment_app_demo frontend to DNA_BJJ_APP Express API. Maps localStorage
  helpers to API endpoints, documents VITE_API_URL and auth setup. Trigger on:
  wire frontend, localStorage, demo repo, frontend integration, API client.
---

# DNA Frontend Bridge

**Frontend repo:** `GymMangment_app_demo` (`NafCodes/GymMangment_app_demo`)  
**Backend repo:** this repo (`DNA_BJJ_APP`)

Phase 2 work — do not start until backend is deployed and CORS is configured.

## Current state (demo)

All data in `src/data/seedData.js` via localStorage keys:
- `bjj_students`, `bjj_attendance`, `bjj_waivers`

## Target state

| Demo helper | Replace with | Express endpoint |
|-------------|--------------|------------------|
| `getStudents()` / `saveStudents()` | API client | GET/POST/PATCH/DELETE `/students` |
| Stripe award/remove in `StudentProfile.jsx` | API client | POST/DELETE `/stripes` |
| `getAttendance()` / `saveAttendance()` | API client | GET/POST `/attendance` |
| Waiver status display | API client | GET `/students` (`waiver_active` field) |
| `initializeStorage()` seed | Remove or gate behind `DEMO_MODE` | Seed script on backend |

## Frontend env vars (Phase 2)

```bash
# GymMangment_app_demo/.env
VITE_API_URL=http://localhost:3000          # or Railway URL
VITE_SUPABASE_URL=https://tjauifnaeirxxwkeqnxu.supabase.co
VITE_SUPABASE_ANON_KEY=<anon-key-from-dashboard>
```

## Files to create in frontend repo

| File | Purpose |
|------|---------|
| `src/lib/supabase.js` | Supabase client with anon key — login only |
| `src/lib/api.js` | fetch wrapper: base URL + Bearer token |
| `src/pages/Login.jsx` | Email/password → store session token |

## Files to update

| File | Change |
|------|--------|
| `App.jsx` | Auth guard; `/sign-waiver` and `/login` public |
| `Students.jsx` | Replace localStorage with GET/POST `/students` |
| `StudentProfile.jsx` | PATCH/DELETE students; POST/DELETE stripes |
| `Attendance.jsx` | GET/POST `/attendance` |
| `Waivers.jsx` | Read `waiver_active` from students list |

## API client pattern

```js
const API_URL = import.meta.env.VITE_API_URL;

export async function apiFetch(path, options = {}) {
  const token = /* from Supabase session */;
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || res.statusText);
  }
  if (res.status === 204) return null;
  return res.json();
}
```

## Waiver business rule

Waivers expire **January 1 of the year following signing**. Preserve this logic when reading `waiver_active` or future waiver fields.

## Order of implementation

1. Deploy backend to Railway + CORS
2. Create coach user in Supabase Auth
3. Login.jsx + auth guard
4. Students.jsx (core)
5. Attendance.jsx
6. StudentProfile.jsx (stripes)
7. Waivers.jsx (read-only status)

One file at a time; test after each.
