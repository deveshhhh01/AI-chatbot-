# System Architecture: DarGlobal & Wasalt Real Estate Intelligence Chatbot

## 1. Executive Summary

The **DarGlobal & Wasalt Real Estate Intelligence Assistant** is an enterprise-grade AI chatbot platform designed to retrieve, synthesize, and present factual real estate intelligence from two premier property ecosystems:
1. **DarGlobal** (International luxury developer across UAE, Saudi Arabia, Oman, Qatar, Spain, UK).
2. **Wasalt** (Leading Saudi Arabian property marketplace with verified listings across Riyadh, Jeddah, Al Khobar, Dammam, and Makkah).

The application enforces a **Strict Anti-Hallucination Retrieval-Augmented Generation (RAG)** protocol, ensuring that all property specifications, pricing figures, locations, and amenities are directly grounded in authentic data collected from the source platforms.

---

## 2. End-to-End System Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                  USER / CLIENT                                    |
|              (React 19 + TypeScript + Vite + Tailwind CSS + Lucide)               |
+-----------------------------------------------------------------------------------+
                                   |          ^
                  HTTP REST / SSE  |          | Streaming Response / Source Cards
                                   v          |
+-----------------------------------------------------------------------------------+
|                                FASTAPI BACKEND                                    |
|                                                                                   |
|  +--------------------+   +---------------------+   +--------------------------+  |
|  | /api/v1/chat       |   | /api/v1/projects    |   | /api/v1/sources          |  |
|  | /api/v1/chat/stream|   | /api/v1/health      |   | /api/v1/admin/ingest     |  |
|  +--------------------+   +---------------------+   +--------------------------+  |
|                                   |                                               |
|                    RAG Pipeline & Orchestration Layer                             |
|  +-----------------------------------------------------------------------------+  |
|  | 1. Session Context & Conversational History (SQLite: messages/conversations)|  |
|  | 2. Context-Aware Query Rewriter (Resolves pronouns & multi-turn intent)     |  |
|  | 3. Semantic Similarity Retrieval (Cosine HNSW Search)                       |  |
|  | 4. Metadata Filtering (Source: All | DarGlobal | Wasalt)                   |  |
|  | 5. Grounded Prompt Assembly (Strict anti-hallucination template)            |  |
|  +-----------------------------------------------------------------------------+  |
|            |                                              |                       |
|            v                                              v                       |
|  +----------------------------+             +----------------------------------+  |
|  |   MODULAR LLM FACTORY      |             |   PERSISTENT VECTOR STORE        |  |
|  |                            |             |   (ChromaDB + ONNX MiniLM-L6-V2) |  |
|  |  +----------------------+  |             |                                  |  |
|  |  | GeminiProvider       |  |             |  79 Indexed Chunks               |  |
|  |  | (Official google-genai) |             |  39 Real Scraped Properties      |  |
|  |  +----------------------+  |             +----------------------------------+  |
|  |  | OpenRouterProvider   |  |                           ^                       |
|  |  | (OpenAI-compatible)  |  |                           |                       |
|  |  +----------------------+  |             +----------------------------------+  |
|  +----------------------------+             |   INGESTION & CLEANING PIPELINE  |  |
|                                             |  - HTML Stripping (BeautifulSoup)|  |
|                                             |  - Chunking (800 / 120 tokens)   |  |
|                                             |  - Metadata Normalization        |  |
|                                             +----------------------------------+  |
|                                                           ^                       |
|                                                           |                       |
|                                             +----------------------------------+  |
|                                             |   SCRAPING SUBSYSTEM             |  |
|                                             |  - DarGlobalScraper (Sitemap)    |  |
|                                             |  - WasaltScraper (llms.txt API)  |  |
|                                             +----------------------------------+  |
+-----------------------------------------------------------------------------------+
                                   |                       |
                                   v                       v
                      +-----------------------+ +---------------------+
                      | https://darglobal.co.uk| | https://wasalt.sa   |
                      +-----------------------+ +---------------------+
