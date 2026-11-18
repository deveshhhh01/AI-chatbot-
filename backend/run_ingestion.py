import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir.parent))

from backend.app.database.db import init_db
from backend.app.ingestion.ingestion_service import IngestionService
from backend.app.core.logging import logger

if __name__ == "__main__":
    logger.info("Initializing DB and starting full ingestion pipeline...")
    init_db()
    service = IngestionService()
    result = service.run_full_pipeline(force_scrape=True)
    print("\n=== INGESTION PIPELINE RESULT ===")
    import json
    print(json.dumps(result, indent=2))
