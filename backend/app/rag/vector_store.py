from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.app.rag.embeddings import EmbeddingManager
from backend.app.core.config import settings
from backend.app.core.logging import logger


class VectorStore:
    _instance = None
    _client = None
    _collection = None

    @classmethod
    def get_client(cls) -> chromadb.ClientAPI:
        if cls._client is None:
            persist_dir = Path(settings.CHROMA_PERSIST_DIR)
            persist_dir.mkdir(parents=True, exist_ok=True)
            logger.info("[VectorStore] Connecting to ChromaDB persistent storage at %s", persist_dir)
            cls._client = chromadb.PersistentClient(
                path=str(persist_dir),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
        return cls._client

    @classmethod
    def get_collection(cls):
        if cls._collection is None:
            client = cls.get_client()
            embed_fn = EmbeddingManager.get_embedding_function()
            cls._collection = client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                embedding_function=embed_fn,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("[VectorStore] Collection '%s' ready. Current items: %d", settings.CHROMA_COLLECTION_NAME, cls._collection.count())
        return cls._collection

    @classmethod
    def upsert_chunks(cls, chunks: List[Dict[str, Any]]) -> int:
        if not chunks:
            return 0
        collection = cls.get_collection()

        ids = [c["chunk_id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = []
        for c in chunks:
            # Flatten/clean metadata for ChromaDB compatibility
            meta = {}
            for k, v in c["metadata"].items():
                if v is None:
                    meta[k] = ""
                elif isinstance(v, (str, int, float, bool)):
                    meta[k] = v
                else:
                    meta[k] = str(v)
            metadatas.append(meta)

        # Batch upsert in sizes of 100
        batch_size = 100
        total_upserted = 0
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i : i + batch_size]
            batch_docs = documents[i : i + batch_size]
            batch_meta = metadatas[i : i + batch_size]
            collection.upsert(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta
            )
            total_upserted += len(batch_ids)

        logger.info("[VectorStore] Successfully upserted %d chunks. Total collection size: %d", total_upserted, collection.count())
        return total_upserted

    @classmethod
    def similarity_search(
        cls,
        query: str,
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        collection = cls.get_collection()
        total_docs = collection.count()
        if total_docs == 0:
            logger.warning("[VectorStore] Vector store is empty.")
            return []

        actual_k = min(top_k, total_docs)
        kwargs = {
            "query_texts": [query],
            "n_results": actual_k
        }
        if where_filter:
            kwargs["where"] = where_filter

        try:
            results = collection.query(**kwargs)
        except Exception as e:
            logger.error("[VectorStore] Query failed with filter %s: %s. Retrying without filter.", where_filter, e)
            kwargs.pop("where", None)
            results = collection.query(**kwargs)

        items = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            ids = results["ids"][0] if "ids" in results else [""] * len(docs)

            for i in range(len(docs)):
                # Convert cosine distance to similarity score
                # In cosine space: distance = 1 - cosine_similarity
                distance = dists[i] if i < len(dists) else 1.0
                similarity = max(0.0, 1.0 - distance)
                items.append({
                    "chunk_id": ids[i],
                    "text": docs[i],
                    "metadata": metas[i],
                    "similarity": round(similarity, 4),
                    "distance": round(distance, 4)
                })

        return items

    @classmethod
    def count(cls) -> int:
        return cls.get_collection().count()
