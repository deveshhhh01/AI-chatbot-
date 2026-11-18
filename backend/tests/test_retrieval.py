import pytest
from backend.app.rag.vector_store import VectorStore
from backend.app.rag.retriever import RealEstateRetriever


def test_vector_store_populated():
    count = VectorStore.count()
    assert count > 0, f"Expected vector store to contain documents, found {count}"


def test_retriever_all_sources():
    retriever = RealEstateRetriever(top_k=3)
    res = retriever.retrieve("Dubai branded apartments", source_filter="all")
    assert "documents" in res
    assert len(res["documents"]) > 0
    assert "sources" in res
    assert len(res["sources"]) > 0
    first_src = res["sources"][0]
    assert first_src.url.startswith("http")


def test_retriever_source_filtering():
    retriever = RealEstateRetriever(top_k=3)
    
    # Test Wasalt-only filter
    wasalt_res = retriever.retrieve("Apartments in Riyadh or Jeddah", source_filter="Wasalt")
    for doc in wasalt_res["documents"]:
        assert doc["metadata"]["source"] == "Wasalt"

    # Test DarGlobal-only filter
    dg_res = retriever.retrieve("Villas and luxury towers", source_filter="DarGlobal")
    for doc in dg_res["documents"]:
        assert doc["metadata"]["source"] == "DarGlobal"
