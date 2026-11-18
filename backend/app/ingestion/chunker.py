from typing import List, Dict, Any


class TextChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        if not text:
            return []
        
        if len(text) <= self.chunk_size:
            return [text.strip()]

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size
            if end >= text_len:
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break

            # Try to break at a paragraph or sentence boundary
            boundary = text.rfind("\n\n", start, end)
            if boundary == -1 or boundary <= start:
                boundary = text.rfind(". ", start, end)
            if boundary == -1 or boundary <= start:
                boundary = text.rfind(" ", start, end)
            if boundary == -1 or boundary <= start:
                boundary = end

            chunk = text[start:boundary].strip()
            if chunk:
                chunks.append(chunk)

            start = max(boundary + 1 - self.chunk_overlap, start + 1)

        return chunks

    def chunk_document(self, document_text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw_chunks = self.chunk_text(document_text)
        chunk_objects = []
        for i, chunk_text in enumerate(raw_chunks):
            chunk_meta = dict(metadata)
            chunk_meta["chunk_index"] = i
            chunk_meta["total_chunks"] = len(raw_chunks)
            chunk_objects.append({
                "chunk_id": f"{metadata.get('id', 'doc')}_chunk_{i}",
                "text": chunk_text,
                "metadata": chunk_meta
            })
        return chunk_objects
