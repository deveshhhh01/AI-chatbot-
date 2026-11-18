from typing import List
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from backend.app.core.logging import logger


class EmbeddingManager:
    _instance = None
    _fn = None

    @classmethod
    def get_embedding_function(cls):
        if cls._fn is None:
            try:
                logger.info("[EmbeddingManager] Initializing ONNX all-MiniLM-L6-v2 embedding function...")
                cls._fn = DefaultEmbeddingFunction()
                logger.info("[EmbeddingManager] Embedding function initialized successfully.")
            except Exception as e:
                logger.error("[EmbeddingManager] Error initializing default embedding function: %s", e)
                raise e
        return cls._fn

    @classmethod
    def embed_texts(cls, texts: List[str]) -> List[List[float]]:
        fn = cls.get_embedding_function()
        return fn(texts)

    @classmethod
    def embed_query(cls, query: str) -> List[float]:
        fn = cls.get_embedding_function()
        res = fn([query])
        return res[0]
