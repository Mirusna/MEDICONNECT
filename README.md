## 🔗 Live Demo [mediconnect-sepia-tau.vercel.app](https://mediconnect-sepia-tau.vercel.app)
# MediConnect — Smart Hospital Appointment & Symptom Advisor

Full-stack app: patients check doctor availability, book/cancel appointments,
and get symptom-based specialist recommendations + basic diet/care tips.

**Stack:** React (Vite) + FastAPI + PostgreSQL

## Status — all phases complete

- [x] Step 1 — repo scaffolded, git initialized
- [x] Step 2 — data model (see `docs/data-model.md`)
- [x] Step 3 — FastAPI ↔ Postgres wired up, `/health` proves it
- [x] Step 4 — SQLAlchemy models + first Alembic migration
- [x] Step 5 — JWT auth, patient/doctor roles
- [x] Step 6 — doctor + appointment CRUD, slot generation, conflict checking
- [x] Step 7 — React frontend: login → doctor list w/ specialty filter → booking flow
- [x] Step 8 — Symptom → Specialty lookup (rule-based)
- [x] Step 9 — Disease → diet/care recommendation lookup
- [x] Step 10 — Symptom input box on frontend, "book with this doctor" shortcut

Every backend endpoint below was actually exercised against a live Postgres
instance while building this (not just written and assumed to work) — signup,
login, doctor filtering, slot generation, booking, double-booking rejection
(409), listing, and cancellation all verified via curl. The frontend was
built with `vite build` and confirmed to compile and serve with zero errors.

## Run it

### 1. Backend + database (Docker)

```bash
docker compose up --build
```

This starts Postgres and the FastAPI backend. On first run, apply the
migration and load seed data (sample doctors + symptom/disease lookup
tables) from a second terminal:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

Check it's alive:

```bash
curl http://localhost:8000/health
# {"api":"ok","database":"connected"}
```

API docs: http://localhost:8000/docs

*(Prefer running the backend locally instead of in Docker? See "Run backend
without Docker" below.)*

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:5173.

- **Sign up as a patient** to book appointments, use the symptom advisor,
  and view diet tips.
- **Sign up as a doctor** (pick a specialty) to see the "your schedule" view
  instead of the booking tools.
- Or log in with a seeded sample doctor, e.g. `asha.rao@mediconnect.dev` /
  `doctor123` (all seeded doctors share this dev-only password — see
  `app/seed.py`).

## Run backend without Docker

```bash
# 1. Start just Postgres
docker compose up -d db

# 2. Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

## Project layout

```
mediconnect/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, router wiring, /health
│   │   ├── database.py      # SQLAlchemy engine/session
│   │   ├── config.py        # env-based settings
│   │   ├── models.py        # User, Doctor, Appointment, Symptom, Disease
│   │   ├── schemas.py       # Pydantic request/response models
│   │   ├── auth.py          # password hashing, JWT, role-based deps
│   │   ├── seed.py          # sample doctors + symptom/disease lookup data
│   │   └── routers/
│   │       ├── auth.py          # signup, login, /me
│   │       ├── doctors.py       # list/filter, get, available slots
│   │       ├── appointments.py  # book (conflict-checked), list mine, cancel
│   │       └── symptoms.py      # symptom→specialty lookup, disease tips
│   ├── alembic/              # migrations
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/                 # React (Vite)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js            # axios client, attaches JWT from localStorage
│   │   └── components/
│   │       ├── AuthForm.jsx
│   │       ├── DoctorList.jsx
│   │       ├── SymptomAdvisor.jsx
│   │       ├── BookingPanel.jsx
│   │       ├── MyAppointments.jsx
│   │       └── DiseaseTips.jsx
│   └── .env.example
├── docker-compose.yml
└── docs/
    └── data-model.md
```

## API reference (quick)

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/auth/signup` | — | role = `patient` or `doctor`; doctors must include `specialty` |
| POST | `/auth/login` | — | returns JWT |
| GET | `/auth/me` | any | |
| GET | `/doctors?specialty=` | — | case-insensitive substring filter |
| GET | `/doctors/{id}/slots?for_date=YYYY-MM-DD` | — | 30-min slots, 9am–5pm, excludes booked times |
| POST | `/appointments` | patient | 409 if the slot was just taken |
| GET | `/appointments/me` | any | patient sees their bookings, doctor sees their schedule |
| POST | `/appointments/{id}/cancel` | owning patient or doctor | |
| GET | `/symptoms/lookup?q=` | — | rule-based symptom → specialty + matching doctors |
| GET | `/diseases` | — | list of conditions with tips available |
| GET | `/diseases/{name}/tips` | — | diet dos/don'ts + general tips |

## Known limitations / next steps if you keep going

- Doctor working hours are fixed (9am–5pm, 30-min slots) — not yet per-doctor configurable.
- Symptom matching is substring-based, not fuzzy/NLP — "ear ache" won't match "ear pain" unless you add it to `seed.py`'s `SYMPTOM_SPECIALTY_MAP`.
- `JWT_SECRET` and the seeded doctor password (`doctor123`) are dev-only placeholders — replace both before any real deployment.
- No password reset / email verification flow.
- No pagination on doctor or appointment lists (fine at seed-data scale, worth adding before real growth).
