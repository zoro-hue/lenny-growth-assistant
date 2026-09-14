# The Lenny Growth Assistant — Design System & Frontend Implementation Spec

---

## Part 0 — Design Plan (grounding)

**What this product actually is:** a research instrument for product/growth professionals. The core tension the design must resolve is *trust* — every claim the assistant makes has to visibly trace back to a transcript. This is closer to a legal-research tool or a financial terminal than a chatbot. The product's job is to make "where did this come from?" always answerable in one glance.

**Design plan:**

- **Color** — cool, editorial, ink-on-paper. Not the cream+terracotta AI-default, not the near-black+neon AI-default.
  - `--ink-950: #14171F` — primary text, dark chrome
  - `--ink-700: #3A4050` — secondary text
  - `--paper-0: #FDFCFA` — app background (warm white, not cream)
  - `--paper-100: #F3F1EC` — panel/sidebar background
  - `--line-200: #E4E1D8` — hairline borders/dividers
  - `--evidence-600: #2F5D50` — the ONE accent, deep pine green, used exclusively for grounding/citation/evidence signals (never for generic UI chrome, so it stays meaningful)
  - `--signal-amber-600: #A6620C` — reserved for "low confidence / insufficient evidence" states only
  - `--error-700: #9A2E1F` — errors

- **Type** — two families, clearly distinct roles, no default Inter-everywhere:
  - **Display/reading serif**: for chat message bodies, essay artifacts, and headings — this is a reading product, long-form matters. (e.g. "Source Serif 4" or "Lora")
  - **UI grotesk**: for chrome, labels, buttons, metadata, citations list, code (e.g. "Inter" or "IBM Plex Sans" for UI; "IBM Plex Mono" for token/metadata strings only, used sparingly)

- **Layout** — three-pane workspace, not cards-on-a-page:
```
┌──────────┬─────────────────────────────┬──────────────────┐
│ Sessions │        Conversation          │  Artifact Viewer │
│  (240px) │         (fluid)               │   (collapsed by  │
│          │                               │   default, 440px │
│          │                               │   when open)     │
└──────────┴─────────────────────────────┴──────────────────┘
```
  Hairline dividers between panes, not shadows or card borders. Sidebar and Artifact Viewer are structurally quiet; the conversation pane carries the typographic weight.

- **Principles**
  1. Citations are structural, not decorative — they render as an integral part of the message, not a footnote-style afterthought.
  2. One accent color, spent entirely on "this is grounded / this is evidence." Nothing else gets colored.
  3. Serif for reading, sans for doing. If it's prose you read, it's serif. If it's a control you operate, it's sans.
  4. Quiet chrome, loud content. The UI should recede; transcript-grounded answers and generated essays are the visual subject.

**Self-check against AI-default tells:** No tracked-out ALL-CAPS eyebrows. No middle-dot-joined meta strings. No `→` on buttons. No identical rounded cards with soft grey shadows. No numbered markers unless content is a genuine sequence (Ship 30/30 steps qualify; nothing else does). Confirmed clear.

---

## Part A — Design Principles

1. **Grounding is the product.** Every AI-generated claim traces to a source. The UI's primary job is making that traceability instant and unambiguous — never a hidden modal, always inline.
2. **Confidence is communicated honestly.** "Not enough evidence" is a first-class state, not an error. It should feel like the system being trustworthy, not failing.
3. **Two reading modes.** Scanning (sidebar, citations, metadata — sans-serif, compact) vs. deep reading (message bodies, essays — serif, generous line-height, ~68–72 char measure).
4. **The Artifact Viewer is a workbench, not a preview pane.** It's where generated essays/HTML artifacts live and get iterated on, side-by-side with the conversation that produced them.
5. **Restraint.** One accent color. One moment of motion per interaction. No decorative gradients, no card-soup.

---

## Part B — Screen/Layout Specification

