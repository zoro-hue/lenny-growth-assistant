# The Lenny Growth Assistant

> A grounded research and operational assistant for product and growth leaders, powered by Lenny's Podcast transcripts with full source traceability, autonomous Pi Coding Agent reasoning, multi-provider inference (OpenAI + Local Ollama), and an editorial frontend interface.

[![Backend Tests](https://img.shields.io/badge/pytest-59%20passed%20(100%25)-2ea44f.svg)](#running-tests)
[![Build Status](https://img.shields.io/badge/frontend-clean%20build-success.svg)](#frontend-setup)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🌟 Key Capabilities

1. **Zero-Fabrication Grounded RAG**:
   - Every growth framework and tactic links to verified episode transcripts with guest names, timestamps, and verbatim quotes.
   - Transparent **"Insufficient Grounded Evidence in Archives"** low-evidence badge when queries are outside Lenny's podcast domain (e.g. crypto tokenomics, unrelated trivia).
2. **Dual-Model Multi-Provider Architecture**:
   - Cloud frontier model: **OpenAI GPT-4o mini**.
   - Offline, privacy-first local model: **Ollama `llama3.2:3b`**.
   - Interactive model switcher with dynamic reachability detection and fallback handling.
3. **Autonomous Pi Coding Agent Framework**:
   - Powered by `@earendil-works/pi-coding-agent` subprocess RPC with bidirectional tool calling.
   - Dedicated tools: `search_lenny_transcripts`, `lookup_episode_source`, `generate_ship30_essay`, `generate_artifact`.
4. **Ship 30 for 30 Writing Skill**:
   - Produces structured 1,250+ word operational essays complete with a viral hook, 2-3 core frameworks, skimmable bullet points, and actionable takeaways.
5. **Interactive Artifact Workbench & Safe Viewer**:
   - Side-by-side workbench for Markdown playbooks and full HTML/CSS calculators/dashboards.
   - Untrusted HTML rendered inside an isolated `<iframe>` with strict sandbox and CSP protections.
6. **Editorial Workstation Ergonomics**:
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

Ingest curated sample transcripts (Casey Winters, Elena Verna, Brian Balfour, Shreyas Doshi):
```bash
python run_ingest.py --sample
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

The system includes **59 comprehensive backend tests** covering the full agent lifecycle, grounding assertions, and live Ollama execution:

```bash
# Run backend tests
python -m pytest backend/tests -v
```

**Test Coverage Summary**:
- **Agent Multi-Provider**: Cloud key handling, Ollama offline handling, fallback state machine (`test_agent_providers.py`)
- **Pi Coding Agent Loop**: Tool registry, chunk accumulation, and zero citation fabrication (`test_agent_service.py`, `test_pi_agent_service.py`)
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
