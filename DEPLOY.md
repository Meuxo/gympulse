# GymPulse Deployment Guide

## Quick Deploy (3 steps)

### Step 1: Create Free MongoDB Database
1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create a free account (or sign in with Google)
3. Create a **FREE** cluster (M0 Sandbox)
4. Choose any region (US East recommended)
5. Under "Security" → "Database Access": Create a user (e.g., `gympulse` / `gympulse123`)
6. Under "Security" → "Network Access": Click "Allow Access from Anywhere" (0.0.0.0/0)
7. Click "Connect" → "Drivers" → Copy the connection string
   - It looks like: `mongodb+srv://gympulse:gympulse123@cluster0.xxxxx.mongodb.net/gympulse?retryWrites=true&w=majority`

### Step 2: Deploy to Render
1. Go to https://render.com (sign up with GitHub)
2. Click **New** → **Blueprint** → Connect your GitHub repo `Meuxo/gympulse`
3. Render will read the `render.yaml` automatically
4. Fill in the environment variables:
   - `MONGODB_URL`: Paste the MongoDB Atlas connection string from Step 1
   - `CORS_ORIGINS`: `https://gympulse-web.onrender.com` (or whatever your frontend URL is)
   - `FRONTEND_URL`: `https://gympulse-web.onrender.com`
5. Click "Apply" — Render deploys both the API and frontend

### Step 3: Seed the Production Database
```bash
cd backend
MONGODB_URL="mongodb+srv://gympulse:gympulse123@cluster0.xxxxx.mongodb.net/gympulse?retryWrites=true&w=majority" python seed.py
```

## Your Live URLs
- **Frontend**: https://gympulse-web.onrender.com
- **Backend API**: https://gympulse-api.onrender.com
- **API Docs**: https://gympulse-api.onrender.com/docs

## Optional: Google Places API Key
To enable the "Explore" feature (search any gym in the US):
1. Go to https://console.cloud.google.com/apis/credentials
2. Create a project → Enable "Places API (New)"
3. Create an API key
4. Add it as `GOOGLE_PLACES_API_KEY` in Render's environment variables
