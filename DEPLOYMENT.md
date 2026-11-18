# Deployment Guide: DarGlobal & Wasalt AI Real Estate Intelligence Chatbot

This document provides step-by-step instructions for deploying the containerized application to production platforms with persistent storage support.

---

## 1. Architecture Overview for Deployment

The application consists of two decoupled services:
1. **Backend Service (`FastAPI`)**:
   - Python 3.12 runtime
   - Embedded persistent vector database (`ChromaDB`)
   - Application metadata & conversation store (`SQLite`)
   - Pre-indexed knowledge base with 79 vector chunks from 39 real scraped properties
   - Modular LLM orchestration (`Google Gemini` or `OpenRouter`)
2. **Frontend Service (`React + Vite + Nginx`)**:
   - Production static build served via Nginx
   - Reverse proxy routing `/api/` traffic to the backend with streaming SSE support

---

## 2. Option A: Deployment on Render (Recommended)

Render supports Docker web services and persistent disk volumes.

### Step 1: Deploy Backend with Persistent Disk
1. Create a **Web Service** on [Render Dashboard](https://dashboard.render.com/).
2. Connect your Git repository.
3. Configure the service:
   - **Environment**: `Docker`
   - **Docker Context**: `.`
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Instance Type**: Starter ($7/mo) or Standard (supports persistent disks)
4. Add a **Persistent Disk**:
   - **Mount Path**: `/app/backend/data`
   - **Size**: 1 GB
5. Configure Environment Variables:
   ```env
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free
   CHROMA_PERSIST_DIR=/app/backend/data/vector_db
   SQLITE_DB_PATH=/app/backend/data/app_metadata.db
   ADMIN_SECRET_KEY=darglobal-admin-secret-2026
   PORT=8000
   ```
6. Deploy and note your backend URL: `https://darglobal-ai-backend.onrender.com`.

### Step 2: Deploy Frontend
1. Create a **Static Site** or **Web Service** on Render.
2. If deploying as Docker Web Service:
   - **Dockerfile Path**: `frontend/Dockerfile`
   - **Docker Context**: `./frontend`
3. Update `frontend/nginx.conf` or configure environment variable `VITE_API_URL` to point to the deployed backend URL.
4. Deploy the frontend.

---

## 3. Option B: Deployment on Railway

Railway natively provisions Docker containers with persistent volume attachments.

### Step 1: Deploy via Docker Compose / Template
1. Create a new project on [Railway.app](https://railway.app/).
2. Select **Deploy from GitHub Repo**.
3. Add a Volume:
   - Name: `data-volume`
   - Mount path: `/app/backend/data`
4. In Railway Settings, set the environment variables:
   - `LLM_PROVIDER`: `gemini` (or `openrouter`)
   - `GEMINI_API_KEY`: `your_key`
   - `GEMINI_MODEL`: `gemini-2.5-flash`
   - `OPENROUTER_API_KEY`: `your_key`
   - `PORT`: `8000`
5. Railway provides a public HTTPS domain: `https://darglobal-production.up.railway.app`.

---

## 4. Option C: Single-Host VPS (DigitalOcean / AWS / Hetzner)

For full control with persistent disk storage:

1. SSH into your VPS:
   ```bash
   ssh root@your-server-ip
   ```
2. Clone repository:
   ```bash
   git clone <repo-url> /opt/darglobal-ai
   cd /opt/darglobal-ai
   ```
3. Copy and edit `.env`:
   ```bash
   cp .env.example .env
   nano .env
   ```
4. Build and run containers:
   ```bash
   docker compose up -d --build
   ```
5. Verify health:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
6. Point your domain (e.g. Nginx with Certbot SSL) to port `3000` (Frontend) and `/api` to port `8000` (Backend).

---

## 5. Production Health & Verification Checklist

Once deployed, verify the following endpoints:

| Endpoint | Expected Status | Purpose |
| :--- | :--- | :--- |
| `GET /api/v1/health` | `200 OK` | Verifies DB, ChromaDB chunk count, and active LLM |
| `GET /api/v1/sources` | `200 OK` | Verifies DarGlobal & Wasalt indexed platform records |
| `GET /api/v1/projects` | `200 OK` | Returns catalog of real scraped properties |
| `POST /api/v1/chat` | `200 OK` | Tests end-to-end RAG response generation |
| `GET /docs` | `200 OK` | Interactive Swagger API documentation |
