# Architecture Documentation — The Lenny Growth Assistant

*The Lenny Growth Assistant* is a production-grade research and operational assistant for product and growth leaders. It blends an editorial frontend interface with autonomous agent reasoning powered by the **Pi Coding Agent Framework**, a **Multi-Provider LLM Layer** (OpenAI Cloud + Local Ollama `llama3.2:3b`), and pgvector-backed retrieval over Lenny's Podcast archives.

---

## 1. System Architecture & Topology

```mermaid
flowchart TD
    User([User / Growth Operator]) --> Frontend[Editorial React Frontend (Port 3000)]
    Frontend --> ModelSelector{Model Provider Selector}
    
    ModelSelector -->|GET /api/models| ModelsRouter[Models API Router]
    ModelSelector -->|POST /api/chat| ChatService[Chat Service]
    ModelSelector -->|PATCH /api/sessions/:id| SessionService[Session Service]
    
    ChatService --> SessionStore[(Session & Message Store)]
    ChatService --> AgentService[Pi Coding Agent Service]
    
    subgraph AgentLayer ["Pi Coding Agent Layer (backend/app/agent)"]
        AgentConfig[Agent Config & System Directives] --> AgentRunner[Autonomous ReAct Loop]
        AgentRunner --> ProviderRouter{Provider Manager}
        
        ProviderRouter -->|Cloud| OpenAIProvider[OpenAI Provider (gpt-4o-mini)]
        ProviderRouter -->|Local| OllamaProvider[Ollama Provider (llama3.2:3b)]
        ProviderRouter -->|Testing/Mock| MockProvider[Mock Agent Provider]
        
        AgentRunner -->|Tool Execution| ToolRegistry[Tool Registry]
        ToolRegistry --> ToolSearch[search_lenny_transcripts]
        ToolRegistry --> ToolLookup[lookup_episode_source]
        ToolRegistry --> ToolShip30[generate_ship30_essay (Ship 30 Skill)]
        ToolRegistry --> ToolArtifact[generate_artifact (Artifact Generator)]
    end
    
    ToolSearch --> RetrievalService[RAG Retrieval Service]
    ToolShip30 --> RetrievalService
    ToolArtifact --> RetrievalService
    RetrievalService --> Database[(PostgreSQL pgvector / SQLite Fallback)]
    
    ToolSearch -.->|Retrieved Chunks| AgentRunner
    AgentRunner --> ResponseSynthesis[Grounded Synthesis & Citation Extraction]
    ResponseSynthesis --> ChatService
    ChatService --> ArtifactService[Playbook Artifact Service]
    ChatService --> Frontend
```

---

## 2. Multi-Provider Architecture