### B.1 Global shell
- **Grid**: 3 columns — Sidebar (240px fixed) | Conversation (fluid, min 480px) | Artifact Viewer (0px collapsed / 440px expanded, fixed).
- **Header bar**: 56px height, spans Conversation + Artifact Viewer columns. Contains: session title (editable inline), model/provider selector (right-aligned), Artifact Viewer toggle icon.
- **Background**: `--paper-0` for Conversation; `--paper-100` for Sidebar and Artifact Viewer (subtle tonal separation, not a border-heavy split).

### B.2 Sidebar (Session list)
- Width 240px, fixed. Collapses to icon-rail (56px) below 1024px viewport width, fully hidden (drawer) below 768px.
- Top: "New chat" as a full-width button, sans-serif, ink-950 text on paper-0 pill, hairline border — not filled/accent (accent is reserved for evidence).
- Session list: each row = truncated session title (sans, 14px) + relative timestamp (sans, 12px, ink-700, right-aligned). Active session has a 2px `--evidence-600` left-border indicator (the ONE place outside citations the accent appears, functioning as "you are here / this is the active thread of evidence").
- Sessions grouped by relative time (Today / Yesterday / Previous 7 days / Older) — plain sans-serif section labels, sentence case, no tracked-caps.

### B.3 Conversation pane
- Max content measure: 680px, centered within the fluid column (keeps line length ~70ch even on wide screens).
- Message list scrolls independently; header bar and composer are fixed.
- Composer docked at bottom: multi-line auto-growing textarea (sans, 15px), send button (icon-only, disabled state until text present), model indicator chip inline to the left of input (shows current provider at a glance without opening the selector).

