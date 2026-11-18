import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from backend.app.scrapers.scraping_manager import ScrapingManager
from backend.app.ingestion.document_processor import DocumentProcessor
from backend.app.rag.vector_store import VectorStore
from backend.app.database.repositories import IngestionRepository, ProjectRepository
from backend.app.core.config import settings
from backend.app.core.logging import logger


class IngestionService:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.scraping_manager = ScrapingManager()

    def run_full_pipeline(self, force_scrape: bool = False) -> Dict[str, Any]:
        run_id = f"ingest_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        logger.info("[IngestionService] Starting ingestion pipeline: %s (force_scrape=%s)", run_id, force_scrape)
        IngestionRepository.record_run_start(run_id)

        processed_file = Path(settings.PROCESSED_DATA_DIR) / "real_estate_processed.json"
        
        # If processed data doesn't exist or force_scrape is requested, execute scraping
        if force_scrape or not processed_file.exists():
            logger.info("[IngestionService] Running scrapers for DarGlobal and Wasalt...")
            scraping_stats = self.scraping_manager.run_all()
        
        # Load records from processed storage
        if not processed_file.exists():
            raise FileNotFoundError(f"Processed file {processed_file} not found after scraping.")

        with open(processed_file, "r", encoding="utf-8") as f:
            all_records = json.load(f)

        logger.info("[IngestionService] Loaded %d real estate records for chunking and embedding.", len(all_records))
        
        # Process and chunk documents
        all_chunks = []
        dg_count = 0
        wasalt_count = 0

        for record in all_records:
            source = record.get("source", "")
            if source == "DarGlobal":
                dg_count += 1
            elif source == "Wasalt":
                wasalt_count += 1

            # Ensure upserted in SQLite
            ProjectRepository.upsert_project(record)

            # Generate chunks
            chunks = self.processor.process_project_record(record)
            all_chunks.extend(chunks)

        logger.info("[IngestionService] Generated %d total chunks from %d records.", len(all_chunks), len(all_records))

        # Upsert into ChromaDB
        upserted_count = VectorStore.upsert_chunks(all_chunks)

        # Record completion
        IngestionRepository.record_run_complete(
            run_id=run_id,
            darglobal_count=dg_count,
            wasalt_count=wasalt_count,
            total_chunks=upserted_count,
            status="completed"
        )

        return {
            "run_id": run_id,
            "status": "completed",
            "darglobal_records": dg_count,
            "wasalt_records": wasalt_count,
            "total_records": len(all_records),
            "chunks_upserted": upserted_count,
            "vector_store_total": VectorStore.count()
        }