```

---

## 3. Data Flow Lifecycle

### 3.1 Scraping & Ingestion Phase
1. **Robots.txt & LLM Policy Check**:
   - Wasalt explicitly permits AI and LLM extraction via its public `https://wasalt.sa/llms.txt` and `robots.txt`.
   - DarGlobal public project sitemaps (`https://www.darglobal.co.uk/sitemap.xml`) expose 480 verified canonical URLs.
2. **Data Extraction**:
   - `DarGlobalScraper`: Collects project name, developer brand partnerships (Pagani, Missoni, Trump, Lamborghini, Marriott, Aston Martin), location (UAE, Oman, Qatar, Spain, UK, Saudi Arabia), amenities, and descriptions.
   - `WasaltScraper`: Queries sitemap product URLs (`product_sitemap_en_sa.xml.gz`), parses Next.js embedded hydration state (`propertyDetailsV3`), extracting property title, district, city, sale price in SAR, bedroom counts, built-up area in SQM, and gallery photo URLs.
3. **Storage & Normalization**:
   - Raw JSON records saved to `backend/data/raw/`.
   - Processed unified records saved to `backend/data/processed/real_estate_processed.json`.
   - Metadata recorded into SQLite `scraped_projects` table.
4. **Vector Embedding**:
   - `TextChunker` chunks records into 800-character segments with 120-character overlap.
   - `EmbeddingManager` computes 384-dimensional dense vectors using `all-MiniLM-L6-v2`.
   - Stored in persistent ChromaDB collection `real_estate_knowledge`.

---

## 4. Query Resolution & Multi-Turn RAG Pipeline

### Step 1: Request Ingestion
- User submits a natural-language query via `/api/v1/chat` or `/api/v1/chat/stream` with a `session_id` and optional `source_filter`.

### Step 2: Context-Aware Query Rewriting
- `QueryRewriter` inspects the last 4 turns of conversation from SQLite.
- If pronouns ("it", "this", "that project") or short follow-ups ("What amenities does it have?") are detected, the rewriter resolves the referenced entity (e.g., "W Residences Dubai") to create an explicit standalone retrieval query.

### Step 3: Semantic Retrieval
- Vector similarity search runs in cosine distance space against ChromaDB.
- Optional metadata filtering (`source: DarGlobal` or `source: Wasalt`) isolates platform data when requested by the user.
- Results passing the similarity threshold are assembled into structured context blocks.

### Step 4: Strict Anti-Hallucination Prompting
- The context and user query are framed inside the system prompt:
  ```
  CRITICAL RULES:
  1. Base answers ONLY on the provided verified context.
  2. If information is unavailable, output:
     "I couldn't find verified information about this in the available DarGlobal and Wasalt data."
  3. Never invent missing prices, room counts, or availability.
  ```

### Step 5: LLM Execution & Attribution
- The active provider (`GeminiProvider` or `OpenRouterProvider`) generates the response.
- Verifiable `SourceReference` objects (title, platform, URL, snippet, price, location) are returned alongside the text.

---

## 5. Storage Schema

### SQLite Database (`backend/data/app_metadata.db`)
- **`conversations`**: `session_id` (PK), `title`, `created_at`, `updated_at`.
- **`messages`**: `id` (PK), `session_id` (FK), `role`, `content`, `sources_json`, `created_at`.
- **`scraped_projects`**: `id` (PK), `source`, `project_name`, `country`, `city`, `property_type`, `price_amount`, `currency`, `source_url`, `data_json`, `scraped_at`.
- **`ingestion_runs`**: `id` (PK), `run_id`, `status`, `started_at`, `finished_at`, `darglobal_count`, `wasalt_count`, `total_chunks`.

### Vector Database (`backend/data/vector_db`)
- ChromaDB HNSW persistent index storing chunk embeddings, source text, and searchable metadata attributes (`source`, `country`, `city`, `property_type`, `source_url`).
