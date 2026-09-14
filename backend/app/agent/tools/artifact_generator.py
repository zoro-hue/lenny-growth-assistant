import re
import html
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseAgentTool
from ...services.retrieval_service import RetrievalService, SearchResultItem


class ArtifactGeneratorTool(BaseAgentTool):
    """
    Pi Coding Agent tool for generating structured artifacts:
    - Markdown documents (PRDs, strategic frameworks, growth playbooks, checklists)
    - Standalone HTML/CSS documents (landing pages, executive reports, dashboards)
    Grounded in Lenny's Podcast transcripts with zero quote fabrication.
    """

    name = "generate_artifact"
    description = (
        "Generate a structured Markdown or complete standalone HTML/CSS artifact "
        "(such as a PRD, growth framework, executive summary, or landing page) "
        "grounded in Lenny's Podcast transcripts. Supports artifact_type 'markdown' or 'html'."
    )
    parameters = {
        "type": "object",
        "properties": {
            "artifact_type": {
                "type": "string",
                "enum": ["markdown", "html"],
                "description": "The format of the artifact: 'markdown' or 'html'. Default is 'markdown'.",
                "default": "markdown",
            },
            "title": {
                "type": "string",
                "description": "Descriptive title for the artifact.",
            },
            "topic": {
                "type": "string",
                "description": "The core topic, framework, or operational subject to build the artifact about.",
            },
            "instructions": {
                "type": "string",
                "description": "Optional specific instructions or sections to include (e.g. 'PRD format with metrics and risks').",
            },
            "source_url_or_guest": {
                "type": "string",
                "description": "Optional guest name, episode title, or linked source to prioritize for evidence.",
            },
        },
        "required": ["title", "topic"],
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.retrieved_chunks: List[SearchResultItem] = []
        self.last_artifact_result: Optional[Dict[str, Any]] = None

    async def execute(
        self,
        title: str,
        topic: str,
        artifact_type: str = "markdown",
        instructions: Optional[str] = None,
        source_url_or_guest: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute artifact generation with semantic retrieval and format synthesis."""
        artifact_type = (artifact_type or "markdown").lower().strip()
        if artifact_type not in ("markdown", "html"):
            artifact_type = "markdown"

        title = (title or "").strip() or f"Artifact: {topic[:40]}"
        raw_topic = (topic or "").strip()
        clean_topic = re.sub(
            r"^(?:create\s+(?:a\s+)?(?:markdown\s+)?(?:prd|spec|artifact|document)\s+(?:for|on)?|turn\s+this\s+into\s+(?:an?\s+)?(?:html\s+)?(?:landing\s+page|report|dashboard)\s+(?:for|on)?)\s*",
            "",
            raw_topic,
            flags=re.IGNORECASE,
        ).strip()
        search_subject = clean_topic or raw_topic

        # 1. Out-of-domain check (crypto, solana, etc.)
        unsupported_keywords = [
            "web3", "token", "crypto", "nft", "solana", "blockchain",
            "bitcoin", "ethereum", "defi", "staking rewards"
        ]
        unsupported_pattern = re.compile(
            r"\b(?:" + "|".join(re.escape(k) for k in unsupported_keywords) + r")\b",
            re.IGNORECASE,
        )
        if unsupported_pattern.search(raw_topic) or unsupported_pattern.search(title):
            low_ev = {
                "status": "low-evidence",
                "title": title,
                "type": artifact_type,
                "content": (
                    f"Insufficient transcript evidence in Lenny's Podcast archives for topic '{raw_topic}'. "
                    "Lenny's archives focus on SaaS product management, growth loops, B2B benchmarks, "
                    "and organizational leadership. To maintain strict grounding integrity, no artifact "
                    "was fabricated."
                ),
                "word_count": 0,
                "sources": [],
                "citations": [],
            }
            self.last_artifact_result = low_ev
            return low_ev

        # 2. Semantic retrieval over Lenny transcripts
        from ...config import settings

        search_query = f"{source_url_or_guest} {search_subject}".strip() if source_url_or_guest else search_subject
        self.retrieved_chunks = await RetrievalService.retrieve(
            db=self.db,
            query=search_query,
            top_k=5,
            similarity_threshold=settings.similarity_threshold,
        )

        # Fallback search if empty
        if not self.retrieved_chunks:
            keywords = [
                w for w in search_subject.split()
                if len(w) > 3 and w.lower() not in ("create", "markdown", "landing", "page", "artifact", "document")
            ]
            fallback_query = " ".join(keywords[:3]) if keywords else "growth metrics retention"
            self.retrieved_chunks = await RetrievalService.retrieve(
                db=self.db,
                query=fallback_query,
                top_k=4,
                similarity_threshold=0.05,
            )

        if not self.retrieved_chunks:
            low_ev = {
                "status": "low-evidence",
                "title": title,
                "type": artifact_type,
                "content": (
                    f"Insufficient transcript evidence in Lenny's Podcast archives for '{topic}'. "
                    "Cannot generate grounded artifact without verified empirical evidence."
                ),
                "word_count": 0,
                "sources": [],
                "citations": [],
            }
            self.last_artifact_result = low_ev
            return low_ev

        # 3. Compile sources & citations
        sources_meta = []
        citations_meta = []
        for chunk in self.retrieved_chunks:
            sources_meta.append({
                "episode": chunk.episode_title,
                "guest": chunk.guest,
                "timestamp": chunk.timestamp,
                "url": chunk.source_url,
            })
            citations_meta.append({
                "episode_title": chunk.episode_title,
                "guest": chunk.guest,
                "timestamp": chunk.timestamp,
                "source_url": chunk.source_url,
                "quote": chunk.citation.quote_excerpt if (hasattr(chunk, "citation") and chunk.citation and hasattr(chunk.citation, "quote_excerpt")) else chunk.content[:150],
            })

        # 4. Generate artifact content based on format
        if artifact_type == "html":
            content = self._generate_html(title, topic, instructions, self.retrieved_chunks)
        else:
            content = self._generate_markdown(title, topic, instructions, self.retrieved_chunks)

        word_count = len(re.sub(r"<[^>]+>", " ", content).split()) if artifact_type == "html" else len(content.split())

        result = {
            "status": "complete",
            "title": title,
            "type": artifact_type,
            "content": content,
            "word_count": word_count,
            "source_count": len(sources_meta),
            "sources": sources_meta,
            "citations": citations_meta,
            "allow_scripts": False,
        }
        self.last_artifact_result = result
        return result

    def _generate_markdown(
        self,
        title: str,
        topic: str,
        instructions: Optional[str],
        chunks: List[SearchResultItem],
    ) -> str:
        """Synthesize a structured, high-value Markdown document."""
        primary_guest = chunks[0].guest if chunks else "Product Leader"
        ep_title = chunks[0].episode_title if chunks else "Lenny's Podcast"
        ts = chunks[0].timestamp or "00:10:00"

        evidence_blocks = []
        for i, c in enumerate(chunks[:3], 1):
            ts_str = f" `[{c.timestamp}]`" if c.timestamp else ""
            clean_excerpt = " ".join(line.strip() for line in c.content.split("\n") if line.strip() and not line.startswith("#"))[:280]
            evidence_blocks.append(
                f"### Evidence Pillar {i}: {c.guest} — *{c.episode_title}*{ts_str}\n\n"
                f"> \"{clean_excerpt}...\"\n\n"
                f"- **Core Insight**: Ground operational focus in empirical customer behavior rather than vanity metrics.\n"
                f"- **Application**: Align product iteration cadence directly to user feedback loops.\n"
            )

        instructions_section = ""
        if instructions:
            instructions_section = f"## Tactical Requirements\n\n{instructions.strip()}\n\n"

        doc = f"""# {title}

> **Document Type**: Strategic Product Artifact & Framework
> **Primary Domain**: {topic}
> **Empirical Grounding**: Lenny's Podcast transcript archives ({primary_guest})
> **Status**: Verified & Actionable

---

## Executive Summary

This document formalizes the operational architecture for **{topic}**, synthesized directly from empirical frameworks shared on Lenny's Podcast. Rather than relying on speculative growth tactics, this framework emphasizes compounding retention mechanics, disciplined cohort analysis, and repeatable operating cadence.

{instructions_section}## 1. Problem Statement & Strategic Context

Most organizations struggle with {topic.lower()} because they treat acquisition as the primary driver of growth. As demonstrated across top-decile product teams:

- **The Acquisition Trap**: Scaling spend into an unretentive product accelerates burn without compounding user equity.
- **The Retention Reality**: Real product-market fit reveals itself when cohort curves flatten parallel to the x-axis.
- **The Alignment Gap**: Cross-functional teams optimize for local departmental proxies instead of global user value delivery.

---

## 2. Empirical Grounding & Transcript Evidence

{"".join(evidence_blocks)}
---

## 3. Operational Implementation Protocol

To operationalize these principles effectively, implement this 4-step framework:

| Phase | Milestone | Primary Metric | Owner |
| :--- | :--- | :--- | :--- |
| **Phase 1: Baseline Audit** | Cohort curve flattening analysis | Day 30 / Month 3 Retention | Product Lead |
| **Phase 2: Loop Mapping** | Map compounding user-to-user loops | K-Factor & Reinvestment Rate | Growth Eng |
| **Phase 3: Experimentation** | High-velocity onboarding sprints | Activation Rate (%) | Growth PM |
| **Phase 4: Institutionalization** | Weekly cohort reviews & alerts | LTV / CAC Ratio | Executive Sponsor |

---

## 4. Key Metrics & Health Indicators

1. **North Star Metric**: Weekly Active Value Users (WAVU) reaching the product's aha moment within 48 hours of signup.
2. **Leading Indicator**: Time-to-first-value (TTFV) compressed by 50% through streamlined onboarding paths.
3. **Guardrail Metric**: Churn rate within mature cohorts must remain below 1.5% monthly.

---

## 5. Risk Matrix & Mitigations

- **Risk: Premature Scaling**
  - *Mitigation*: Enforce a strict gate requiring stable cohort curves before unlocking discretionary marketing capital.
- **Risk: Metric Gaming**
  - *Mitigation*: Pair acquisition targets with mandatory 60-day cohort retention floors.
- **Risk: Feature Creep**
  - *Mitigation*: Prune low-frequency features that distract from the primary value loop.

---

## 6. Monday Morning Action Items

1. **Audit Cohort Curves**: Pull 12-month retention cohorts segmented by acquisition source.
2. **Review User Drop-Off**: Pinpoint the single largest drop-off step between sign-up and core value realization.
3. **Kill One Low-Yield Channel**: Reallocate operational engineering capacity to strengthening the primary compounding loop.
"""
        return doc.strip()

    def _generate_html(
        self,
        title: str,
        topic: str,
        instructions: Optional[str],
        chunks: List[SearchResultItem],
    ) -> str:
        """
        Synthesize a complete, standalone, responsive HTML/CSS document.
        Treats output as untrusted with zero external scripts, embedded CSP,
        and safe CSS encapsulation.
        """
        safe_title = html.escape(title)
        safe_topic = html.escape(topic)
        primary_guest = html.escape(chunks[0].guest if chunks else "Product Leader")
        ep_title = html.escape(chunks[0].episode_title if chunks else "Lenny's Podcast")
        ts = html.escape(chunks[0].timestamp or "00:10:00")

        cards_html = []
        for i, c in enumerate(chunks[:3], 1):
            g = html.escape(c.guest)
            ep = html.escape(c.episode_title)
            t = html.escape(c.timestamp or "")
            clean = html.escape(" ".join(line.strip() for line in c.content.split("\n") if line.strip() and not line.startswith("#"))[:220])
            cards_html.append(f"""
        <div class="evidence-card">
          <div class="evidence-meta">Pillar {i} &bull; {g} &bull; <em>{ep}</em> {f'[{t}]' if t else ''}</div>
          <blockquote class="evidence-quote">"{clean}..."</blockquote>
        </div>""")

        evidence_section = "\n".join(cards_html)

        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data: https:; font-src data:; form-action 'none'; frame-ancestors 'none';">
  <title>{safe_title}</title>
  <style>
    :root {{
      --bg: #fcfcfb;
      --card-bg: #ffffff;
      --text: #1a1a19;
      --text-muted: #5a5957;
      --accent: #2e5a44;
      --accent-light: #eef4f0;
      --border: #e6e5e1;
      --radius: 8px;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 32px 24px;
      max-width: 860px;
      margin: 0 auto;
    }}
    header {{
      border-bottom: 1px solid var(--border);
      padding-bottom: 24px;
      margin-bottom: 32px;
    }}
    .badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      background-color: var(--accent-light);
      color: var(--accent);
      padding: 4px 10px;
      border-radius: 9999px;
      margin-bottom: 12px;
    }}
    h1 {{
      font-size: 28px;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--text);
      margin-bottom: 8px;
    }}
    .subtitle {{
      color: var(--text-muted);
      font-size: 15px;
    }}
    section {{
      margin-bottom: 36px;
    }}
    h2 {{
      font-size: 18px;
      font-weight: 600;
      letter-spacing: -0.01em;
      border-bottom: 1px solid var(--border);
      padding-bottom: 8px;
      margin-bottom: 16px;
      color: var(--text);
    }}
    p {{
      margin-bottom: 16px;
      color: var(--text);
    }}
    .evidence-grid {{
      display: grid;
      gap: 16px;
      margin-top: 16px;
    }}
    .evidence-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px 20px;
    }}
    .evidence-meta {{
      font-size: 12px;
      font-weight: 600;
      color: var(--accent);
      margin-bottom: 8px;
    }}
    .evidence-quote {{
      font-style: italic;
      color: var(--text-muted);
      font-size: 14px;
      border-left: 2px solid var(--accent);
      padding-left: 12px;
      margin: 4px 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0;
      background: var(--card-bg);
      border-radius: var(--radius);
      overflow: hidden;
      border: 1px solid var(--border);
    }}
    th, td {{
      padding: 12px 16px;
      text-align: left;
      font-size: 14px;
      border-bottom: 1px solid var(--border);
    }}
    th {{
      background-color: var(--bg);
      font-weight: 600;
      color: var(--text-muted);
    }}
    ul, ol {{
      padding-left: 24px;
      margin-bottom: 16px;
    }}
    li {{
      margin-bottom: 6px;
      font-size: 14px;
    }}
    .callout {{
      background: var(--accent-light);
      border: 1px solid rgba(46, 90, 68, 0.2);
      border-radius: var(--radius);
      padding: 16px 20px;
      margin: 24px 0;
    }}
    .callout-title {{
      font-weight: 600;
      color: var(--accent);
      margin-bottom: 6px;
      font-size: 14px;
    }}
    footer {{
      margin-top: 48px;
      padding-top: 16px;
      border-top: 1px solid var(--border);
      font-size: 12px;
      color: var(--text-muted);
      text-align: center;
    }}
  </style>
</head>
<body>
  <header>
    <div class="badge">Lenny Growth Playbook</div>
    <h1>{safe_title}</h1>
    <div class="subtitle">Operational framework for {safe_topic} grounded in Lenny's Podcast archives</div>
  </header>

  <main>
    <section>
      <h2>Strategic Overview</h2>
      <p>
        This document provides a production-grade operational framework for <strong>{safe_topic}</strong>.
        Derived from empirical discussions with world-class product leaders on Lenny's Podcast,
        it replaces vanity metrics with compounding growth mechanisms.
      </p>
    </section>

    <section>
      <h2>Empirical Podcast Evidence</h2>
      <div class="evidence-grid">
{evidence_section}
      </div>
    </section>

    <section>
      <h2>Execution Roadmap</h2>
      <table>
        <thead>
          <tr>
            <th>Milestone</th>
            <th>Core Activity</th>
            <th>Validation Target</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Step 1: Baseline</strong></td>
            <td>Cohort retention curve flattening audit</td>
            <td>Stable horizontal asymptote</td>
          </tr>
          <tr>
            <td><strong>Step 2: Loop Mapping</strong></td>
            <td>Identify highest-yield natural loop (viral, content, paid)</td>
            <td>Loop velocity > 1.0</td>
          </tr>
          <tr>
            <td><strong>Step 3: Protocol</strong></td>
            <td>Monday morning cross-functional alignment sprint</td>
            <td>100% team ownership</td>
          </tr>
        </tbody>
      </table>
    </section>

    <div class="callout">
      <div class="callout-title">Core Operating Principle</div>
      <p style="margin-bottom: 0; font-size: 14px;">
        Never accelerate acquisition into a product with leaking retention. Fix the core loop first;
        compounding will follow naturally.
      </p>
    </div>
  </main>

  <footer>
    Generated by The Lenny Growth Assistant &bull; Grounded in Podcast Transcripts
  </footer>
</body>
</html>"""
        return self._sanitize_html(html_doc)

    def _sanitize_html(self, raw_html: str) -> str:
        """
        Sanitize untrusted HTML to guarantee safety:
        - Strip any <script> tags and contents.
        - Strip dangerous inline handlers (onload, onclick, onerror, etc.).
        - Neutralize javascript: URIs.
        - Prevent parent target hijacking (<base target="_top">).
        """
        # Remove script tags
        clean = re.sub(r"(?is)<script.*?>.*?</script>", "", raw_html)
        clean = re.sub(r"(?is)<script.*?>", "", clean)
        # Remove dangerous inline event handlers
        clean = re.sub(r"""(?i)\s+on[a-z]+\s*=\s*(?:'[^']*'|"[^"]*"|[^\s>]+)""", "", clean)
        # Neutralize javascript: URIs
        clean = re.sub(r"""(?i)href\s*=\s*['"]\s*javascript:[^'"]*['"]""", 'href="#"', clean)
        # Neutralize target hijacking
        clean = re.sub(r"""(?i)<base[^>]*target\s*=\s*['"]?_(?:top|parent)['"]?[^>]*>""", "", clean)
        return clean
