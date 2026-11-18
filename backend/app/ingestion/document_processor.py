from typing import Dict, Any, List
from backend.app.ingestion.data_cleaner import DataCleaner
from backend.app.ingestion.chunker import TextChunker
from backend.app.core.config import settings


class DocumentProcessor:
    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def process_project_record(self, item: Dict[str, Any]) -> List[Dict[str, Any]]:
        source = item.get("source", "Real Estate")
        name = item.get("project_name", "Untitled")
        loc = item.get("location", {})
        country = loc.get("country", "")
        city = loc.get("city", "")
        address = loc.get("address", "")
        prop_type = item.get("property_type", "")
        developer = item.get("developer", "")
        status = item.get("project_status", "")
        
        price = item.get("price", {})
        price_formatted = price.get("formatted", "Price upon request") if isinstance(price, dict) else "Price upon request"
        
        bedrooms = item.get("bedrooms", "")
        bathrooms = item.get("bathrooms", "")
        area_sqm = item.get("area_sqm", "")
        amenities = item.get("amenities", [])
        features = item.get("features", [])
        raw_description = item.get("description", "")
        clean_description = DataCleaner.normalize_text(raw_description)
        source_url = item.get("source_url", "")

        # Build comprehensive searchable representation
        parts = [
            f"Project/Property Title: {name}",
            f"Source Platform: {source}",
            f"Developer / Brand: {developer or 'N/A'}",
            f"Location: {city}, {country} (Address: {address})",
            f"Property Type: {prop_type or 'Residential'}",
            f"Status: {status or 'Available'}",
            f"Price: {price_formatted}",
        ]
        if bedrooms:
            parts.append(f"Bedrooms: {bedrooms}")
        if bathrooms:
            parts.append(f"Bathrooms: {bathrooms}")
        if area_sqm:
            parts.append(f"Area: {area_sqm} SQM")
        if amenities:
            parts.append(f"Amenities: {', '.join(amenities)}")
        if features:
            parts.append(f"Key Features: {', '.join(features)}")
        parts.append(f"Description: {clean_description}")
        parts.append(f"Official Source URL: {source_url}")

        full_document_text = "\n".join(parts)

        # Base metadata for filtering in vector database
        metadata = {
            "id": str(item.get("id")),
            "source": source,
            "project_name": name,
            "country": country,
            "city": city,
            "property_type": prop_type or "Residential",
            "price_formatted": price_formatted,
            "source_url": source_url,
            "developer": developer or "",
            "status": status or ""
        }

        # Chunk document
        chunks = self.chunker.chunk_document(full_document_text, metadata)
        return chunks