The application abstracts LLM inference behind `BaseLLMProvider` in [`backend/app/agent/providers.py`](file:///d:/oogway/backend/app/agent/providers.py):

| Provider | Type | Default Model | Configuration | Offline / Error Handling |
| :--- | :--- | :--- | :--- | :--- |
| **OpenAI** | Cloud | `gpt-4o-mini` | `OPENAI_API_KEY`, `OPENAI_MODEL` | Structured `MissingProviderKeyError` with actionable prompt to configure key or switch to Ollama |
| **Ollama** | Local | `llama3.2:3b` | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | Fast TCP reachability check; returns `ProviderUnavailableError` if daemon is offline |
| **Mock** | In-Memory | Deterministic | Built-in test mock | Automatically activated during unit tests if OpenAI key is unset |

### Provider Selection & Fallback Behavior
- Controlled by `MODEL_FALLBACK_ENABLED=false` (default: disabled to prevent masking model failures).
- When enabled (`MODEL_FALLBACK_ENABLED=true`), `ProviderManager` detects provider unavailability and transparently delegates to the secondary provider while capturing:
  - `requested_provider`: original selection (e.g., `ollama`).
  - `actual_provider`: fallback provider (e.g., `openai`).
  - `fallback_reason`: explicit logging and user-visible notification.

---

## 3. Pi Coding Agent Execution Loop

Located in [`backend/app/agent/agent_service.py`](file:///d:/oogway/backend/app/agent/agent_service.py):

1. **Context Assembly**: Concatenates system directives, up to 6 historical conversation turns, and the current user prompt.
2. **Autonomous Tool Selection**: The LLM autonomously issues tool calls if it needs transcript excerpts or episode metadata.
3. **Tool Registry Dispatch**:
   - `search_lenny_transcripts(query: str, top_k: int = 3)`: Runs semantic retrieval via `RetrievalService`.
   - `lookup_episode_source(episode_title_or_guest: str)`: Inspects episode metadata table for audio URLs and publishing dates.
4. **Normalized Tool Arguments**: Converts OpenAI-format JSON string arguments to Python dictionaries when calling Ollama to conform to Ollama's native tool schema.
5. **Zero Citation Fabrication**: Citations are derived exclusively from verified chunks retrieved during tool execution. No hallucinated citations are permitted.
6. **Low-Evidence Detection**: When queries ask for unsupported domains (e.g., crypto/Solana staking) or retrieval yields no matching chunks, the agent responds with clear limitations, zero citations, and sets status to `"low-evidence"`.

---

## 4. Database & Storage Layer

- **Primary**: PostgreSQL 16 + `vector` extension with HNSW cosine similarity index on `transcript_chunks.embedding`.
- **Fallback**: SQLite (`lenny_growth.db`) with in-memory cosine ranking and auto-failover if PostgreSQL daemon is offline.
- **Entities**:
  - `sessions`: Conversation sessions and active model IDs.
  - `messages`: Message turns, citations, role, status (`complete`, `low-evidence`, `error`), and metadata.
  - `artifacts`: Structured Ship 30/30 Playbooks and markdown assets.
  - `transcript_metadata`: Podcast episodes, guest titles, audio URLs, and publishing dates.
  - `transcript_chunks`: Dialogue turns with speaker attribution, timestamps, and vector embeddings.

---

## 5. Ship 30 for 30 Writing Skill (`generate_ship30_essay`)

The dedicated Ship 30 for 30 writing capability is registered as a native Pi Coding Agent skill ([`.pi/skills/ship30-writer/SKILL.md`](file:///.pi/skills/ship30-writer/SKILL.md)) and tool ([`backend/app/agent/tools/ship30_essay.py`](file:///backend/app/agent/tools/ship30_essay.py)):

### Writing Principles Encoded
1. **1-3-1 Hook**: Gripping one-sentence hook, three-sentence context/friction, one-sentence transition.
2. **Single Core Idea**: Every essay develops exactly one governing mental model or growth thesis.
3. **5-Act Narrative Arc**: The Friction/Status Quo, The False Summit, The Pivot/Aha!, The Tactical Architecture, The Compounding Flywheel.
4. **Skimmable Formatting**: Short paragraphs (1-3 sentences max), distinct section headers, bold thematic anchors, bulleted rules of thumb.
5. **Target Word Count**: Calibrated to generate ~1,250 words (typically 1,100 to 1,350 words) with deep analytical rigor.
6. **Strict Transcript Grounding**: Verbatim quotes with speaker attribution and timestamps derived directly from `RetrievalService`. Zero invented quotes or episodes.
7. **Actionable Takeaway**: Concludes with a 3-step Monday morning implementation protocol.
8. **Low Evidence Guardrail**: If asked for unsupported domains (e.g. crypto/web3), immediately returns explicit low-evidence notice with 0 fabricated citations.

---

## 6. Artifact Generation & Safe Artifact Viewer (`generate_artifact`)

Phase 6 implements full-stack artifact generation (Markdown and complete standalone HTML/CSS documents) integrated with the existing three-pane Artifact Workbench.

### Execution Flow
```
POST /api/chat
  -> ChatService.process_chat
    -> AgentService.run
      -> Pi Coding Agent (RPC)
        -> Tool Execution: generate_artifact(title, topic, artifact_type="markdown"|"html")
          -> RetrievalService.retrieve (RAG over podcast transcripts)
          -> ArtifactGeneratorTool synthesizes content & compiles citations
        -> ArtifactService.create_artifact (persists to `artifacts` table)
      -> ChatResponse(userMessage, assistantMessage, artifact)
  -> Frontend useChatStream automatically registers artifact & opens Artifact Viewer
```

### Artifact API & Data Contract
```typescript
interface Artifact {
  id: string;             // e.g. "artifact-3a8f1b2c4e5d"
  sessionId: string;      // Foreign key to sessions.id
  title: string;          // Descriptive document title
  type: "markdown" | "html";
  content: string;        // Full markdown body or complete HTML document
  wordCount: number;      // Calculated word count
  sourceCount: number;    // Number of linked podcast evidence chunks
  allowScripts?: boolean; // Default: false
  createdAt: string;      // ISO timestamp
}
```

### HTML Security & Isolation Model
Treats all LLM-generated HTML as untrusted content:
1. **Sandboxed iframe**: Rendered exclusively via `<iframe sandbox={sandboxFlags} srcDoc={safeContent} />`. Direct DOM injection via `dangerouslySetInnerHTML` is strictly prohibited.
2. **Restrictive Sandbox Policy**:
   - **Default (`allowScripts=false`)**: `sandbox=""` — Maximum isolation. Scripts, form submissions, popups, and same-origin privileges are completely blocked.
   - **Toggled (`allowScripts=true`)**: `sandbox="allow-scripts"` strictly **without** `allow-same-origin`. This preserves an opaque/null origin (`origin: null`), preventing embedded code from accessing `window.parent`, cookies, localStorage, session state, or making authenticated API calls.
3. **Server-Side Sanitization**: `ArtifactGeneratorTool._sanitize_html` strips `<script>` tags, dangerous event handlers (`onload`, `onerror`, `onclick`), `javascript:` URIs, and top-level target hijackers (`<base target="_top">`).
4. **Content Security Policy (CSP)**: Standalone HTML embeds an inline CSP `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data: https:; font-src data:; form-action 'none'; frame-ancestors 'none';">` to block outbound network exfiltration.

---

## 7. Evaluator-Ready Product Upgrades

### Upgrade 1: Speaker-Aware & Relevance-Aware Citations
- **Speaker & Episode Target Extraction**: `RetrievalService.extract_query_targets` parses guest names (Brian Balfour, Elena Verna, Casey Winters, Rahul Vohra, Shreyas Doshi) and episode numbers from queries.
- **Rank Prioritization**: When an explicit speaker is named, chunks matching that speaker are boosted to the top of citations without discarding other relevant corroborating speakers.
- **Qualitative Evidence-Strength Indicator**: Instead of fabricated percentage scores, answers display subtle qualitative badges:
  - `HIGH EVIDENCE`: $\ge 2$ sources and $\ge 2$ speakers.
  - `LIMITED EVIDENCE`: 1 relevant source or limited single-speaker reference.
  - `NOT GROUNDED`: 0 supporting sources or low-evidence status.
- **Why This Source**: Contextual explanation synthesized from query intent, speaker match, and retrieval score.

### Upgrade 2: Professional Demo Conversation History
- **Clean Demo Seed Mechanism**: `backend/app/scripts/seed_demo.py` populates 6 curated research conversations:
  - *Today*: Brian Balfour — Channel Model Fit, Retention Curves — What Actually Matters, Ship 30/30 — Pricing Strategy, B2B SaaS Retention Playbook
  - *Yesterday*: Elena Verna — Product-Led Growth, Rahul Vohra — PMF Framework
- **Execution**: Run `python -m backend.app.scripts.seed_demo --reset` or trigger `POST /api/sessions/seed-demo?reset=true` to restore a pristine demo environment without hardcoding fake production data.

### Upgrade 3: Source Explorer
- **Focused Inspection Experience**: Clicking an expanded citation opens an elegant Source Explorer with:
  - `SOURCE` badge
  - Guest and episode header (`Episode #112 · Brian Balfour`)
  - Timestamp indicator (`00:01:28`)
  - Verified transcript quote
  - Contextual *"Why this source?"* explanation
  - Authentic episode deep link

### Upgrade 4: Compare Perspectives Engine (`compare_perspectives`)
- **Native Dual-Perspective Retrieval**: `ComparePerspectivesTool` retrieves evidence for two named guests or topics without hallucination.
- **Structured Synthesis**: Outputs:
  - Core idea, growth mechanism, and relevant evidence for Speaker A
  - Core idea, growth mechanism, and relevant evidence for Speaker B
  - Synthesis (Agreements, Differences, and Practical Implications)
- **Zero Fabrication**: If evidence for one speaker is missing from archives, explicitly flags `insufficient_evidence` instead of fabricating positions.

### Upgrade 5: Contextual Follow-Up Suggestions
- **Deterministic Action Suggestions**: Generated directly from response topics and speaker metadata (no extra LLM overhead).
- **Direct Chat Routing**: Clicking an action sends the query into the chat loop, seamlessly invoking Compare Perspectives, Ship 30 essays, or playbook artifact generation.



