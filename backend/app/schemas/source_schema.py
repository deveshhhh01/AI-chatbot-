from typing import List, Optional
from pydantic import BaseModel, Field


class SourcePlatformStats(BaseModel):
    name: str = Field(..., description="Platform name")
    url: str = Field(..., description="Main platform website URL")
    total_records: int = Field(default=0, description="Total properties/projects indexed")
    countries_covered: List[str] = Field(default_factory=list, description="Countries covered")
    last_scraped_at: Optional[str] = Field(default=None, description="Last successful scraping timestamp")
    status: str = Field(default="ready", description="Platform ingestion status")


class SourcesOverviewResponse(BaseModel):
    platforms: List[SourcePlatformStats]
    total_records: int
    vector_indexed_chunks: int
    llm_provider: str
    active_model: str


class IngestionTriggerResponse(BaseModel):
    status: str
    message: str
    job_id: str
    started_at: str
