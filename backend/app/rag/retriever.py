from typing import List, Dict, Any, Optional
from backend.app.rag.vector_store import VectorStore
from backend.app.schemas.chat_schema import SourceReference
from backend.app.core.config import settings
from backend.app.core.logging import logger


class RealEstateRetriever:
    def __init__(
        self,
        top_k: int = settings.TOP_K_RETRIEVAL,
        threshold: float = settings.SIMILARITY_THRESHOLD
    ):
        self.top_k = top_k
        self.threshold = threshold

    def retrieve(
        self,
        query: str,
        source_filter: Optional[str] = "all",
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        k = top_k or self.top_k
        where_filter = None

        if source_filter and source_filter.lower() != "all":
            if "darglobal" in source_filter.lower():
                where_filter = {"source": "DarGlobal"}
            elif "wasalt" in source_filter.lower():
                where_filter = {"source": "Wasalt"}

        logger.info("[Retriever] Searching for: '%s' (filter=%s, top_k=%d)", query, where_filter, k)
        raw_results = VectorStore.similarity_search(query=query, top_k=k, where_filter=where_filter)

        # Filter by threshold while preserving the best matching result
        filtered_results = []
        for doc in raw_results:
            sim = doc.get("similarity", 0.0)
            if sim >= self.threshold or len(filtered_results) == 0:
                filtered_results.append(doc)

        sources: List[SourceReference] = []
        seen_urls = set()

        for item in filtered_results:
            meta = item.get("metadata", {})
            url = meta.get("source_url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)

            snippet = item.get("text", "")[:280] + "..." if len(item.get("text", "")) > 280 else item.get("text", "")
            sources.append(SourceReference(
                title=meta.get("project_name") or "Real Estate Property",
                source=meta.get("source") or "Verified Data",
                url=url,
                snippet=snippet,
                location=f"{meta.get('city', '')}, {meta.get('country', '')}".strip(", "),
                property_type=meta.get("property_type", ""),
                price=meta.get("price_formatted", "")
            ))

        return {
            "documents": filtered_results,
            "sources": sources,
            "retrieved_count": len(filtered_results)
        }
