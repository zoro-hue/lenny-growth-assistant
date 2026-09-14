# Product Requirements Document (PRD) & Discovery Brief

## 1. Problem Statement & Market Context
Product managers, founders, and growth leaders face an overwhelming volume of business and growth advice. *Lenny's Podcast* contains world-class tactical wisdom from top operators (e.g., Elena Verna, Casey Winters, Brian Balfour, Shreyas Doshi). However:
- Audio and unstructured text are difficult to search cross-episode.
- Generic LLM chatbots fabricate claims, attribute quotes incorrectly, or hallucinate metrics.
- Practitioners lack an integrated tool to synthesize long-form actionable operational essays (e.g. Ship 30 for 30 format) directly backed by episode evidence.

---

## 2. Product Objectives & Value Proposition
**The Lenny Growth Assistant** delivers an authoritative, grounded research companion:
1. **Verifiable Truth**: Every recommendation traces to exact episode titles, guest operators, timestamps, and verbatim quotes.
2. **First-Class Low-Evidence Handling**: If a topic is outside the podcast domain (e.g., crypto tokenomics, unrelated trivia), the assistant transparently reports insufficient evidence with 0 fabricated citations.
3. **Dual-Model Inference**: Support for cloud frontier models (OpenAI GPT-4o mini) and offline, privacy-first local models (Ollama `llama3.2:3b`).
4. **Ship 30 for 30 Essay Generation**: Generates 1,200+ word structured operational essays with strong hooks, narrative flow, skimmable subheadings, and clear takeaways.
5. **Interactive Artifact Workbench**: Side-by-side artifact viewer supporting Markdown documents and sandboxed, safe HTML/CSS dashboards.

---

## 3. Key User Personas
- **Growth Operator / Head of Growth**: Needs battle-tested playbooks on acquisition loops, retention mechanics, and pricing changes.
- **Product Leader / VP of Product**: Queries frameworks on feature prioritization, team structure, and product-market fit metrics.
- **Content Creator / Founder**: Uses the Ship 30 for 30 engine to generate thought leadership derived from operator transcripts.

---

## 4. Functional Requirements

### 4.1 Retrieval-Augmented Generation (RAG) & Grounding
- **FR-1**: Dialogue-aware ingestion preserving speaker attribution and episode metadata.
- **FR-2**: Vector search with cosine similarity (pgvector HNSW index or SQLite in-memory fallback).
- **FR-3**: Multi-turn conversation history preserved up to 6 turns per session.
- **FR-4**: Strict zero-fabrication constraint: citations must map to verified database chunks.

### 4.2 Autonomous Pi Coding Agent Integration
- **FR-5**: Agent reasoning via `@earendil-works/pi-coding-agent` RPC protocol.
- **FR-6**: Custom tool registry exposing `search_lenny_transcripts`, `lookup_episode_source`, `generate_ship30_essay`, and `generate_artifact`.
- **FR-7**: Seamless tool call translation between OpenAI function calling format and Ollama JSON formats.

### 4.3 Editorial User Interface & Workstation
- **FR-8**: Three-pane responsive layout with collapsible sidebar (240px -> 56px rail).
- **FR-9**: Full session lifecycle: create new chat, rename inline, delete with confirmation.
- **FR-10**: Interactive model switcher with dynamic availability checking and key warnings.
- **FR-11**: Artifact workbench with raw/preview toggles, copy actions, and script safety sandbox.

---

## 5. Non-Functional Requirements
- **NFR-1 Performance**: Sub-second fast-path response for casual greetings and low-evidence short-circuits; streaming feedback during agent tool execution.
- **NFR-2 Reliability**: SQLite fallback allows 100% operation even if PostgreSQL or external vector databases are unavailable.
- **NFR-3 Security**: Untrusted generated HTML executed in sandboxed `<iframe>` with strict CSP. Zero credentials committed to version control.
