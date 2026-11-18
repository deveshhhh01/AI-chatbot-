export interface SourceReference {
  title: string;
  source: string;
  url: string;
  snippet?: string;
  location?: string;
  property_type?: string;
  price?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceReference[];
  retrieved_documents?: number;
  timestamp: string;
  isStreaming?: boolean;
}

export interface LocationInfo {
  country: string;
  city: string;
  address?: string;
}

export interface PriceInfo {
  amount?: number | null;
  currency?: string | null;
  formatted?: string | null;
}

export interface ProjectItem {
  id: string;
  source: string;
  project_name: string;
  description: string;
  location: LocationInfo;
  property_type?: string;
  price?: PriceInfo;
  bedrooms?: string | number | null;
  bathrooms?: string | number | null;
  area_sqm?: number | null;
  amenities: string[];
  features: string[];
  project_status?: string;
  developer?: string;
  image_urls: string[];
  source_url: string;
  scraped_at: string;
}

export interface SourcePlatformStats {
  name: string;
  url: string;
  total_records: number;
  countries_covered: string[];
  last_scraped_at?: string | null;
  status: string;
}

export interface SourcesOverview {
  platforms: SourcePlatformStats[];
  total_records: number;
  vector_indexed_chunks: number;
  llm_provider: string;
  active_model: string;
}

export interface HealthStatus {
  status: string;
  app_name: string;
  database: string;
  total_properties_stored: number;
  vector_store_chunks: number;
  active_llm_provider: string;
  llm_provider_config: string;
}
