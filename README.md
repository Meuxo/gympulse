# FitTrack - Fitness Tracking MVP

Full-stack fitness application with workout tracking, wearable device integration, gym crowd meter, and basketball court finder.

## Features

- **Workout Tracking** — Log exercises with sets, reps, weight, duration. Filter by type, muscle group, date.
- **Wearable Integration** — Modular support for Fitbit, Apple Health, Samsung Health. Steps, heart rate, calories, sleep.
- **Gym Busy Meter** — Crowdsourced crowd reports with time-weighted decay. 5-level scale (Empty → Packed).
- **Basketball Courts** — Find pickup games. Report player counts, upload photos.
- **Dashboard** — Combined view of today's workouts, wearable stats, gym crowds, basketball reports.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, React Router, Recharts |
| Backend | Python, FastAPI, Pydantic |
| Database | MongoDB (Motor async driver) |
| Auth | JWT (access + refresh tokens), bcrypt |
| File Storage | Local filesystem (swappable to S3) |

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **MongoDB** running on `localhost:27017`

## Quick Start

### 1. Clone and set up environment

```bash
cd fitness-app
cp .env.example backend/.env
```

### 2. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Seed the database

```bash
python seed.py
```

This creates sample users, workouts, gyms, and crowd reports.

**Demo account:** `demo@fittrack.com` / `password123`

### 4. Start the backend

```bash
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Project Structure

```
fitness-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings / env vars
│   │   ├── database.py          # MongoDB connection
│   │   ├── auth/jwt.py          # JWT + password auth
│   │   ├── models/              # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── workout.py
│   │   │   ├── wearable.py
│   │   │   └── gym.py
│   │   ├── routes/              # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── workouts.py
│   │   │   ├── wearables.py
│   │   │   ├── gyms.py
│   │   │   ├── basketball.py
│   │   │   ├── dashboard.py
│   │   │   └── uploads.py
│   │   ├── services/wearables/  # Modular wearable providers
│   │   │   ├── base.py          # Abstract interface
│   │   │   ├── fitbit.py
│   │   │   ├── apple_health.py
│   │   │   ├── samsung_health.py
│   │   │   └── registry.py      # Provider registry
│   │   └── utils/helpers.py     # Time decay, serialization
│   ├── seed.py                  # Database seeder
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Routing
│   │   ├── context/AuthContext   # Auth state management
│   │   ├── services/api.js      # API client
│   │   ├── components/          # Reusable components
│   │   └── pages/               # Page views
│   ├── package.json
│   └── vite.config.js
├── .env.example
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Sign in |
| GET | `/api/auth/me` | Current user profile |
| GET/POST | `/api/workouts/` | List/create workouts |
| GET/PUT/DELETE | `/api/workouts/{id}` | Single workout CRUD |
| GET | `/api/workouts/stats/summary` | Workout statistics |
| POST | `/api/wearables/sync` | Submit wearable data |
| POST | `/api/wearables/sync/batch` | Bulk import |
| GET | `/api/wearables/daily-summary` | Daily aggregated stats |
| GET/POST | `/api/gyms/` | List/create gyms |
| POST | `/api/gyms/{id}/crowd-reports` | Submit crowd report |
| GET | `/api/gyms/{id}/crowd-reports` | Get crowd reports |
| POST | `/api/basketball/reports` | Submit basketball report (with photo) |
| GET | `/api/basketball/reports/{gym_id}` | Get basketball reports |
| GET | `/api/basketball/courts` | List basketball courts |
| GET | `/api/dashboard/summary` | Combined dashboard data |
| POST | `/api/uploads/` | Upload a file |

## Key Design Decisions

**Crowd report decay:** Reports are weighted using exponential decay with a 30-minute half-life. A report from 30 minutes ago counts half as much as a fresh one. This prevents stale data from skewing results.

**Wearable strategy pattern:** Each provider implements `WearableProvider` (base.py). New providers register in `registry.py` and become available automatically — no route changes needed.

**MongoDB:** Chosen for flexible schemas — workouts can have varying exercise structures, wearable data varies by provider, and crowd reports are naturally document-shaped.

## Known Limitations

- Wearable OAuth flows are placeholder implementations (Fitbit is most complete)
- Apple Health requires a native iOS app for HealthKit access
- No real-time updates — crowd reports refresh on page load
- Photo uploads stored locally (not suitable for multi-server deployment)
- No email verification or password reset
- No rate limiting on crowd report submissions

## Future Improvements

- WebSocket for real-time crowd updates
- S3/CloudFront for file storage
- Push notifications for gym crowd alerts
- Social features (friends, shared workouts)
- Workout templates and programs
- Exercise auto-complete with muscle group detection
- Geolocation for nearby gym discovery
- PWA support for mobile install
- Rate limiting and abuse prevention
- Admin dashboard for gym management
