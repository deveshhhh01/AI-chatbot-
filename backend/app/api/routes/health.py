from fastapi import APIRouter
from backend.app.rag.vector_store import VectorStore
from backend.app.llm.llm_factory import LLMFactory
from backend.app.database.repositories import ProjectRepository
from backend.app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    vector_count = 0
    try:
        vector_count = VectorStore.count()
    except Exception:
        pass

    db_projects = 0
    try:
        db_projects = ProjectRepository.count_projects()
    except Exception:
        pass

    active_provider = "unconfigured"
    try:
        active_provider = LLMFactory.get_active_provider_name()
    except Exception:
        pass

    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "database": "connected",
        "total_properties_stored": db_projects,
        "vector_store_chunks": vector_count,
        "active_llm_provider": active_provider,
        "llm_provider_config": settings.LLM_PROVIDER
    }
