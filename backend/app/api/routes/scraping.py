import threading
from datetime import datetime
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from backend.app.database.repositories import IngestionRepository, ProjectRepository
from backend.app.rag.vector_store import VectorStore
from backend.app.api.dependencies import get_ingestion_service, verify_admin_secret
from backend.app.ingestion.ingestion_service import IngestionService
from backend.app.schemas.source_schema import IngestionTriggerResponse
from backend.app.core.logging import logger

router = APIRouter(prefix="/admin", tags=["Scraping & Ingestion Administration"])

_ingestion_lock = threading.Lock()


@router.get("/scraping/status")
def get_scraping_status():
    latest_run = IngestionRepository.get_latest_run()
    dg_count = ProjectRepository.count_projects(source="DarGlobal")
    wasalt_count = ProjectRepository.count_projects(source="Wasalt")
    vector_count = VectorStore.count()

    return {
        "status": "idle" if not _ingestion_lock.locked() else "running",
        "latest_run": latest_run,
        "darglobal_properties": dg_count,
        "wasalt_properties": wasalt_count,
        "total_properties": dg_count + wasalt_count,
        "vector_chunks": vector_count,
        "timestamp": datetime.utcnow().isoformat()
    }


def _run_ingestion_task(ingestion_service: IngestionService, force_scrape: bool):
    with _ingestion_lock:
        try:
            logger.info("[BackgroundIngest] Starting ingestion task (force_scrape=%s)", force_scrape)
            result = ingestion_service.run_full_pipeline(force_scrape=force_scrape)
            logger.info("[BackgroundIngest] Ingestion completed: %s", result)
        except Exception as e:
            logger.error("[BackgroundIngest] Ingestion failed: %s", e)


@router.post("/ingest", response_model=IngestionTriggerResponse)
def trigger_ingestion(
    background_tasks: BackgroundTasks,
    force_scrape: bool = Query(default=False, description="Re-run web scrapers before vectorization"),
    authenticated: bool = Depends(verify_admin_secret),
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    if _ingestion_lock.locked():
        return IngestionTriggerResponse(
            status="already_running",
            message="An ingestion job is currently executing.",
            job_id="active",
            started_at=datetime.utcnow().isoformat()
        )

    job_id = f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    background_tasks.add_task(_run_ingestion_task, ingestion_service, force_scrape)

    return IngestionTriggerResponse(
        status="started",
        message="Ingestion pipeline triggered successfully in background.",
        job_id=job_id,
        started_at=datetime.utcnow().isoformat()
    )
