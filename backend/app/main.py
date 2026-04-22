"""Main FastAPI application entry point"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, users, websocket, workouts, chat
from app.core.config import settings
from app.core.scheduler import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Create tables
    from app.models.user import Base
    from app.core.database import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start scheduler
    try:
        start_scheduler()
    except Exception as e:
        print(f"Error starting scheduler: {e}")
    yield
    # Shutdown scheduler
    try:
        shutdown_scheduler()
    except Exception as e:
        print(f"Error shutting down scheduler: {e}")

app = FastAPI(
    title="AI Gym Coach API",
    description="Privacy-first real-time workout recognition and smart fitness assistant",
    version="0.1.0",
    lifespan=lifespan
)

# ... (omitted)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(websocket.router)
app.include_router(workouts.router, prefix="/api/workouts", tags=["workouts"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {"message": "AI Gym Coach API", "version": "0.1.0"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )