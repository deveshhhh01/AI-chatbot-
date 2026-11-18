from fastapi import Header, HTTPException, status
from backend.app.rag.rag_pipeline import RAGPipeline
from backend.app.ingestion.ingestion_service import IngestionService
from backend.app.core.config import settings

_pipeline_instance = None
_ingestion_instance = None


def get_rag_pipeline() -> RAGPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RAGPipeline()
    return _pipeline_instance


def get_ingestion_service() -> IngestionService:
    global _ingestion_instance
    if _ingestion_instance is None:
        _ingestion_instance = IngestionService()
    return _ingestion_instance


def verify_admin_secret(x_admin_secret: str = Header(default="")):
    if not x_admin_secret or x_admin_secret != settings.ADMIN_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Admin-Secret header."
        )
    return True
