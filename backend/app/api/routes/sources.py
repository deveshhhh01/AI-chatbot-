from fastapi import APIRouter
from backend.app.database.repositories import ProjectRepository, IngestionRepository
from backend.app.rag.vector_store import VectorStore
from backend.app.llm.llm_factory import LLMFactory
from backend.app.schemas.source_schema import SourcesOverviewResponse, SourcePlatformStats
from backend.app.core.config import settings

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get("", response_model=SourcesOverviewResponse)
def get_sources_overview():
    dg_count = ProjectRepository.count_projects(source="DarGlobal")
    wasalt_count = ProjectRepository.count_projects(source="Wasalt")
    total_records = dg_count + wasalt_count
    
    vector_chunks = 0
    try:
        vector_chunks = VectorStore.count()
    except Exception:
        pass

    latest_run = IngestionRepository.get_latest_run()
    last_scraped = latest_run.get("finished_at") if latest_run else None

    platforms = [
        SourcePlatformStats(
            name="DarGlobal",
            url="https://www.darglobal.co.uk",
            total_records=dg_count,
            countries_covered=["United Arab Emirates", "Saudi Arabia", "Oman", "Qatar", "Spain", "United Kingdom"],
            last_scraped_at=last_scraped,
            status="active" if dg_count > 0 else "pending_ingestion"
        ),
        SourcePlatformStats(
            name="Wasalt",
            url="https://wasalt.sa",
            total_records=wasalt_count,
            countries_covered=["Saudi Arabia (Riyadh, Jeddah, Al Khobar, Dammam, Taif, Makkah)"],
            last_scraped_at=last_scraped,
            status="active" if wasalt_count > 0 else "pending_ingestion"
        )
    ]

    return SourcesOverviewResponse(
        platforms=platforms,
        total_records=total_records,
        vector_indexed_chunks=vector_chunks,
        llm_provider=settings.LLM_PROVIDER,
        active_model=LLMFactory.get_active_provider_name()
    )
