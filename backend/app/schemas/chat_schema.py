from typing import List, Optional
from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    title: str = Field(..., description="Project or listing title")
    source: str = Field(..., description="Source platform name (DarGlobal or Wasalt)")
    url: str = Field(..., description="Original URL on the source platform")
    snippet: Optional[str] = Field(default=None, description="Relevant context snippet")
    location: Optional[str] = Field(default=None, description="Location of the property/project")
    property_type: Optional[str] = Field(default=None, description="Type of property")
    price: Optional[str] = Field(default=None, description="Price if available")


class ChatRequest(BaseModel):
    session_id: str = Field(default="default_session", description="Unique conversation session ID")
    message: str = Field(..., min_length=1, description="User's natural language question")
    source_filter: Optional[str] = Field(
        default="all",
        description="Optional filter: 'all', 'DarGlobal', or 'Wasalt'"
    )


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[SourceReference] = []
    retrieved_documents: int = 0
    provider_used: str = "gemini"


class ChatMessageHistoryItem(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")
    timestamp: str = Field(..., description="ISO timestamp")
