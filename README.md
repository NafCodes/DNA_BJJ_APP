# DNA_BJJ_APP
This is for BJJ it will be used mostly for attendance tracking, and will have few other features


# DNA — BJJ Club Management App

> A mobile-first gym management app for BJJ clubs. Built for coaches. Handles student rosters, attendance, belt stripe progression, and digital waivers.

---

## Overview

DNA is a coach-facing mobile web app. Students interact with it in exactly one way — scanning a QR code to sign their annual waiver. Everything else is for coaches and instructors only.

This repo is the **backend API**. The frontend lives in a separate repo (`dna-bjj-frontend`).

---

## Tech Stack

| Layer | Tool |
|---|---|
| Runtime | Node.js |
| Framework | Express |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth (email/password) |
| File Storage | Supabase Storage (waiver PDFs) |
| Hosting | Railway |

---

## Getting Started

### Prerequisites

- Node.js v18+
- A Supabase project (see [supabase.com](https://supabase.com))
- Access to the `.env` file (ask a team member — never committed to the repo)

### Install

```bash
git clone https://github.com/your-org/dna-bjj-api.git
cd dna-bjj-api
npm install
```

### Environment Variables

Create a `.env` file in the root:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
JWT_SECRET=your_jwt_secret
PORT=3000
```

### Run Locally

```bash
npm run dev
```

The API will be running at `http://localhost:3000`.

---

## Database Schema

All tables live in Supabase. Row Level Security (RLS) is enabled — only authenticated coaches can read or write data.

### `students`
| Column | Type | Notes |
|---|---|---|
| id | uuid | Primary key |
| name | text | |
| email | text | Unique |
| belt_level | text | white / blue / purple / brown / black |
| join_date | date | |
| created_at | timestamptz | Auto |

### `stripes`
| Column | Type | Notes |
|---|---|---|
| id | uuid | Primary key |
| student_id | uuid | FK → students.id |
| stripe_number | int | 1–4 |
| awarded_date | date | |

### `attendance`
| Column | Type | Notes |
|---|---|---|
| id | uuid | Primary key |
| student_id | uuid | FK → students.id |
| session_date | date | |
| created_at | timestamptz | Auto |

### `waivers`
| Column | Type | Notes |
|---|---|---|
| id | uuid | Primary key |
| student_id | uuid | FK → students.id (nullable if unmatched) |
| signer_name | text | From the waiver form |
| signer_email | text | Used to match to a student |
| signed_date | date | |
| expires_date | date | Always Jan 1 of the following year |
| pdf_url | text | Supabase Storage URL |

---

## API Routes

All routes (except `POST /waivers`) require a valid coach auth token in the `Authorization` header.

### Students
```
GET    /students              List all students
POST   /students              Add a new student
PATCH  /students/:id          Update student info
DELETE /students/:id          Remove a student
```

### Stripes
```
POST   /stripes               Award a stripe to a student
DELETE /stripes/:id           Revoke a stripe
```

### Attendance
```
GET    /attendance            List attendance records (filter by student_id or date)
POST   /attendance            Check in a student for a session
DELETE /attendance/:id        Remove an attendance record
```

### Waivers
```
GET    /waivers               List all waivers
POST   /waivers               Submit a signed waiver (public — no auth required)
GET    /waivers/:student_id   Get waiver for a specific student
```

---

## Auth

Coaches log in with email and password via Supabase Auth. The frontend handles the login flow and passes a JWT with every request. There are no student accounts — students never log in.

To add a new coach account, an existing admin must create one directly in the Supabase dashboard under Authentication → Users.

---

## Waiver Logic(already done we just need to put the designed QR code on the app)
 
- Waivers are submitted by students via QR code — no login required
- On submission, the backend matches the signer's email to a student record and links the waiver
- If no match is found, the waiver is saved unmatched — a coach can assign it manually from the dashboard
- Expiry is always **January 1st of the following year**, regardless of when it was signed
- A student is considered waiver-compliant if they have a waiver where `expires_date` is in the future

---

## Deployment

The API is deployed on Railway and connected to the GitHub repo. Pushes to `main` trigger an automatic redeploy.

Environment variables are set in the Railway dashboard — do not commit them to the repo.

---

## Folder Structure

```
/src
  /routes
    students.js
    stripes.js
    attendance.js
    waivers.js
  /middleware
    auth.js
  /lib
    supabase.js
  index.js
.env              ← never committed
.gitignore
package.json
README.md
```

---

## Contributing

1. Branch off `main` — use `feature/your-feature-name`
2. Open a pull request with a short description of what changed
3. Get a review before merging

---

## Contact

For access to environment variables or the Supabase project, reach out to the project owner directly