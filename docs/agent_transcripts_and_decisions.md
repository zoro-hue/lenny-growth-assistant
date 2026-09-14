# Pi Coding Agent Integration & Transcripts Record

This document records the integration history, runtime failures, root cause diagnoses, and architectural decisions made while connecting the **Pi Coding Agent (`@earendil-works/pi-coding-agent`)** subprocess to local Ollama and cloud LLMs.

---

## 1. Initial State & Runtime Failures

### Issue 1: Hanging Pi Coding Agent Child Subprocess
- **Symptom**: During end-to-end integration tests, `PiRpcClient` spawned `node rpc-entry.js` which hung indefinitely without returning output or timing out.
- **Diagnosis**:
  1. The Node.js subprocess was waiting for standard input without closing, or blocking on missing Ollama credentials.
  2. The Pi agent lacked a hard timeout mechanism when executed synchronously.
  3. The local Ollama model identifier format in Pi differed (`ollama/llama3.2:3b` vs `ollama/llama3.2:3b` needing an `OLLAMA_API_KEY` dummy environment variable).
- **Correction**:
  - Configured `env["OLLAMA_API_KEY"] = "ollama"` in `backend/app/agent/pi_rpc_client.py`.
  - Added strict 60-second timeouts with process group termination (`taskkill /F /T /PID` on Windows).
  - Ensured `node_modules/@earendil-works/pi-coding-agent/dist/bundle/rpc-entry.js` was invoked with `--no-session --no-builtin-tools -e .pi/extensions/lenny_tools.ts`.

---

### Issue 2: OpenAI Cloud Quota Exhaustion (HTTP 429) & Silent Canned Fallback
- **Symptom**: Cloud queries failed with `insufficient_quota (credit_balance_exhausted)`, yet the chat interface kept outputting a canned answer ("Based on Lenny's Podcast...") with fake Casey Winters citations for every prompt.
- **Diagnosis**:
  - The frontend `useChatStream.ts` had an older fallback simulation that caught API errors and substituted hardcoded mock dialogue.
  - Furthermore, `backend/.env` had an exhausted cloud API key which prevented cloud inference.
- **Correction**:
  - Removed all hardcoded canned fallback text from `src/hooks/useChatStream.ts`.
  - Configured graceful fallback to local Ollama (`llama3.2:3b`) with `MODEL_FALLBACK_ENABLED=true`.
  - Implemented strict citation integrity: when low evidence or API limits occur, return 0 citations and the amber `Insufficient Grounded Evidence in Archives` badge.

---

### Issue 3: Model Selector Popover Sticking Closed
- **Symptom**: Clicking the top header model selector button (`• Ollama (llama3.2:3b) ▾`) did not open the dropdown.
- **Diagnosis**:
  - `ModelProviderSelector.tsx` evaluated `isOpen = isOpenExternal !== undefined ? isOpenExternal : isOpenInternal`.
  - The parent `AppShell` passed `isOpenExternal={isModelSelectorOpen}` initialized to `false`.
  - Clicking the trigger button internally invoked `setIsOpenInternal(!isOpen)`, but because `isOpenExternal !== undefined` was always `false`, the internal state was ignored.
- **Correction**:
  - Added `onToggleExternal?: () => void` prop to `ModelProviderSelector`.
  - Wired `onToggleExternal={() => setIsModelSelectorOpen(prev => !prev)}` in `ConversationHeader` and `AppShell`.
  - Popover now opens reliably on click, via `Cmd + M`, and from the composer model badge.

---

### Issue 4: Out-of-Domain & Casual Greeting Latency
- **Symptom**: Prompts like `"hi"` or `"What is the capital of Mars?"` took 40+ seconds of CPU inference on local Ollama just to output that it lacked transcript context.
- **Diagnosis**:
  - Casual greetings and non-growth queries were being fed into the full LLM agent loop without early classification.
- **Correction**:
  - Added an early evaluation gate in `backend/app/agent/agent_service.py` that immediately returns `low-evidence` with 0 citations in under 5ms for greetings and short off-topic prompts.

---

## 2. Pi Tool Bridge Specification

The following tools are registered in `.pi/extensions/lenny_tools.ts` and backed by Python handlers:

1. `search_lenny_transcripts`:
   - Inputs: `query` (string), `top_k` (integer).
   - Retrieves semantic dialogue chunks with cosine similarity, speaker name, and episode URL.
2. `lookup_episode_source`:
   - Inputs: `episode_title_or_guest` (string).
   - Retrieves exact episode metadata, guest bio, publishing date, and Spotify/YouTube link.
3. `generate_ship30_essay`:
   - Inputs: `topic`, `target_guest`, `word_count`.
   - Structures 1,200+ word essay following Ship 30 for 30 principles: hook, 2-3 core frameworks, skimmable bullet points, and actionable takeaway.
4. `generate_artifact`:
   - Inputs: `type` (`markdown` | `html`), `title`, `content`.
   - Generates and persists playbooks, dashboards, and growth calculators directly into the Artifact Workbench.
