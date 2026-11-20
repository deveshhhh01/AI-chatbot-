from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.db import init_db
from backend.app.database.repositories import ProjectRepository
from backend.app.api.routes import health, chat, projects, sources, scraping
from backend.app.ingestion.ingestion_service import IngestionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing DarGlobal & Wasalt AI Backend...")
    # 1. Initialize SQLite database
    init_db()

    # 2. Check if knowledge base is populated, if not perform initial ingestion
    try:
        project_count = ProjectRepository.count_projects()
        logger.info("Database initialized. Existing project count: %d", project_count)
        if project_count == 0:
            logger.info("Knowledge base empty. Performing initial data ingestion...")
            ingestion = IngestionService()
            ingestion.run_full_pipeline(force_scrape=False)
            logger.info("Initial ingestion completed successfully.")
    except Exception as e:
        logger.warning("Auto-ingestion note during startup: %s", e)

    yield
    logger.info("Shutting down DarGlobal & Wasalt AI Backend.")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Enterprise AI Real Estate Intelligence Assistant for DarGlobal and Wasalt platforms.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

# Include API Routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(projects.router, prefix=settings.API_V1_PREFIX)
app.include_router(sources.router, prefix=settings.API_V1_PREFIX)
app.include_router(scraping.router, prefix=settings.API_V1_PREFIX)

# Serve Frontend static assets if available (Full-stack single container mode)
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "message": "Welcome to DarGlobal & Wasalt AI Real Estate Intelligence API",
            "docs": "/docs",
            "health": f"{settings.API_V1_PREFIX}/health"
        }
