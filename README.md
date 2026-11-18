# DarGlobal & Wasalt – AI Real Estate Intelligence Chatbot

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.3-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)](https://www.typescriptlang.org/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Persistent-orange.svg)](https://www.trychroma.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-20%2F20%20Passing-success.svg)](backend/tests/)

> Production-grade, containerized AI Real Estate Intelligence Chatbot built for the **DarGlobal technical recruitment assignment**. Collects, indexes, and synthesizes authentic public real estate intelligence from **DarGlobal** and **Wasalt**, answering complex natural-language queries using Retrieval-Augmented Generation (RAG) with verifiable source citations and strict anti-hallucination protocols.

---

## 1. Problem Statement & Solution Overview

### The Challenge
Real estate buyers and investors navigating international luxury developments and regional property markets face fragmented platforms, scattered project brochures, and unreliable estimates. General-purpose LLMs frequently hallucinate property specifications, invent non-existent prices, or fabricate citations.

### The Solution
The **DarGlobal & Wasalt Real Estate Intelligence Assistant** provides a unified, conversational interface backed by a persistent RAG pipeline. The application:
- Scrapes and continuously maintains verified property catalogs from **DarGlobal** (`https://darglobal.co.uk`) and **Wasalt** (`https://wasalt.sa`).
- Translates natural-language user queries into dense vector searches across 79 pre-indexed chunks representing 39 real scraped properties.
- Enforces strict anti-hallucination guardrails: when data is missing or unverified, the assistant explicitly states:
  > *"I couldn't find verified information about this in the available DarGlobal and Wasalt data."*
- Resolves conversational follow-ups and pronoun references across multiple chat turns.
- Renders clickable source cards with direct URLs to the original listings.

---

## 2. Key Features

- **Real Data Sourcing**: Scraped from official public sitemaps and listings adhering to `robots.txt` and `llms.txt`.
- **Modular LLM Architecture**: Pluggable provider system supporting **Google Gemini API** (`google-genai` SDK) and **OpenRouter API** (`meta-llama/llama-3.3-70b-instruct:free`, etc.) with zero code changes.
- **Context-Aware Conversational Memory**: SQLite-backed session history with entity and pronoun query rewriting for multi-turn conversations.
- **Persistent Vector Database**: Embedded ChromaDB with cosine distance indexing and local ONNX `all-MiniLM-L6-v2` embeddings (zero external API cost for embeddings).
- **Source Attribution**: Every factual assertion is accompanied by verified cards displaying the project title, platform tag, price, location, and official URL.
- **Enterprise UI / UX**: Modern real estate visual identity featuring dark navy typography, subtle gold accents, responsive sidebar, filter chips, and SSE streaming.
- **Full Containerization**: Multi-stage Dockerfiles and Docker Compose configuration with volume-persisted vector and metadata storage.
- **Comprehensive Test Suite**: 20 automated unit and integration tests covering scrapers, ingestion, vector store, retriever, LLM providers, and REST endpoints.

---

## 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12+, FastAPI, Pydantic v2, Uvicorn, HTTPX, BeautifulSoup4, Tenacity |
| **AI / RAG** | ChromaDB (Persistent), ONNX all-MiniLM-L6-v2, Google GenAI SDK, OpenRouter API |
| **Database** | SQLite3 (Persistent application metadata, chat history, scraping runs) |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4, Axios, Lucide React |
| **DevOps** | Docker, Docker Compose, Multi-stage builds, Nginx reverse proxy |

---

## 4. System Architecture

```
+-----------------------------------------------------------------------------------+
|                                  USER INTERFACE                                   |
|                React 19 + TypeScript + Vite + Tailwind CSS + Lucide               |
+-----------------------------------------------------------------------------------+
                                   |          ^
                      HTTP REST    |          | Streaming SSE / Verified Source Cards
                                   v          |
+-----------------------------------------------------------------------------------+
|                                FASTAPI BACKEND                                    |
|                                                                                   |
|  [ /api/v1/chat ]    [ /api/v1/projects ]    [ /api/v1/sources ]    [ /health ]   |
|                                   |                                               |
|                    RAG Pipeline & Orchestration Layer                             |
|  +-----------------------------------------------------------------------------+  |
|  | 1. Session Context (SQLite: conversations & messages)                       |  |
|  | 2. Context-Aware Query Rewriter (Resolves follow-ups & pronouns)            |  |
|  | 3. Semantic Similarity Search (ChromaDB Vector Store)                       |  |
|  | 4. Metadata Filtering (Source: All | DarGlobal | Wasalt)                   |  |
|  | 5. Grounded Prompt Assembly (Strict anti-hallucination template)            |  |
|  +-----------------------------------------------------------------------------+  |
|            |                                              |                       |
|            v                                              v                       |
|  +----------------------------+             +----------------------------------+  |
|  |     MODULAR LLM FACTORY    |             |     PERSISTENT VECTOR STORE      |  |
|  |  - GeminiProvider (google) |             |  (ChromaDB + ONNX MiniLM-L6-V2)  |  |
|  |  - OpenRouterProvider      |             |  79 Indexed Chunks               |  |
|  +----------------------------+             |  39 Real Scraped Properties      |  |
|                                             +----------------------------------+  |
|                                                           ^                       |
|                                             +----------------------------------+  |
|                                             |   SCRAPING & INGESTION SERVICE   |  |
|                                             |  - DarGlobalScraper              |  |
|                                             |  - WasaltScraper                 |  |
|                                             +----------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 5. Web Scraping & Ingested Data

The system does not rely on fabricated properties or static mock JSON. Real data was extracted during project initialization:

### DarGlobal Sourcing (`https://darglobal.co.uk`)
- Sourced from official project sitemaps and verified architectural listings:
  - **W Residences Dubai – Downtown** (Downtown Dubai, UAE)
  - **Tierra Viva, Design Inspired by Automobili Lamborghini** (Benahavís, Spain)
  - **DaVinci Tower by Pagani** (Dubai Canal, UAE)
  - **Urban Oasis by Missoni** (Business Bay, UAE)
  - **AIDA 360 Muscat & Marriott Residences** (Muscat, Oman)
  - **Trump Tower Jeddah** (Corniche, Jeddah, Saudi Arabia)
  - **The Astera, Interiors by Aston Martin** (Al Marjan Island, Ras Al Khaimah)
  - **Les Vagues by Elie Saab** (Qetaifan Island North, Qatar)
  - **DG1 Living Residences** (Business Bay, Dubai)
  - **Fendi Casa Azure Oceanfront Villas & Painite Villas**

### Wasalt Sourcing (`https://wasalt.sa`)
- Sourced in compliance with Wasalt's official `https://wasalt.sa/llms.txt` and `product_sitemap_en_sa.xml.gz`:
  - Authentic residential villas, duplexes, and apartments across **Riyadh, Jeddah, Al Khobar, Dammam, and Makkah**.
  - Real prices in SAR (e.g. 120,000 SAR rental villas, 850,000 SAR apartments, 435,000 SAR units).
  - Exact bedroom counts, built-up areas (SQM), and official URLs.

---

## 6. Project Structure

```
DarGlobal/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── chat.py             # Chat & SSE streaming endpoints
│   │   │   │   ├── projects.py         # Property catalog search & filtering
│   │   │   │   ├── sources.py          # Data source stats & platform health
│   │   │   │   ├── scraping.py         # Admin-protected scraping & ingestion trigger
│   │   │   │   └── health.py           # System status & vector count
│   │   │   └── dependencies.py        # Pipeline & security injection
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic v2 application settings
│   │   │   └── logging.py              # Structured logger
│   │   ├── database/
│   │   │   ├── db.py                   # SQLite tables initialization
│   │   │   └── repositories.py         # Repositories for chat, projects, and runs
│   │   ├── ingestion/
│   │   │   ├── chunker.py              # TextChunker (800 / 120 overlap)
│   │   │   ├── data_cleaner.py         # HTML stripping & whitespace normalizer
│   │   │   ├── document_processor.py   # Document processor with metadata
│   │   │   └── ingestion_service.py    # Pipeline coordinator
│   │   ├── llm/
│   │   │   ├── base_provider.py        # Abstract LLM provider interface
│   │   │   ├── gemini_provider.py      # Google GenAI SDK integration
│   │   │   ├── openrouter_provider.py  # OpenRouter API integration
│   │   │   └── llm_factory.py          # Dynamic provider factory
│   │   ├── rag/
│   │   │   ├── embeddings.py           # ONNX all-MiniLM-L6-v2 embedding manager
│   │   │   ├── prompt_templates.py     # Anti-hallucination prompt definitions
│   │   │   ├── query_rewriter.py       # Multi-turn context pronoun resolver
│   │   │   ├── retriever.py            # Cosine similarity retriever with filters
│   │   │   ├── vector_store.py         # Persistent ChromaDB client
│   │   │   └── rag_pipeline.py         # End-to-end RAG orchestrator
│   │   ├── schemas/                    # Pydantic schemas (chat, project, source)
│   │   ├── scrapers/
│   │   │   ├── base_scraper.py         # HTTPX client with retries & user-agents
│   │   │   ├── darglobal_scraper.py    # DarGlobal public project crawler
│   │   │   ├── wasalt_scraper.py       # Wasalt sitemap & Next.js state scraper
│   │   │   └── scraping_manager.py     # Multi-scraper orchestrator
│   │   └── main.py                     # FastAPI entrypoint with CORS & lifespan
│   ├── data/
│   │   ├── raw/                        # Scraped raw JSON files
│   │   ├── processed/                  # Normalized unified records
│   │   └── vector_db/                  # Persistent ChromaDB vector files
│   ├── tests/                          # 20 Unit & integration tests
│   ├── Dockerfile                      # Production Python 3.12-slim image
│   ├── requirements.txt                # Pinned dependencies
│   └── run_ingestion.py                # Standalone ingestion runner script
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInput.tsx           # Input with platform filter & auto-grow
│   │   │   ├── ChatMessage.tsx         # Message bubble with markdown & copy
│   │   │   ├── LoadingIndicator.tsx    # Bouncing pulse search indicator
│   │   │   ├── ProjectCard.tsx         # Property card with image & stats
│   │   │   ├── Sidebar.tsx             # Luxury navigation & platform status
│   │   │   └── SourceCard.tsx          # Clickable source reference card
│   │   ├── pages/
│   │   │   └── ChatPage.tsx            # Main chat screen with suggested prompts
│   │   ├── services/
│   │   │   └── api.ts                  # Axios & SSE streaming client
│   │   ├── types/
│   │   │   └── index.ts                # TypeScript interfaces
│   │   ├── App.tsx                     # Top-level state coordinator
│   │   └── index.css                   # Tailwind CSS v4 styling
│   ├── Dockerfile                      # Multi-stage Node 22 + Nginx image
│   ├── nginx.conf                      # Nginx SPA & reverse proxy configuration
│   └── package.json
│
├── docker-compose.yml                  # Docker Compose configuration
├── .env.example                        # Template for environment variables
├── ARCHITECTURE.md                     # Deep technical architecture documentation
├── DEPLOYMENT.md                       # Production deployment guide
└── README.md
```

---

## 7. Local Installation & Quickstart

### Prerequisites
- Python 3.12+
- Node.js 20+ and npm
- (Optional) Docker & Docker Compose

### 1. Clone Repository & Setup Environment
```bash
git clone <repository-url>
cd DarGlobal
cp .env.example .env
```
Edit `.env` and insert your API credentials:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Optional: To test OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Run backend test suite
pytest backend/tests -v

# Start FastAPI server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API docs are available at: `http://localhost:8000/docs`.

### 3. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 8. Docker & Containerization

Run the complete multi-container system with persistent volume storage:
```bash
docker compose up --build
```
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **Interactive Swagger Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/v1/health`

Vector data (`backend/data/vector_db`) and metadata (`backend/data/app_metadata.db`) persist across container restarts via mounted volumes.

---

## 9. Switching LLM Providers

To switch from Google Gemini to OpenRouter:
1. Update `.env`:
   ```env
   LLM_PROVIDER=openrouter
   OPENROUTER_API_KEY=your_key
   OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free
   ```
2. Restart the backend.
3. The application logs the provider change and routes all prompts through OpenRouter without affecting the RAG pipeline or frontend interface.

---

## 10. Automated Test Results

The project includes 20 comprehensive unit and integration tests:

```
backend/tests/test_api.py::test_health_endpoint PASSED
backend/tests/test_api.py::test_sources_endpoint PASSED
backend/tests/test_api.py::test_projects_endpoint PASSED
backend/tests/test_api.py::test_projects_filter_source PASSED
backend/tests/test_api.py::test_admin_ingest_protection PASSED
backend/tests/test_ingestion.py::test_data_cleaner PASSED
backend/tests/test_ingestion.py::test_chunker_basic PASSED
backend/tests/test_ingestion.py::test_document_processor PASSED
backend/tests/test_ingestion.py::test_embedding_manager PASSED
backend/tests/test_llm.py::test_llm_factory_instantiation PASSED
backend/tests/test_llm.py::test_missing_api_key_handling PASSED
backend/tests/test_llm.py::test_query_rewriter_follow_up PASSED
backend/tests/test_llm.py::test_query_rewriter_standalone PASSED
backend/tests/test_retrieval.py::test_vector_store_populated PASSED
backend/tests/test_retrieval.py::test_retriever_all_sources PASSED
backend/tests/test_retrieval.py::test_retriever_source_filtering PASSED
backend/tests/test_scrapers.py::test_base_scraper_text_cleaning PASSED
backend/tests/test_scrapers.py::test_base_scraper_link_extraction PASSED
backend/tests/test_scrapers.py::test_darglobal_scraper_structure PASSED
backend/tests/test_scrapers.py::test_wasalt_scraper_parsing PASSED

======================= 20 passed in 3.08s =======================
```

---

## 11. API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health, ChromaDB chunk count, and active LLM provider |
| `POST` | `/api/v1/chat` | Non-streaming grounded RAG chat endpoint |
| `POST` | `/api/v1/chat/stream` | Server-Sent Events (SSE) streaming chat endpoint |
| `GET` | `/api/v1/chat/history/{session_id}` | Retrieve persistent conversation history for a session |
| `GET` | `/api/v1/chat/conversations` | List past conversation sessions |
| `GET` | `/api/v1/projects` | Query property catalog with source, country, city, and text filters |
| `GET` | `/api/v1/sources` | Overview of indexed platforms and data coverage statistics |
| `GET` | `/api/v1/admin/scraping/status`| Scraping pipeline execution status |
| `POST` | `/api/v1/admin/ingest` | Trigger background ingestion (requires `X-Admin-Secret` header) |

---

## 12. Deployment Guide

See [DEPLOYMENT.md](file:///c:/Users/New%20Join/Documents/DarGlobal/DEPLOYMENT.md) for detailed deployment steps on:
- **Render** (Docker Web Service + Persistent Disk)
- **Railway** (Docker Compose with Volume attachment)
- **Cloud VPS** (Direct Docker Compose with persistent disk)
