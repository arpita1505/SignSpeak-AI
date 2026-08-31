"""FastAPI application factory."""
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import Engine

from app.api import health, history, websocket
from app.config import settings
from app.db.database import init_db, engine as default_engine

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Application starting up...")
    # Skip init_db if we're using test database
    if not hasattr(app, "test_mode"):
        init_db()
        logger.info(f"Database initialized: {settings.db_url}")
    else:
        logger.info("Skipping init_db in test mode")

    # Load model
    from app.api.health import model_service
    if model_service.is_model_loaded():
        logger.info(f"Model loaded: version {model_service.get_model_version()}")
    else:
        logger.warning("Model not loaded - inference will not work")

    yield

    # Shutdown
    logger.info("Application shutting down...")


def create_app(test_mode: bool = False) -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="SignSpeak AI",
        description="Real-Time Indian Sign Language to Text Translator",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # Mark test mode
    if test_mode:
        app.test_mode = True

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(history.router)
    app.include_router(websocket.router)

    # Serve static files (frontend)
    dist_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
    if os.path.exists(dist_path):
        app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")

    return app


app = create_app()