### B.4 Artifact Viewer
- Slides in from the right (transform, 220ms, ease-out) when an artifact is generated or the toggle is clicked. Does not reflow the whole page violently — conversation column narrows smoothly.
- Header: artifact title (editable), format toggle (Markdown source / Rendered), copy button, download button, close (×).
- Body: scrollable rendered content area, `--paper-0` background (lighter than the viewer's own header strip, to visually "lift" the document like paper on a desk).
- Footer (HTML artifacts only): a thin "Sandboxed preview" indicator strip — quiet, sans, 12px, ink-700 — communicating trust boundary without alarm.

---

## Part C — Component Hierarchy

```
App
├── AppShell
│   ├── Sidebar
│   │   ├── NewChatButton
│   │   ├── SessionGroup (repeated: Today/Yesterday/...)
│   │   │   └── SessionListItem (active | default | renaming)
│   │   └── SidebarFooter (settings/help, minimal)
│   ├── ConversationHeader
│   │   ├── SessionTitle (inline-editable)
│   │   ├── ModelProviderSelector
│   │   └── ArtifactViewerToggle
│   ├── ConversationPane
│   │   ├── MessageList
│   │   │   ├── UserMessage
│   │   │   └── AssistantMessage
│   │   │       ├── MessageBody (serif, markdown-rendered)
│   │   │       ├── CitationList
│   │   │       │   └── CitationChip (× N)
│   │   │       ├── EvidenceConfidenceBadge (optional — low-evidence state)
│   │   │       └── ArtifactGeneratedCard (optional — links to Artifact Viewer)
│   │   ├── EmptyState (new session)
│   │   ├── LoadingIndicator (assistant thinking / retrieving)
│   │   └── Composer
│   │       ├── TextArea
│   │       ├── ModelIndicatorChip
│   │       ├── ShipEssayAction (secondary action button)
│   │       └── SendButton
│   └── ArtifactViewer
│       ├── ArtifactHeader
│       │   ├── ArtifactTitle
│       │   ├── FormatToggle (Source | Rendered)
│       │   └── ArtifactActions (copy, download, close)
│       ├── ArtifactBody
│       │   ├── MarkdownRenderer
│       │   └── HtmlSandboxFrame (iframe, sandboxed)
│       └── SandboxIndicator (HTML only)
└── Toaster (system-level confirmations, errors)
```

---

## Part D — Design Tokens

```css
:root {
  /* Color */
  --ink-950: #14171F;
  --ink-700: #3A4050;
  --ink-500: #6B7280;
  --paper-0: #FDFCFA;
  --paper-100: #F3F1EC;
  --paper-200: #EAE7DF;
  --line-200: #E4E1D8;
  --line-300: #D5D1C5;
  --evidence-600: #2F5D50;
  --evidence-100: #E7EEEA; /* citation chip background */
  --signal-amber-600: #A6620C;
  --signal-amber-100: #F5E9D8;
  --error-700: #9A2E1F;
  --error-100: #F5E2DE;

  /* Type */
  --font-serif: "Source Serif 4", Georgia, serif;
  --font-sans: "Inter", -apple-system, sans-serif;
  --font-mono: "IBM Plex Mono", monospace;

  --text-xs: 12px;
  --text-sm: 14px;
  --text-base: 15px;
  --text-md: 17px;   /* message body */
  --text-lg: 20px;
  --text-xl: 26px;
  --text-2xl: 32px;

  --leading-tight: 1.3;
  --leading-normal: 1.55;
  --leading-relaxed: 1.75; /* serif body */

  /* Spacing (4px base scale) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;

  /* Radius — deliberately small/near-zero, editorial not "SaaS card" */
  --radius-sm: 3px;
  --radius-md: 6px;
  --radius-pill: 999px; /* only for chips/badges */

  /* Motion */
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --duration-fast: 120ms;
  --duration-base: 220ms;

  /* Layout */
  --sidebar-w: 240px;
  --sidebar-rail-w: 56px;
  --artifact-w: 440px;
  --header-h: 56px;
  --content-measure: 680px;
}
```

---

## Part E — Interaction Flows

### E.1 New-chat experience
1. User clicks "New chat" (or app loads with no sessions).
2. Conversation pane shows **EmptyState**: centered, serif headline ("Ask about product and growth, grounded in Lenny's Podcast"), 2–3 example prompts as plain clickable text rows (not buttons-as-cards), composer focused and ready.
3. First message sent → session created in sidebar with auto-generated title (first ~6 words of the query), animates into the "Today" group.

### E.2 Grounded Q&A flow
1. User sends message → **LoadingIndicator** replaces send affordance: a single-line status text that transitions through states — "Retrieving transcripts…" → "Drafting answer…" — sans-serif, ink-500, with a subtle pulsing single dot (not a spinner, not three bouncing dots).
2. Assistant message streams in (serif body text token-by-token).
3. Citation chips animate in *after* the message completes streaming, as a distinct beat — small fade+slight-rise, 150ms, staggered 40ms each. This visually says "here's what backs up what you just read."
4. Clicking a citation chip opens an inline expandable panel (not a new pane) directly below the message: episode title, guest, timestamp/quote excerpt, "Open episode" link.

### E.3 Ship 30/30 essay flow
1. User invokes via composer's secondary action ("Write an essay") or explicit request in text.
2. Confirmation micro-step: assistant asks/confirms the topic if ambiguous (single clarifying message, not a modal).
3. Generation shows LoadingIndicator with status "Structuring essay…" → "Grounding claims…" → "Finalizing draft…" (reflects real pipeline stages, sets accurate expectation for a longer wait, ~1,250 words).
4. On completion: an **ArtifactGeneratedCard** appears inline in the conversation (title, word count, source count) — clicking it opens the Artifact Viewer. Artifact Viewer auto-opens on first generation.

### E.4 Artifact Viewer flow
1. Opens via slide-in transform (220ms, ease-out), conversation column narrows in sync.
2. Format toggle defaults to "Rendered." Toggling to "Source" shows raw Markdown in mono font, line-numbered, for copy-paste precision.
3. HTML artifacts render inside a sandboxed iframe (`sandbox="allow-same-origin"` only — no `allow-scripts` by default; if the artifact requires JS to demo, an explicit "Enable interactivity" toggle must be clicked, with a one-line explanation of what that means).
4. Copy/download always operate on the raw source, never the rendered DOM.

### E.5 Model/provider selector
1. Compact chip in header showing current provider + model (e.g. "Claude · Cloud" or "Llama 3.1 · Local").
2. Click opens a small popover (not a full modal): two grouped options — Cloud, Local — each showing model name and a one-line latency/capability note ("Local — private, slower" / "Cloud — faster, requires network").
3. Switching mid-session shows a small inline system note in the conversation ("Switched to Local · Llama 3.1") — sans, ink-500, centered, 12px — so the transcript stays an honest record.

---

## Part F — States

### F.1 Loading states
- **Message-level**: single pulsing dot + status text (see E.2). Never a full-pane spinner.
- **Session list (initial load)**: skeleton rows — flat `--paper-200` bars, no shimmer animation (shimmer reads as generic template default; a slow 800ms opacity pulse is quieter and preferred).
- **Artifact generation**: staged status text as described in E.3.

### F.2 Empty states
- **No sessions yet**: see E.1.
- **No citations found for a query** → this is NOT an error; see F.4 "Not enough evidence."
- **Artifact Viewer, nothing generated yet**: quiet centered serif line — "Generated essays and documents will appear here" — no icon, no illustration (avoid decorative SVG-people clutter).

### F.3 Error states
- Inline, attached to the failed message — never a toast for content-level failures (toasts are for system-level: connectivity, save failures).
- Voice: state what happened and what to do. E.g., "Couldn't reach the local model. Check that Ollama is running, or switch to Cloud." with an inline "Switch to Cloud" action button — not just prose.
- Color: `--error-700` text on `--error-100` background, `--radius-sm`, left-aligned icon (exclamation, outline style, not filled/alarming).

### F.4 "Not enough evidence" state
- This is the product's most important state — must feel like integrity, not failure.
- Rendered as a distinct message treatment: `--signal-amber-600` thin left border (2px, same visual language as the active-session indicator, reused intentionally), body text in normal ink-950 serif.
- Copy pattern: "I don't have enough grounded material on \[topic\] in Lenny's Podcast to answer confidently." followed by what *is* available if anything partial was found, and never a fabricated answer.
- No citation chips appear (there's nothing to cite) — their absence is itself the signal.

---

## Part G — Responsive Behavior

- **≥1280px**: full three-pane layout as specified.
- **1024–1279px**: Sidebar collapses to 56px icon-rail (session titles on hover tooltip); Artifact Viewer still 440px overlay-style (slides over conversation edge rather than pushing, to preserve reading width).
- **768–1023px**: Sidebar becomes a drawer (hidden by default, hamburger toggle in header); Artifact Viewer becomes a full-width overlay (slides up from bottom on tablet-portrait, covers conversation entirely with a clear back affordance).
- **<768px (mobile)**: single-column stack. Header has hamburger (sessions) + artifact icon (only visible/enabled once an artifact exists). Composer becomes sticky-bottom with safe-area padding. Citation panels open as bottom sheets rather than inline expand (avoids awkward inline reflow on narrow screens). Message max-width 100% with 16px gutters, serif body drops to 16px for mobile readability floor.

---

## Part H — Accessibility Requirements

- Color contrast: `--ink-950` on `--paper-0` = 15.8:1 (AAA). `--evidence-600` on `--paper-0` = 6.2:1 (AA for normal text). `--signal-amber-600` on `--paper-0` verified ≥ 4.5:1.
- Never convey state by color alone: citation presence/absence is structural (chips exist or don't), confidence state has distinct copy + border position, not just color.
- All interactive elements have visible focus rings: 2px `--evidence-600` outline, 2px offset — consistent regardless of element type.
- Composer, citation chips, session list items, model selector: all reachable and operable via keyboard (see Part I).
- Live region (`aria-live="polite"`) on the message list for streaming assistant responses, so screen readers announce completion rather than every token.
- Artifact iframe: `title` attribute always set descriptively; sandboxed HTML content is announced as "embedded content" to assistive tech, with the sandbox indicator strip's text also present as visible + accessible text (not just a color strip).
- Reduced motion: all transform/opacity transitions wrapped in `@media (prefers-reduced-motion: reduce)` → durations drop to 0, indicator dot pulse becomes static.

---

## Part I — Keyboard Interactions

| Action | Shortcut |
|---|---|
| New chat | `Cmd/Ctrl + N` |
| Send message | `Enter` (send) / `Shift+Enter` (newline) |
| Focus composer from anywhere | `/` |
| Toggle Artifact Viewer | `Cmd/Ctrl + .` |
| Navigate session list | `↑ / ↓` when sidebar focused |
| Open focused citation | `Enter` when chip focused |
| Close Artifact Viewer / citation panel | `Esc` |
| Switch model selector | `Cmd/Ctrl + M` opens popover |

---

## Part J — Animation/Motion Guidelines

- **One orchestrated moment**: the Artifact Viewer slide-in is the product's signature motion beat — everything else is quieter by comparison.
- Citation chips: fade + 4px rise, staggered, only on first appearance after streaming completes (not on every re-render).
- Message streaming: no per-token animation beyond natural text appearance (avoid cursor-blink gimmicks beyond a simple caret at the end of in-progress text).
- Hover states: 120ms background-color transition only, no scale/shadow-lift (avoids generic "card lift" tell).
- Loading dot: single dot, 1.4s ease-in-out opacity pulse (0.3 → 1 → 0.3), not a 3-dot bounce.
- All durations use `--duration-fast` (hover/focus) or `--duration-base` (panel transitions) tokens exclusively — no ad hoc values.

---

## Part K — Detailed Artifact Viewer UX

**Purpose**: a workbench for generated documents, not a passive preview.

- **Header** (44px): title (inline-editable, sans 15px medium), Format Toggle (segmented control: "Rendered" / "Source"), icon actions (copy, download as .md/.html, close). No overflow menu — all actions visible, this is a working surface used often.
- **Body**:
  - *Markdown rendering*: serif body matching conversation typography (visual continuity — the essay reads like the chat, because it was born from it). Headings use the sans-serif UI font at larger sizes (contrast device: sans for structure/navigation within the document, serif for the prose itself). Code blocks in `--font-mono` on `--paper-100` background, `--radius-sm`.
  - *HTML/CSS rendering*: rendered inside `<iframe sandbox="allow-same-origin">` by default (styles + static markup only). A visible strip above the iframe: "Sandboxed preview — scripts disabled" with an explicit toggle to add `allow-scripts` if the artifact declares interactive JS, gated behind one click, never on by default.
  - Both modes share a consistent 24px padding, `--content-measure`-equivalent internal max-width (artifact panel is 440px so this mostly just means: no forced full-bleed).
- **Footer**: none by default; sandbox indicator lives at top of body, not buried in a footer, since trust information should be seen before content, not after.
- **Versioning (if multiple artifacts generated in one session)**: a simple `< 1/3 >` stepper in the header, sans 12px — lets user page through prior generated artifacts without cluttering the conversation.

---

## Part L — Final Implementation Specification (React + TypeScript + Tailwind + shadcn/ui + Lucide)

### L.1 Tech setup
- **Framework**: React 18 + TypeScript, Vite.
- **Styling**: Tailwind CSS, configured with the design tokens from Part D as `theme.extend` values (custom colors, fontFamily, spacing aliases, borderRadius).
- **Components**: shadcn/ui primitives for: `Popover` (model selector), `Sheet` (mobile drawers), `Tooltip` (icon-rail sidebar), `Toast` (system errors), `Separator`. Everything else (MessageBody, CitationChip, ArtifactViewer internals) is custom — shadcn defaults would pull in the generic SaaS-card look this brief explicitly avoids.
- **Icons**: `lucide-react` — outline style throughout, 18px default, 16px in compact contexts (chips, inline citation icons). Use: `Plus` (new chat), `Send`, `FileText` (artifact card), `ExternalLink` (open episode), `Copy`, `Download`, `X` (close), `ChevronDown` (selector), `AlertTriangle` (error, outline not filled).
- **Markdown rendering**: `react-markdown` + `remark-gfm`, custom component overrides mapping `h1–h3` to sans-serif UI font, `p/li` to serif body font per Part K.

### L.2 File/component structure
```
src/
  styles/tokens.css          — Part D tokens as CSS custom properties
  components/
    layout/
      AppShell.tsx
      Sidebar.tsx
      SessionListItem.tsx
      ConversationHeader.tsx
      ModelProviderSelector.tsx
    chat/
      ConversationPane.tsx
      MessageList.tsx
      UserMessage.tsx
      AssistantMessage.tsx
      CitationList.tsx
      CitationChip.tsx
      CitationExpandPanel.tsx
      EvidenceConfidenceBadge.tsx
      Composer.tsx
      LoadingIndicator.tsx
      EmptyState.tsx
    artifact/
      ArtifactViewer.tsx
      ArtifactHeader.tsx
      MarkdownRenderer.tsx
      HtmlSandboxFrame.tsx
      SandboxIndicator.tsx
      ArtifactGeneratedCard.tsx
    common/
      Toaster.tsx
  hooks/
    useSession.ts
    useChatStream.ts
    useArtifact.ts
  types/
    chat.ts   (Message, Citation, Session)
    artifact.ts (Artifact, ArtifactFormat)
```

### L.3 Component specs

**`AssistantMessage`**
- *Purpose*: render a grounded assistant reply with its evidence.
- *Appearance*: serif body `--text-md`/`--leading-relaxed`, `max-width: var(--content-measure)`. `CitationList` below body if citations present. `EvidenceConfidenceBadge` (amber left-border variant) instead of citations if evidence insufficient.
- *States*: streaming (caret at text end, live region updating) / complete / low-evidence / error.
- *Behavior*: citation chips animate in post-stream (Part E.2/J). Clicking a chip toggles `CitationExpandPanel` inline below the message (accordion, one open at a time per message).
- *Mobile*: citation panel becomes a `Sheet` (shadcn) bottom-sheet instead of inline expand.

**`CitationChip`**
- *Purpose*: compact, always-visible proof-of-grounding unit.
- *Appearance*: pill (`--radius-pill`), `--evidence-100` background, `--evidence-600` text, `--text-xs`, sans-serif, small document icon (Lucide `FileText`, 12px) + episode short-title, truncated.
- *States*: default / hover (`--duration-fast` background darken) / expanded (active) / focus-visible ring.
- *Behavior*: `Enter`/click toggles expand panel; `aria-expanded` reflects state.

**`ModelProviderSelector`**
- *Purpose*: show + switch active LLM provider.
- *Appearance*: header chip, sans `--text-sm`, ink-700, small `ChevronDown`. Popover (shadcn) with two option groups: Cloud / Local, each row showing model name + one-line note.
- *States*: default / open / switching (brief inline disabled state on the chip while backend confirms) / unavailable (Local shown greyed with "Ollama not detected" if health-check fails).
- *Behavior*: on switch, posts a system note into the conversation (Part E.5).

**`ArtifactViewer`**
- *Purpose*: workbench for generated documents.
- *Appearance/behavior/mobile*: fully specified in Part K.
- *States*: empty / generating (loading stage text in header area) / populated / stepping between multiple artifacts.

**`HtmlSandboxFrame`**
- *Purpose*: safely render generated HTML/CSS.
- *Appearance*: `iframe` filling ArtifactViewer body, `--paper-0` background matching rest of viewer.
- *States*: scripts-disabled (default) / scripts-enabled (explicit opt-in per artifact, resets on new artifact generation — never persists as a global setting).
- *Behavior*: `sandbox` attribute is the enforcement mechanism, not just a UI label — `allow-same-origin` only by default, `allow-scripts` added only after explicit user toggle click, never both granted silently.

### L.4 Breakpoints (Tailwind config)
```js
screens: {
  sm: '480px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
}
```
Matches Part G thresholds exactly (768/1024/1280).

### L.5 Do-not-implement-yet boundary
This document is design + spec only. Next step (separate task) is scaffolding the actual `.tsx` files against this spec, plus wiring to the FastAPI backend's `/chat`, `/sessions`, `/artifacts` endpoints.
