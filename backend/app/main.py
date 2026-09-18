"""Open Wearables Personal Trainer - FastAPI Application."""

from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.workouts import router as workouts_router
from app.api.v1.biometrics import router as biometrics_router
from app.api.v1.recommendations import router as recommendations_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Startup/shutdown lifecycle manager."""
    await init_db()
    yield


app = FastAPI(
    title="Open Wearables Personal Trainer",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(workouts_router, prefix="/api/v1")
app.include_router(biometrics_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")


@app.get("/healthz")
async def healthz() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
