from typing import List, Optional, Union
from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    country: str = Field(default="", description="Country name")
    city: str = Field(default="", description="City name")
    address: Optional[str] = Field(default="", description="Specific district, neighborhood or address")


class PriceSchema(BaseModel):
    amount: Optional[float] = Field(default=None, description="Numeric price if available")
    currency: Optional[str] = Field(default=None, description="Currency e.g. SAR, USD, AED, GBP, EUR")
    formatted: Optional[str] = Field(default=None, description="Human readable formatted price")


class ProjectItem(BaseModel):
    id: str = Field(..., description="Unique project or listing ID")
    source: str = Field(..., description="DarGlobal or Wasalt")
    project_name: str = Field(..., description="Name of the project or title of listing")
    description: str = Field(default="", description="Detailed property/project description")
    location: LocationSchema = Field(default_factory=LocationSchema)
    property_type: Optional[str] = Field(default="", description="e.g. Villa, Apartment, Penthouse, Land")
    price: Optional[PriceSchema] = Field(default_factory=PriceSchema)
    bedrooms: Optional[Union[str, int]] = Field(default=None, description="Number of bedrooms or bedroom range")
    bathrooms: Optional[Union[str, int]] = Field(default=None, description="Number of bathrooms")
    area_sqm: Optional[Union[str, float]] = Field(default=None, description="Size or built-up area in sqm")
    amenities: List[str] = Field(default_factory=list, description="List of amenities")
    features: List[str] = Field(default_factory=list, description="Special features")
    project_status: Optional[str] = Field(default="", description="e.g. Off-plan, Under Construction, Completed, For Sale")
    developer: Optional[str] = Field(default="", description="Developer name or partner brand")
    image_urls: List[str] = Field(default_factory=list, description="Publicly available image URLs")
    source_url: str = Field(..., description="Official URL on the source platform")
    scraped_at: str = Field(..., description="Scraping timestamp")


class ProjectListResponse(BaseModel):
    total: int
    page: int = 1
    page_size: int = 20
    projects: List[ProjectItem]
