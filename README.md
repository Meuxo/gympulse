# GymPulse

Track workouts, check gym crowds, and find pickup basketball — all in one place.

Built with React + FastAPI + MongoDB. Deployed on Vercel (frontend) and Render (backend).

**Live:** https://frontend-brown-two-55.vercel.app
**API:** https://gympulse-vrna.onrender.com/docs

## What it does

- Log workouts with exercises, sets, reps, weight
- See how busy a gym is right now (crowdsourced reports with time-decay weighting)
- Popular times charts for each gym (like Google Maps)
- Find basketball courts and see who's playing
- Search any gym in the US via Google Places
- Sync wearable data (Fitbit OAuth, Apple Health, Samsung Health)

## Running locally

You need Python 3.11+, Node 18+, and MongoDB.

```bash
# backend
cd backend
python -m venv venv && venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
python seed.py                                # creates demo data
uvicorn app.main:app --reload --port 8000

# frontend (new terminal)
cd frontend
npm install
npm run dev
```

Demo login: `demo@gympulse.com` / `password123`

## Stack

- **Frontend:** React 18, Vite, React Router, Recharts, Axios
- **Backend:** FastAPI, Motor (async MongoDB), Pydantic
- **Auth:** JWT access/refresh tokens, bcrypt
- **Database:** MongoDB with geospatial indexes
- **Deployment:** Vercel (static) + Render (Docker) + MongoDB Atlas

## Project layout

```
backend/
  app/
    main.py           # FastAPI app, CORS, route registration
    config.py         # env-based settings (pydantic-settings)
    database.py       # MongoDB connection + index creation
    auth/jwt.py       # password hashing, token create/verify
    models/           # pydantic schemas (user, workout, gym, wearable)
    routes/           # API endpoints
    services/         # Google Places client, wearable providers
    utils/helpers.py  # time decay math, serialization
  seed.py             # populates DB with sample data
  Dockerfile

frontend/
  src/
    pages/            # Dashboard, Gyms, Workouts, Basketball, Explore, etc.
    components/       # Layout, PopularTimes, BusyLevelBadge, etc.
    services/api.js   # axios client with JWT interceptors
    context/          # auth state
```

## Environment variables

Copy `.env.example` to `backend/.env` and fill in:

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGODB_URL` | yes | MongoDB connection string |
| `JWT_SECRET_KEY` | yes | random string for signing tokens |
| `CORS_ORIGINS` | yes | comma-separated allowed origins |
| `GOOGLE_PLACES_API_KEY` | no | enables gym search via Google |
| `FITBIT_CLIENT_ID` | no | for Fitbit OAuth |
| `FITBIT_CLIENT_SECRET` | no | for Fitbit OAuth |

## How crowd reports work

Each gym has a busyness score from 1 (empty) to 5 (packed). Reports are weighted with exponential decay — a 30-minute half-life means older reports matter less. If no users have reported, the app falls back to estimated patterns based on typical gym traffic.

## Limitations

- Wearable OAuth is only fully implemented for Fitbit (Apple/Samsung are webhook receivers)
- Free tier Render spins down after 15min idle (~30s cold start)
- No real-time updates yet (reports refresh on page load)
- Photo uploads use local storage (not persistent on Render free tier)
