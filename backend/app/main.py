from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import get_settings
from app.database import connect_db, close_db
from app.routes import auth, workouts, wearables, gyms, basketball, dashboard, uploads

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time gym crowd tracking, workout logging, wearable sync, and pickup basketball finder.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Register routes
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(workouts.router, prefix=settings.API_PREFIX)
app.include_router(wearables.router, prefix=settings.API_PREFIX)
app.include_router(gyms.router, prefix=settings.API_PREFIX)
app.include_router(basketball.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)
app.include_router(uploads.router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": settings.API_PREFIX,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
