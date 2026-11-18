import pytest
from backend.app.ingestion.data_cleaner import DataCleaner
from backend.app.ingestion.chunker import TextChunker
from backend.app.ingestion.document_processor import DocumentProcessor
from backend.app.rag.embeddings import EmbeddingManager


def test_data_cleaner():
    html = "<div><h1>Title</h1><script>alert(1)</script><p>Text here &nbsp; with space.</p></div>"
    cleaned = DataCleaner.clean_html(html)
    assert "Title" in cleaned
    assert "Text here" in cleaned
    assert "alert" not in cleaned


def test_chunker_basic():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    text = "Sentence one. " * 20
    chunks = chunker.chunk_text(text)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 120


def test_document_processor():
    processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
    sample_item = {
        "id": "dg_test_1",
        "source": "DarGlobal",
        "project_name": "Test Tower",
        "description": "Exclusive penthouse in Downtown Dubai.",
        "location": {"country": "UAE", "city": "Dubai", "address": "Downtown"},
        "property_type": "Penthouse",
        "price": {"amount": 5000000, "currency": "AED", "formatted": "5,000,000 AED"},
        "bedrooms": "4 Bedrooms",
        "bathrooms": "5",
        "amenities": ["Infinity Pool", "Concierge"],
        "developer": "DarGlobal",
        "source_url": "https://darglobal.co.uk/test-tower"
    }

    chunks = processor.process_project_record(sample_item)
    assert len(chunks) >= 1
    first_chunk = chunks[0]
    assert "Test Tower" in first_chunk["text"]
    assert "DarGlobal" in first_chunk["text"]
    assert first_chunk["metadata"]["country"] == "UAE"
    assert first_chunk["metadata"]["source"] == "DarGlobal"


def test_embedding_manager():
    res = EmbeddingManager.embed_texts(["DarGlobal luxury residences", "Wasalt Riyadh apartments"])
    assert len(res) == 2
    assert len(res[0]) == 384
