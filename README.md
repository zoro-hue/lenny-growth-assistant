# The Lenny Growth Assistant

> A grounded research and operational assistant for product and growth leaders, powered by Lenny's Podcast transcripts with full source traceability, autonomous Pi Coding Agent reasoning, multi-provider inference (OpenAI + Local Ollama), and an editorial frontend interface.

[![Backend Tests](https://img.shields.io/badge/pytest-69%20passed%20(100%25)-2ea44f.svg)](#running-tests)
[![Build Status](https://img.shields.io/badge/frontend-clean%20build-success.svg)](#frontend-setup)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🌟 Key Capabilities

1. **Speaker-Aware & Zero-Fabrication RAG**:
   - Explicit speaker mentions (e.g. Brian Balfour, Elena Verna) prioritize matching transcript chunks while preserving corroborating evidence.
   - Qualitative **evidence-strength indicators** (`HIGH EVIDENCE`, `LIMITED EVIDENCE`, `NOT GROUNDED`) without fabricated percentage scores.
   - **Focused Source Explorer** displaying speaker, episode, timestamp, verified quote, and contextual *"Why this source?"* explanation.
2. **Dual-Speaker Perspective Comparison (`compare_perspectives`)**:
   - Compare contrasting frameworks (e.g. Brian Balfour vs Elena Verna on growth loops) with structured points of agreement, divergence, and operational synthesis backed by authentic transcript evidence.
3. **Contextual Action Follow-Ups ("Explore this further")**:
   - Dynamic, deterministic follow-up chips routing directly to normal chat flow, Compare Perspectives, Ship 30 essays, or playbook artifact generation.
4. **Professional Demo Seed Environment**:
   - Single-command seed/reset mechanism populating 6 curated growth research conversations (`Today` and `Yesterday`) without fake production data.
5. **Dual-Model Multi-Provider Architecture**:
   - Cloud frontier model: **OpenAI GPT-4o mini**.
   - Offline, privacy-first local model: **Ollama `llama3.2:3b`**.
   - Interactive model switcher with dynamic reachability detection and fallback handling.
6. **Autonomous Pi Coding Agent Framework**:
   - Powered by `@earendil-works/pi-coding-agent` subprocess RPC with bidirectional tool calling.
   - Dedicated tools: `search_lenny_transcripts`, `lookup_episode_source`, `compare_perspectives`, `generate_ship30_essay`, `generate_artifact`.
7. **Ship 30 for 30 Writing Skill**:
   - Produces structured 1,250+ word operational essays complete with a viral hook, 2-3 core frameworks, skimmable bullet points, and actionable takeaways.
8. **Interactive Artifact Workbench & Safe Viewer**:
   - Side-by-side workbench for Markdown playbooks and full HTML/CSS calculators/dashboards.
   - Untrusted HTML rendered inside an isolated `<iframe>` with strict sandbox and CSP protections.
9. **Editorial Workstation Ergonomics**:
   - Responsive 3-pane layout with a **collapsible left sidebar** (240px to 56px icon rail).
   - Full conversation lifecycle: **inline renaming** and **safe deletion with confirmation**.
   - Keyboard shortcuts (`⌘N` New Chat, `⌘B` Toggle Sidebar, `⌘.` Toggle Workbench, `⌘M` Model Switcher).

---

## 🏗 System Topology

```mermaid
flowchart TD
    User([Growth Leader / Operator]) --> Frontend[React 18 + TS Editorial UI (Port 3000)]
    Frontend --> ModelSelector{Model Selector}
    
    ModelSelector -->|POST /api/chat| ChatService[FastAPI Chat Service]
    ModelSelector -->|GET /api/models| ModelsRouter[Models API Router]
    
    ChatService --> AgentService[Pi Coding Agent Service]
    AgentService --> PiRPC[Pi RPC Subprocess Bridge]
    
    PiRPC --> ProviderManager{Provider Manager}
    ProviderManager -->|Cloud| OpenAIProvider[OpenAI (gpt-4o-mini)]
    ProviderManager -->|Local| OllamaProvider[Ollama (llama3.2:3b)]
    
    PiRPC --> ToolBridge[Lenny Tool Extensions]
    ToolBridge --> ToolSearch[search_lenny_transcripts]
    ToolBridge --> ToolShip30[generate_ship30_essay]
    ToolBridge --> ToolArtifact[generate_artifact]
    
    ToolSearch --> RAG[Retrieval Service]
    RAG --> VectorDB[(PostgreSQL pgvector / SQLite Fallback)]
    
    AgentService --> ChatResponse[Grounded Response + Zero-Fabrication Citations]
    ChatResponse --> Frontend
    ChatResponse --> Workbench[Artifact Workbench (440px Panel)]
```

---

## 🚀 Quick Start (One-Command Startup)

### Option A: Docker Compose (Recommended)

Start the entire stack (PostgreSQL with pgvector, FastAPI Backend, and React Frontend) with a single command:

```bash
docker-compose up --build
```

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

---

### Option B: Local Developer Startup

#### 1. Prerequisites
- **Python**: 3.10+
- **Node.js**: 18+
- **Ollama** (optional for local offline mode): `ollama run llama3.2:3b`

#### 2. Backend Setup
```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
```

Run database migrations:
```bash
alembic upgrade head
```

Ingest curated sample transcripts (Casey Winters, Elena Verna, Brian Balfour, Shreyas Doshi, Rahul Vohra):
```bash
python run_ingest.py --sample
```

Seed professional research demo conversations (6 curated sessions):
```bash
python -m backend.app.scripts.seed_demo --reset
```

Start the backend server:
```bash
python run.py
```
Backend runs at `http://localhost:8000`.

#### 3. Frontend Setup
In the root directory:
```bash
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🌐 Production Deployment Guide (Railway + Vercel)

This application is engineered for turnkey production deployment with a decoupled frontend and backend:

* **Frontend**: Hosted on **Vercel** (React 19 + TypeScript + Vite SPA)
* **Backend**: Hosted on **Railway** (FastAPI + Python 3.11 + Docker)
* **Database**: **Railway PostgreSQL** with `pgvector` extension
* **Cloud LLM**: **OpenAI** (`gpt-4o-mini` + `text-embedding-3-small`)
* **Local Ollama**: Preserved for local developer demo environments

```mermaid
flowchart LR
    Browser([End User Browser]) -->|HTTPS| Vercel[Vercel Frontend (SPA)]
    Vercel -->|VITE_API_URL / REST + SSE| Railway[Railway FastAPI Backend]
    Railway -->|DATABASE_URL / asyncpg| RailwayPG[(Railway PostgreSQL + pgvector)]
    Railway -->|HTTPS / API Key| OpenAI[OpenAI API (gpt-4o-mini & embeddings)]
```

---

### Step 1: Deploy Database & Backend on Railway

1. **Create a Railway Project**:
   - Go to [railway.com](https://railway.com/) and create a new project (**New Project**).
   - Click **New Service** -> **Database** -> **Add PostgreSQL**.
   - In PostgreSQL service settings, verify pgvector is enabled (Railway PostgreSQL enables `vector` automatically; backend also runs `CREATE EXTENSION IF NOT EXISTS vector;` on startup).

2. **Deploy the Backend Service**:
   - Click **New Service** -> **GitHub Repo** -> select `lenny-growth-assistant`.
   - Railway will automatically detect `railway.json` and use `backend/Dockerfile`.
   - Under **Variables**, configure the following environment variables:

| Variable | Value / Description | Required |
| :--- | :--- | :--- |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (Select from Railway Reference Variable) | **Yes** |
| `APP_ENV` | `production` | **Yes** |
| `DEBUG` | `false` | **Yes** |
| `OPENAI_API_KEY` | `sk-proj-...` (Your OpenAI production API key) | **Yes** |
| `OPENAI_MODEL` | `gpt-4o-mini` | Optional (default: `gpt-4o-mini`) |
| `CLOUD_MODEL` | `gpt-4o-mini` | Optional (default: `gpt-4o-mini`) |
| `EMBEDDING_PROVIDER` | `openai` | **Yes** (or `auto`) |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Optional (default: `text-embedding-3-small`) |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app` (Add your Vercel URL once deployed) | Optional (`*.vercel.app` auto-allowed) |
| `PORT` | Set automatically by Railway (defaults to `8000`) | Railway default |

3. **Database Migrations & Auto-Seeding**:
   - Alembic migrations run automatically on deploy via `railway.json`.
   - On the very first startup, the backend checks chunk count: if 0 chunks exist, it automatically ingests the sample transcripts into PostgreSQL with pgvector embeddings so the service is immediately functional.

4. **Verify Backend Health**:
   - In Railway, click **Settings** -> **Generate Domain** (e.g. `https://lenny-backend.up.railway.app`).
   - Visit `https://lenny-backend.up.railway.app/health` in your browser.
   - You will receive:
     ```json
     {"status": "ok", "database": "connected", "db_dialect": "postgresql", "version": "1.0.0"}
     ```

---

### Step 2: Deploy Frontend on Vercel

1. **Import Repository to Vercel**:
   - Go to [vercel.com](https://vercel.com/) and click **Add New...** -> **Project**.
   - Select `lenny-growth-assistant` from your GitHub accounts.

2. **Configure Build Settings**:
   - **Framework Preset**: Vite
   - **Root Directory**: `./`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

3. **Add Environment Variable**:
   - Under **Environment Variables**, add:
     - **Name**: `VITE_API_URL`
     - **Value**: Your Railway backend domain, e.g. `https://lenny-backend.up.railway.app` (no trailing slash).

4. **Deploy**:
   - Click **Deploy**. Vercel will build and deploy the React 19 SPA.
   - Routing rewrites and asset caching are handled automatically by `vercel.json`.

5. **Final Production Verification**:
   - Open your deployed Vercel URL (e.g. `https://lenny-growth-assistant.vercel.app`).
   - Notice the connection pill in the header: **API Connected (PostgreSQL)**.
   - Select **Cloud (GPT-4o mini)** or run an inquiry:
     > *"What does Brian Balfour say about growth loops vs funnels?"*
   - Verify grounded citations, transcript audio-jump timestamp links, and artifact workbench rendering.

---

## ⚙️ Configuration & Environment Variables

Copy `.env.example` to `.env`. Key options:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_growth` |
| `SQLITE_FALLBACK_URL` | Local SQLite fallback database | `sqlite+aiosqlite:///./lenny_growth.db` |
| `EMBEDDING_PROVIDER` | Vector embedding engine (`auto`, `openai`, `ollama`, `mock`) | `mock` |
| `OPENAI_API_KEY` | OpenAI API key for cloud inference | Empty (uses local Ollama by default) |
| `OPENAI_MODEL` | Cloud model name | `gpt-4o-mini` |
| `OLLAMA_BASE_URL` | Local Ollama daemon endpoint | `http://localhost:11434` |
| `OLLAMA_MODEL` | Local Ollama model name | `llama3.2:3b` |
| `MODEL_FALLBACK_ENABLED` | Seamless fallback between providers on failure | `true` |
| `AGENT_FRAMEWORK` | Autonomous agent framework | `pi_coding_agent` |

---

## 🧪 Verification & Test Suite

The system includes **69 comprehensive backend tests** covering the full agent lifecycle, grounding assertions, and live Ollama execution:

```bash
# Run backend tests
python -m pytest backend/tests -v
```

**Test Coverage Summary**:
- **Speaker-Aware Ranking & Evidence Indicators**: Speaker and episode entity detection, ranking boost without exclusion, qualitative evidence strength labels (`test_speaker_aware_citations.py`)
- **Compare Perspectives**: Dual-speaker grounding, missing evidence handling, zero fabrication (`test_compare_perspectives.py`)
- **Contextual Follow-Up Suggestions**: Deterministic suggestion routing to Compare, Ship 30, and Playbooks (`test_follow_up_suggestions.py`)
- **Demo Seed Persistence**: Seed script execution, idempotent updates, and API endpoint verification (`test_demo_seed.py`)
- **Agent Multi-Provider**: Cloud key handling, Ollama offline handling, fallback state machine (`test_agent_providers.py`)
- **Pi Coding Agent Loop**: Tool registry (5 registered tools), chunk accumulation, and zero citation fabrication (`test_agent_service.py`, `test_pi_agent_service.py`)
- **Ship 30 for 30 Skill**: Essay structure, word count compliance, and citation propagation (`test_ship30_skill.py`)
- **Artifact Generator**: Markdown & HTML generation, sanitization, sandboxed viewing (`test_artifact_generation.py`)
- **Real Ollama Execution**: Live tool-calling and out-of-domain rejection against local Ollama (`test_real_ollama.py`)
- **RAG & Vector Retrieval**: Dialogue chunking, speaker attribution, and thresholding (`test_chunking.py`, `test_retrieval.py`)
- **Session Lifecycle**: Creation, inline renaming, deletion, and cross-session isolation (`test_sessions.py`, `test_isolation.py`)

### Frontend Build Validation
```bash
npm run build
```
Builds cleanly with Vite and TypeScript strict mode.

---

## 📚 Documentation Directory

- 📐 [Architecture & Topology Specification](architecture.md)
- 🎨 [Design Specification & Semantic Tokens](design.md)
- 📋 [Product Requirements Document (PRD)](docs/prd.md)
- 🔍 [Knowledge Base & Ingestion Guide](docs/knowledge-base.md)
- 🛠 [Pi Agent Transcripts & Debugging Decisions](docs/agent_transcripts_and_decisions.md)

---

## 🔒 Security & Safety Note
- **Zero Secrets Committed**: `.gitignore` strictly protects `.env`, databases (`.db`), and cache directories.
- **Untrusted Code Sandboxing**: Generated HTML/CSS artifacts run in isolated iframes with `allow-same-origin` and no script execution by default.
- **No Hallucinated Citations**: The agent is programmatically blocked from emitting citations not present in retrieved knowledge base chunks.
