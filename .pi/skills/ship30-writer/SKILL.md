---
name: ship30-writer
description: Generates high-impact, actionable ~1,250-word Ship 30 for 30-style essays and playbooks grounded in Lenny's Podcast transcripts. Use whenever asked to write an essay, playbook, or deep-dive framework from podcast evidence.
---

# Ship 30 for 30 Writing Skill: Lenny Growth Playbook

This skill encodes the core writing principles of **Ship 30 for 30** (created by Nicolas Cole and Dickie Bush), adapted specifically for synthesizing deep empirical insights from **Lenny's Podcast**.

## Core Writing Principles

### 1. The Hook (Headline & First 1-3 Lines)
* **Never use throat-clearing openings:** Avoid phrases like "In today's fast-paced world...", "Product managers often struggle with...", or "It is important to remember...".
* **Use a 1-3-1 Cadence:**
  * **Line 1 (Single Sentence):** A bold, counter-intuitive insight, provocative contrast, or visceral truth.
  * **Lines 2–4 (Short Paragraph):** Concrete expansion validating the struggle that founders and product leaders face.
  * **Line 5 (Punchy Anchor):** The thesis statement setting up the definitive framework.
* **Promise High ROI:** Make it clear within 10 seconds what the reader will be able to do, measure, or avoid after reading.

### 2. One Clear Central Idea
* Every essay must revolve around **one dominant thesis** (e.g., "Retention curves don't lie: how to find your natural floor", "Never paywall activation: B2B monetization loops").
* Cut any tangents that do not support the core thesis.

### 3. Narrative Progression (The 5-Act Arc)
1. **The Broken Conventional Myth:** What 90% of teams do wrong (e.g., chasing top-of-funnel blended CAC, forcing daily habits for quarterly problems).
2. **The Empirical Discovery:** What top operators actually observe in real cohort data.
3. **The Framework Deconstruction:** Step-by-step operational mechanics (e.g., Four Fits, Habit Moments, Quantitative PMF criteria).
4. **Tactical Execution & Failure Modes:** Concrete examples from named companies (Eventbrite, Miro, Reforge, Figma), metrics tables, and implementation checklists.
5. **The Golden Rule & Takeaway:** A memorable 1-2 sentence distillation the reader can remember and apply immediately.

### 4. Skimmable Formatting & Visual Rhythm
* **Paragraph Length:** Maximum 1 to 3 sentences per paragraph. Never write walls of text.
* **Subheadings:** Descriptive, value-packed H2s and H3s that convey the argument even if the reader only scans the headers.
* **Callout Quotes:** Use Markdown blockquotes (`>`) to highlight verbatim transcript quotes from guests.
* **Structured Tables & Checklists:** Include comparison tables and markdown task checklists (`- [ ]`) for operational clarity.
* **Bold Key Phrases:** Bold essential terms, numbers, and takeaways so skimmers capture the core message effortlessly.

### 5. Grounded Evidence & Zero Fabrication
* **All claims must trace to retrieved transcript evidence:**
  * Always name the guest (e.g., Casey Winters, Elena Verna, Brian Balfour).
  * Reference the episode context.
  * Quote their exact words or faithful concepts.
* **Strict prohibition against hallucination:** Never invent statistics, frameworks, guest quotes, or URLs. If evidence is lacking on a particular question, explicitly state the boundary of the archives.

### 6. Word Count Calibration
* **Target:** Approximately **1,250 words** (acceptable range: 1,100 to 1,450 words).
* Ensure the essay is thorough, providing complete tactical depth rather than a brief summary.

---

## Tool Execution Workflow

When a user asks for an essay, playbook, or Ship 30 piece:
1. Call `generate_ship30_essay(topic="...", source_url_or_guest="...")`.
2. Inspect the returned structured payload containing the grounded title, content, word count, and verified transcript citations.
3. Present the executive summary in chat and direct the user to the full playbook in the Artifact Workbench.
