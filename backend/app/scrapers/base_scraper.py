import re
import json
import time
import random
from pathlib import Path
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from backend.app.core.logging import logger


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]


class BaseScraper(ABC):
    def __init__(self, name: str, base_url: str, delay_range: tuple = (0.5, 1.5)):
        self.name = name
        self.base_url = base_url
        self.delay_range = delay_range
        self.client = httpx.Client(
            timeout=15.0,
            verify=False,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )

    def get_random_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

    def _sleep(self):
        duration = random.uniform(*self.delay_range)
        time.sleep(duration)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=False
    )
    def fetch_page(self, url: str) -> Optional[str]:
        try:
            self._sleep()
            headers = self.get_random_headers()
            response = self.client.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                logger.warning("[%s] 404 Not Found: %s", self.name, url)
                return None
            else:
                logger.warning("[%s] Received status %d for %s", self.name, response.status_code, url)
                return None
        except Exception as e:
            logger.error("[%s] Error fetching %s: %s", self.name, url, str(e))
            raise

    def extract_links(self, html: str, filter_keyword: Optional[str] = None) -> List[str]:
        soup = BeautifulSoup(html, "lxml")
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            full_url = urljoin(self.base_url, href)
            # Ensure domain matches
            if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                if filter_keyword:
                    if filter_keyword.lower() in full_url.lower():
                        links.add(full_url.split("#")[0].split("?")[0])
                else:
                    links.add(full_url.split("#")[0].split("?")[0])
        return sorted(list(links))

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def save_scraped_data(self, data: List[Dict[str, Any]], filepath: str):
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("[%s] Saved %d records to %s", self.name, len(data), filepath)

    @abstractmethod
    def scrape(self, limit: int = 50) -> List[Dict[str, Any]]:
        pass
