import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from backend.app.scrapers.darglobal_scraper import DarGlobalScraper
from backend.app.scrapers.wasalt_scraper import WasaltScraper
from backend.app.database.repositories import ProjectRepository, IngestionRepository
from backend.app.core.config import settings
from backend.app.core.logging import logger


class ScrapingManager:
    def __init__(self):
        self.darglobal_scraper = DarGlobalScraper()
        self.wasalt_scraper = WasaltScraper()

    def run_all(self, darglobal_limit: int = 25, wasalt_limit: int = 25) -> Dict[str, Any]:
        run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        IngestionRepository.record_run_start(run_id)
        logger.info("[ScrapingManager] Starting coordinated scraping run: %s", run_id)

        try:
            # Scrape DarGlobal
            darglobal_items = self.darglobal_scraper.scrape(limit=darglobal_limit)
            raw_dg_path = Path(settings.RAW_DATA_DIR) / "darglobal_raw.json"
            self.darglobal_scraper.save_scraped_data(darglobal_items, str(raw_dg_path))

            # Scrape Wasalt
            wasalt_items = self.wasalt_scraper.scrape(limit=wasalt_limit)
            raw_wasalt_path = Path(settings.RAW_DATA_DIR) / "wasalt_raw.json"
            self.wasalt_scraper.save_scraped_data(wasalt_items, str(raw_wasalt_path))

            # Combine and deduplicate
            all_items = []
            seen_ids = set()
            seen_urls = set()

            for item in darglobal_items + wasalt_items:
                iid = item.get("id")
                url = item.get("source_url")
                if iid in seen_ids or url in seen_urls:
                    continue
                seen_ids.add(iid)
                seen_urls.add(url)
                all_items.append(item)
                # Store in SQLite database
                ProjectRepository.upsert_project(item)

            # Save processed combined dataset
            processed_path = Path(settings.PROCESSED_DATA_DIR) / "real_estate_processed.json"
            processed_path.parent.mkdir(parents=True, exist_ok=True)
            with open(processed_path, "w", encoding="utf-8") as f:
                json.dump(all_items, f, indent=2, ensure_ascii=False)

            stats = {
                "run_id": run_id,
                "darglobal_count": len(darglobal_items),
                "wasalt_count": len(wasalt_items),
                "total_unique_records": len(all_items),
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success"
            }
            logger.info("[ScrapingManager] Scraping finished successfully. Summary: %s", stats)
            return stats
        except Exception as e:
            logger.error("[ScrapingManager] Scraping failed: %s", e)
            IngestionRepository.record_run_complete(
                run_id=run_id,
                darglobal_count=0,
                wasalt_count=0,
                total_chunks=0,
                status="failed",
                error_message=str(e)
            )
            raise e
