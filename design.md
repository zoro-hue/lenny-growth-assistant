# Design Specification — The Lenny Growth Assistant

## 1. Executive Summary & Design Vision
The Lenny Growth Assistant is an editorial research workstation engineered for growth operators, product leaders, and startup founders. Unlike generic chat interfaces, the assistant is built around **verifiable trust**: every claim, framework, and operational tactic links directly back to verified transcripts from *Lenny's Podcast*.

### Core Design Principles
1. **Grounding is the Product**: Every statement is visibly backed by podcast evidence. Citations are first-class structural elements, not hidden footnotes.
2. **Honest Confidence**: "Insufficient evidence" is a core system state, communicating high integrity rather than failure.
3. **Editorial Typography & Restraint**:
   - **Serif (`Lora` / `Merriweather`)**: For long-form reading, essay artifacts, and synthesis prose.
   - **Grotesk (`Inter` / `IBM Plex Sans`)**: For UI chrome, buttons, metadata tags, and controls.
   - **Monospace (`IBM Plex Mono`)**: For timestamps, token counts, and identifiers.
4. **Single Pine Accent (`#2F5D50`)**: Color is strictly reserved for verified evidence and citations.
5. **Fluid Three-Pane Workspace**:
   - Left: Conversation History & Session Management (240px, collapsible to 56px rail).
   - Center: Grounded Conversation & Prompt Composer (fluid, max-w-680px reading measure).
   - Right: Artifact Workbench (440px expandable panel for Markdown essays and sandboxed HTML).

---

## 2. Color System & Semantic Tokens

```css
:root {
  /* Ink Tokens */
  --ink-950: #14171F; /* Primary typography & high-contrast chrome */
  --ink-700: #3A4050; /* Secondary metadata & supporting labels */
  --ink-500: #6B7280; /* Tertiary captions, timestamps & placeholders */

  /* Paper Backgrounds */
  --paper-0: #FDFCFA;   /* Primary canvas warm white */
  --paper-100: #F3F1EC; /* Sidebar & panel neutral */
  --paper-200: #EAE6DD; /* Hover highlights & active states */

  /* Structural Lines */
  --line-200: #E4E1D8; /* Hairline panel dividers */
  --line-300: #D1CCC0; /* Input borders & active outlines */

  /* Accent & Signaling */
  --evidence-600: #2F5D50; /* Deep pine green: Grounded transcript citations */
  --signal-amber-600: #A6620C; /* Low-evidence & missing key alerts */
  --signal-red-600: #B91C1C; /* Destructive actions & session deletion */
}
```

---

## 3. Interaction & Keyboard Ergonomics

| Shortcut | Action | Scope |
| :--- | :--- | :--- |
| `⌘ / Ctrl + N` | Create New Conversation | Global |
| `⌘ / Ctrl + B` | Toggle Left Sidebar Collapse / Expand | Global |
| `⌘ / Ctrl + .` | Toggle Artifact Workbench | Global |
| `⌘ / Ctrl + M` | Toggle Model Selector Dropdown | Global |
| `/` | Focus Composer Textarea | Global |
| `Escape` | Close Popovers / Cancel Inline Renaming | Global |
| `Enter` | Submit Prompt / Save Inline Rename | Form Input |

---

## 4. Safety & Sandboxing Architecture
All generated HTML/CSS artifacts are isolated in sandboxed iframes:
- `sandbox="allow-same-origin"` by default (scripts blocked).
- Explicit user opt-in toggle to execute JavaScript with visual security badges.
- Strict CSP prohibiting external script injection.
