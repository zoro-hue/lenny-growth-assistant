import os
import sys
import uuid
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to sys.path to enable direct running
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from backend.app.database import get_session_maker, init_models
from backend.app.models.session import SessionModel
from backend.app.models.message import MessageModel
from backend.app.models.artifact import ArtifactModel
from backend.app.models.transcript import TranscriptMetadataModel, TranscriptChunkModel
from backend.app.services.ingestion_service import IngestionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_demo")


DEMO_CONVERSATIONS = [
    # TODAY 1
    {
        "id": "demo-balfour-channel-model",
        "title": "Brian Balfour — Channel Model Fit",
        "days_ago": 0,
        "hours_ago": 2,
        "model_id": "openai-cloud",
        "messages": [
            {
                "role": "user",
                "content": "Why does Brian Balfour argue that traditional acquisition funnels are dead, and how does Channel-Model Fit work?",
            },
            {
                "role": "assistant",
                "content": (
                    "Based on Brian Balfour's Four Fits Framework on Lenny's Podcast (Episode #112), "
                    "distribution channels do not bend to your product—your product must bend to the channel.\n\n"
                    "### 1. Products Are Built to Fit Channels\n"
                    "Distribution channels (Google SEO, Meta ads, Virality, App Stores) are external platforms with their own rules. "
                    "You cannot build a product and then 'find a channel'; the product characteristics must be engineered "
                    "specifically to exploit the natural dynamics of the channel.\n\n"
                    "### 2. Channel-Model Fit & The Growth Danger Zone\n"
                    "Your pricing model determines what Customer Acquisition Cost (CAC) you can afford:\n"
                    "- **Low ARPU ($10/mo):** Requires low CAC channels such as virality, UGC, or organic search. Outbound sales will bankrupt the business.\n"
                    "- **High ARPU ($100k+/yr):** Can support enterprise sales, high-touch onboarding, and multi-month sales cycles.\n"
                    "- **The Danger Zone:** Companies with ARPU too high for frictionless self-serve but too low to support direct sales reps get trapped without a viable channel."
                ),
                "citations": [
                    {
                        "id": "cit-balfour-1",
                        "episodeNumber": 112,
                        "episodeTitle": "Brian Balfour on the Four Fits Framework and Why Growth Is a System",
                        "guest": "Brian Balfour",
                        "guestRole": "Founder & CEO of Reforge, Former VP Growth at HubSpot",
                        "timestamp": "00:01:28",
                        "quoteExcerpt": "Distribution channels—whether it is Google SEO, Facebook ads, Apple App Store, or Virality—do not care about your product. You do not control the rules of Google or Meta; they control their algorithms.",
                        "episodeUrl": "https://www.youtube.com/watch?v=BrianBalfourGrowth",
                        "whyThisSource": "Direct evidence from Brian Balfour supporting the Channel-Model Fit argument.",
                    },
                    {
                        "id": "cit-balfour-2",
                        "episodeNumber": 112,
                        "episodeTitle": "Brian Balfour on the Four Fits Framework and Why Growth Is a System",
                        "guest": "Brian Balfour",
                        "guestRole": "Founder & CEO of Reforge, Former VP Growth at HubSpot",
                        "timestamp": "00:02:20",
                        "quoteExcerpt": "Your pricing model determines what CAC you can afford. If your Average Revenue Per User (ARPU) is $10 a month, you cannot use an outbound sales team or expensive enterprise marketing—the math simply will not work.",
                        "episodeUrl": "https://www.youtube.com/watch?v=BrianBalfourGrowth",
                        "whyThisSource": "Direct evidence from Brian Balfour on CAC alignment with pricing model.",
                    },
                ],
            },
        ],
    },
    # TODAY 2
    {
        "id": "demo-winters-retention",
        "title": "Retention Curves — What Actually Matters",
        "days_ago": 0,
        "hours_ago": 3,
        "model_id": "ollama-local",
        "messages": [
            {
                "role": "user",
                "content": "How does Casey Winters recommend measuring true product-market fit using cohort retention curves?",
            },
            {
                "role": "assistant",
                "content": (
                    "On Episode 42 of Lenny's Podcast, Casey Winters articulates the single quantitative indicator of real Product-Market Fit:\n\n"
                    "### The Asymptote Floor\n"
                    "Product-market fit is revealed exclusively when a cohort retention curve stops declining and runs completely flat, "
                    "parallel to the horizontal x-axis by Month 3 or Month 6. If the curve continues dropping monotonically toward zero, "
                    "you do not have PMF, regardless of top-of-funnel conversion or user signups.\n\n"
                    "### Benchmarks by Business Model\n"
                    "- **Consumer Subscription / Social:** A retention floor of **20% to 30%** can build a massive business if organic acquisition is massive.\n"
                    "- **B2B SaaS:** Requires a logo retention floor of **70% to 80%**, and Net Revenue Retention (NRR) above **110% to 120%** via seat and usage expansion."
                ),
                "citations": [
                    {
                        "id": "cit-winters-1",
                        "episodeNumber": 42,
                        "episodeTitle": "Casey Winters on Growth Loops, Retention, and Why Blended Metrics Lie",
                        "guest": "Casey Winters",
                        "guestRole": "Former CPO at Eventbrite, Growth Lead at Pinterest",
                        "timestamp": "00:00:44",
                        "quoteExcerpt": "Product-market fit is revealed when a cohort retention curve stops dropping and runs completely flat parallel to the horizontal axis. If you don't have that horizontal floor by Month 3 or Month 6, nothing else you do matters.",
                        "episodeUrl": "https://www.youtube.com/watch?v=WlRfyEpAKxw",
                        "whyThisSource": "Empirical methodology from Casey Winters on cohort retention flattening.",
                    },
                    {
                        "id": "cit-winters-2",
                        "episodeNumber": 42,
                        "episodeTitle": "Casey Winters on Growth Loops, Retention, and Why Blended Metrics Lie",
                        "guest": "Casey Winters",
                        "guestRole": "Former CPO at Eventbrite, Growth Lead at Pinterest",
                        "timestamp": "00:01:25",
                        "quoteExcerpt": "In consumer subscription or social, a flat retention curve at 20% to 30% can build a massive business... In B2B SaaS, your logo retention floor needs to be 70% or 80%, and your Net Revenue Retention (NRR) should be over 110% to 120%.",
                        "episodeUrl": "https://www.youtube.com/watch?v=WlRfyEpAKxw",
                        "whyThisSource": "Benchmark criteria for cohort asymptotes across consumer and B2B SaaS.",
                    },
                ],
            },
        ],
    },
    # TODAY 3
    {
        "id": "demo-ship30-pricing",
        "title": "Ship 30/30 — Pricing Strategy",
        "days_ago": 0,
        "hours_ago": 4,
        "model_id": "openai-cloud",
        "artifact": {
            "id": "art-ship30-pricing",
            "title": "Ship 30/30: The Channel-Model Pricing Law",
            "type": "markdown",
            "word_count": 1180,
            "source_count": 2,
            "content": """# The Channel-Model Pricing Law: Why Your Business Model Dictates Acquisition

*Synthesized from Brian Balfour's Four Fits Framework on Lenny's Podcast.*

---

Most founders treat pricing as a finance problem.

They calculate costs, check competitor rates, and set a monthly fee.

Then they hire a sales team and wonder why unit economics collapse.

Here is the immutable growth reality: **Your pricing model dictates your distribution channels, not your financial ambitions.**

---

## 1. The Power Law of Channel-Model Fit

In Episode 112, Brian Balfour warns against the "Growth Danger Zone":

> "Your pricing model determines what CAC you can afford. If your Average Revenue Per User (ARPU) is $10 a month, you cannot use an outbound sales team or expensive enterprise marketing—the math simply will not work."

When ARPU is $100/year, you must rely exclusively on compounding, zero-marginal-cost loops:
- Virality & Word-of-Mouth
- Programmatic SEO
- User-Generated Content

When ARPU reaches $100,000/year, you can fund multi-month enterprise sales cycles, field engineers, and executive dinners.

---

## 2. Escaping the Danger Zone

Companies die when their ARPU sits at $1,000 to $5,000 annually. It is too expensive for frictionless self-serve credit card checkout, but generates insufficient margin to pay account executives a viable commission.

To escape:
1. **Push down to pure self-serve:** Reduce onboarding friction, enforce Time-to-Aha under 8 minutes, and automate activation.
2. **Push up to enterprise:** Add SSO, audit logs, compliance guarantees, and dedicated account management to justify a $25k+ contract floor.

---

## 3. Tactical 5-Step Pricing Audit

1. **Calculate Fully-Loaded CAC:** Include sales salaries, tools, marketing overhead, and onboarding headcount.
2. **Map CAC to Payback Period:** In SaaS, CAC payback must be under 12 months for self-serve and under 18 months for enterprise.
3. **Audit Problem Frequency:** Match recurring billing cycles directly to the natural cadence of user habit realization.
4. **Eliminate Activation Paywalls:** Never charge users before they experience the core value milestone.
5. **Monetize Governance, Not Core Utility:** Restrict collaboration, data retention, and security behind enterprise tiers.
""",
        },
        "messages": [
            {
                "role": "user",
                "content": "Write a Ship 30/30 essay on pricing strategy and channel-model fit.",
            },
            {
                "role": "assistant",
                "content": (
                    "I've synthesized a comprehensive Ship 30 for 30 playbook titled **\"The Channel-Model Pricing Law: Why Your Business Model Dictates Acquisition\"** "
                    "grounded in transcript frameworks from Brian Balfour.\n\n"
                    "The complete ~1,180-word playbook with a 1-3-1 hook, Danger Zone diagnostic matrix, and tactical 5-step audit is open in the Artifact Workbench to your right."
                ),
                "artifact_id": "art-ship30-pricing",
                "citations": [
                    {
                        "id": "cit-balfour-pricing-1",
                        "episodeNumber": 112,
                        "episodeTitle": "Brian Balfour on the Four Fits Framework and Why Growth Is a System",
                        "guest": "Brian Balfour",
                        "guestRole": "Founder & CEO of Reforge, Former VP Growth at HubSpot",
                        "timestamp": "00:02:20",
                        "quoteExcerpt": "Low ARPU products require low CAC distribution channels like virality, user-generated content, or organic search. Conversely, high ARPU products ($100k+ annual contracts) can afford direct sales...",
                        "episodeUrl": "https://www.youtube.com/watch?v=BrianBalfourGrowth",
                        "whyThisSource": "Direct evidence from Brian Balfour on channel-model pricing laws.",
                    },
                ],
            },
        ],
    },
    # TODAY 4
    {
        "id": "demo-b2b-saas-playbook",
        "title": "B2B SaaS Retention Playbook",
        "days_ago": 0,
        "hours_ago": 5,
        "model_id": "openai-cloud",
        "artifact": {
            "id": "art-b2b-retention-playbook",
            "title": "B2B SaaS Retention Playbook: Cohort Flattening & Natural Frequency",
            "type": "markdown",
            "word_count": 1350,
            "source_count": 3,
            "content": """# B2B SaaS Retention Playbook: Cohort Flattening & Natural Frequency

*Synthesized from Lenny's Podcast archives featuring Casey Winters, Elena Verna, and Brian Balfour.*

---

## Executive Summary

B2B SaaS retention is governed by two empirical laws:
1. **The Asymptote Law (Casey Winters):** Unflattened retention curves reflect lack of Product-Market Fit.
2. **The Natural Frequency Law (Elena Verna):** Measuring daily engagement for non-daily problems creates artificial churn.

---

## Stage 1: Cohort Curve Flattening

To evaluate if your retention asymptote is viable:
- **Logo Retention Floor:** Must stabilize at 70–80% by Month 3.
- **Net Revenue Retention (NRR):** Must exceed 115% via natural expansion loops.
- **Leaky Bucket Diagnostic:** Stop acquisition spend if Month 6 retention falls below 60%.

---

## Stage 2: Aligning with Problem Cadence

Elena Verna highlights that B2B tools solve jobs with distinct rhythms:
- **Daily:** Messaging, task management, code review.
- **Weekly:** Sprint planning, status reporting, analytics.
- **Monthly/Quarterly:** Financial close, payroll, performance reviews.

Trying to force daily push notifications on quarterly workflows irritates executive buyers and drives unsubscribes.

---

## Stage 3: The 7-Step Operational Checklist

1. Identify the core Habit Moment where users achieve recurring value.
2. Verify that 40%+ of active users would be "very disappointed" if the tool vanished.
3. Eliminate credit card requirements before activation.
4. Establish Time-to-Aha under 8 minutes.
5. Measure cohort retention by ICP archetype, not blended averages.
6. Build expansion triggers tied directly to seat count and data volume.
7. Conduct quarterly pre-mortems on cohort drop-off inflection points.
""",
        },
        "messages": [
            {
                "role": "user",
                "content": "Generate a comprehensive tactical playbook for B2B SaaS retention benchmarks and monetization loops.",
            },
            {
                "role": "assistant",
                "content": (
                    "I've generated a comprehensive Markdown playbook titled **\"B2B SaaS Retention Playbook: Cohort Flattening & Natural Frequency\"** "
                    "grounded in transcript evidence from Casey Winters, Elena Verna, and Brian Balfour.\n\n"
                    "The operational framework, cohort benchmark tables, and 7-step checklist are open in the Artifact Workbench to your right."
                ),
                "artifact_id": "art-b2b-retention-playbook",
                "citations": [
                    {
                        "id": "cit-b2b-playbook-1",
                        "episodeNumber": 42,
                        "episodeTitle": "Casey Winters on Growth Loops, Retention, and Why Blended Metrics Lie",
                        "guest": "Casey Winters",
                        "guestRole": "Former CPO at Eventbrite, Growth Lead at Pinterest",
                        "timestamp": "00:01:25",
                        "quoteExcerpt": "In B2B SaaS, your logo retention floor needs to be 70% or 80%, and your Net Revenue Retention (NRR) should be over 110% to 120% because existing accounts expand over time.",
                        "episodeUrl": "https://www.youtube.com/watch?v=WlRfyEpAKxw",
                        "whyThisSource": "Benchmark criteria for B2B SaaS logo retention and NRR.",
                    },
                    {
                        "id": "cit-b2b-playbook-2",
                        "episodeNumber": 88,
                        "episodeTitle": "Elena Verna on PLG, B2B Retention Benchmarks, and Monetization Loops",
                        "guest": "Elena Verna",
                        "guestRole": "Head of Growth at Lovable, Former Interim CMO at Miro & Amplitude",
                        "timestamp": "00:01:38",
                        "quoteExcerpt": "B2B growth loops must strictly align with the natural cadence of the organization. Trying to create daily habits for quarterly problems always creates churn.",
                        "episodeUrl": "https://www.youtube.com/watch?v=ElenaVernaPLG",
                        "whyThisSource": "Direct operational guidance on problem frequency alignment.",
                    },
                ],
            },
        ],
    },
    # YESTERDAY 1
    {
        "id": "demo-verna-plg",
        "title": "Elena Verna — Product-Led Growth",
        "days_ago": 1,
        "hours_ago": 26,
        "model_id": "openai-cloud",
        "messages": [
            {
                "role": "user",
                "content": "What is the single biggest misconception about PLG according to Elena Verna?",
            },
            {
                "role": "assistant",
                "content": (
                    "In Episode 88 of Lenny's Podcast, Elena Verna explains that the most destructive misconception "
                    "is assuming Product-Led Growth is just a self-serve pricing page and a free trial.\n\n"
                    "### 1. True PLG is an Organizational Distribution Model\n"
                    "PLG means the product itself performs the heavy lifting of acquisition, retention, and expansion. "
                    "If your product requires a human sales rep to explain why it is valuable before the user feels the value, "
                    "you do not have a PLG motion.\n\n"
                    "### 2. The 8-Minute Time-to-Aha Rule\n"
                    "Elena highlights that in a true PLG motion, your **Time-to-Aha must be under 8 minutes**. "
                    "If users cannot experience the core value proposition in their very first session without reading documentation, "
                    "onboarding drop-off will routinely exceed 80%.\n\n"
                    "### 3. Monetize Governance, Not Activation\n"
                    "Never place a paywall before the user has formed a habit. Charge for organizational collaboration, "
                    "security (SSO/SCIM), and administrative controls when multiple teams adopt the tool."
                ),
                "citations": [
                    {
                        "id": "cit-verna-plg-1",
                        "episodeNumber": 88,
                        "episodeTitle": "Elena Verna on PLG, B2B Retention Benchmarks, and Monetization Loops",
                        "guest": "Elena Verna",
                        "guestRole": "Head of Growth at Lovable, Former Interim CMO at Miro & Amplitude",
                        "timestamp": "00:00:45",
                        "quoteExcerpt": "The biggest mistake is assuming PLG is just a self-serve pricing page and a free trial. PLG is an organizational distribution model where the product itself does the heavy lifting of acquisition, retention, and expansion.",
                        "episodeUrl": "https://www.youtube.com/watch?v=ElenaVernaPLG",
                        "whyThisSource": "Direct statement on PLG organizational definition and Time-to-Aha.",
                    },
                    {
                        "id": "cit-verna-plg-2",
                        "episodeNumber": 88,
                        "episodeTitle": "Elena Verna on PLG, B2B Retention Benchmarks, and Monetization Loops",
                        "guest": "Elena Verna",
                        "guestRole": "Head of Growth at Lovable, Former Interim CMO at Miro & Amplitude",
                        "timestamp": "00:02:40",
                        "quoteExcerpt": "Never paywall activation. If you put a credit card wall or hard paywall before the user has validated that the product solves their problem, you destroy your conversion loop. You should monetize on scale and organizational governance...",
                        "episodeUrl": "https://www.youtube.com/watch?v=ElenaVernaPLG",
                        "whyThisSource": "Tactical guidance on monetization placement and paywall timing.",
                    },
                ],
            },
        ],
    },
    # YESTERDAY 2
    {
        "id": "demo-vohra-pmf",
        "title": "Rahul Vohra — PMF Framework",
        "days_ago": 1,
        "hours_ago": 28,
        "model_id": "openai-cloud",
        "messages": [
            {
                "role": "user",
                "content": "How did Rahul Vohra operationalize the 40% PMF survey rule at Superhuman?",
            },
            {
                "role": "assistant",
                "content": (
                    "On Episode 15 of Lenny's Podcast, Rahul Vohra shared how Superhuman turned Sean Ellis's 40% survey question "
                    "into an active product engine that systematically drove their PMF score from 22% to 58%:\n\n"
                    "### The 4-Step PMF Engine\n"
                    "1. **Survey and Segment:** Ask: *'How would you feel if you could no longer use the product?'* (Very disappointed, Somewhat disappointed, Not disappointed).\n"
                    "2. **Analyze Your High-Expectation Advocates:** Isolate the 'Very disappointed' group to identify the exact customer archetype who finds undeniable value.\n"
                    "3. **Filter the Middle Cohort:** Look at the 'Somewhat disappointed' group, but **ONLY** those who share the same primary benefit as the 'Very disappointed' lovers. Politely ignore everyone else so you don't build a Frankenstein product.\n"
                    "4. **The 50/50 Roadmap Allocation:** Dedicate half of your engineering roadmap to doubling down on what fans love, and the other half to systematically removing blockers for that specific target middle cohort."
                ),
                "citations": [
                    {
                        "id": "cit-vohra-pmf-1",
                        "episodeNumber": 15,
                        "episodeTitle": "Rahul Vohra on The Product-Market Fit Engine and Building Superhuman",
                        "guest": "Rahul Vohra",
                        "guestRole": "Founder & CEO of Superhuman",
                        "timestamp": "00:00:52",
                        "quoteExcerpt": "We surveyed our users and only 22% said they would be very disappointed if Superhuman disappeared. Instead of despairing, we created a systematic method to drive that number up to 58%.",
                        "episodeUrl": "https://www.youtube.com/watch?v=ourIThGMpYE",
                        "whyThisSource": "Operational breakdown of the Superhuman 40% PMF engine.",
                    },
                    {
                        "id": "cit-vohra-pmf-2",
                        "episodeNumber": 15,
                        "episodeTitle": "Rahul Vohra on The Product-Market Fit Engine and Building Superhuman",
                        "guest": "Rahul Vohra",
                        "guestRole": "Founder & CEO of Superhuman",
                        "timestamp": "00:02:24",
                        "quoteExcerpt": "Because if you listen to everyone, you will build a Frankenstein product. Users who want completely different value propositions will pull your product in directions that dilute what makes it magical...",
                        "episodeUrl": "https://www.youtube.com/watch?v=ourIThGMpYE",
                        "whyThisSource": "Guidance on why feedback from non-ICP users must be filtered.",
                    },
                ],
            },
        ],
    },
]


async def seed_demo_conversations(db: AsyncSession, reset: bool = True) -> Dict[str, Any]:
    """
    Seeds the authoritative set of 6 professional demo conversations.
    If reset=True, clears previous sessions to ensure a clean sidebar.
    """
    # 1. Ensure transcripts are ingested first
    await IngestionService.ingest_source(db=db, source="sample", force_refresh=False)

    if reset:
        logger.info("[SEED] Resetting existing sessions and messages for clean demo state...")
        await db.execute(delete(ArtifactModel))
        await db.execute(delete(MessageModel))
        await db.execute(delete(SessionModel))
        await db.commit()

    now = datetime.now(timezone.utc)
    created_sessions = []

    for conv in DEMO_CONVERSATIONS:
        # Check if already exists
        stmt = select(SessionModel).where(SessionModel.id == conv["id"])
        existing = (await db.execute(stmt)).scalar_one_or_none()
        if existing and not reset:
            logger.info(f"[SEED] Session '{conv['title']}' already exists, skipping.")
            continue

        created_time = now - timedelta(days=conv["days_ago"], hours=conv["hours_ago"])
        updated_time = created_time + timedelta(minutes=15)

        session = SessionModel(
            id=conv["id"],
            title=conv["title"],
            active_model_id=conv["model_id"],
            created_at=created_time,
            updated_at=updated_time,
        )
        db.add(session)
        await db.flush()

        # Seed artifact if present
        art_id = None
        if "artifact" in conv:
            art_data = conv["artifact"]
            artifact = ArtifactModel(
                id=art_data["id"],
                session_id=session.id,
                title=art_data["title"],
                type=art_data["type"],
                content=art_data["content"],
                word_count=art_data["word_count"],
                source_count=art_data["source_count"],
                allow_scripts=False,
                created_at=created_time + timedelta(minutes=5),
                updated_at=updated_time,
            )
            db.add(artifact)
            await db.flush()
            art_id = artifact.id

        # Seed messages
        for msg_data in conv["messages"]:
            msg_created = created_time + timedelta(minutes=2 if msg_data["role"] == "user" else 4)
            message = MessageModel(
                id=f"msg-{uuid.uuid4().hex[:12]}",
                session_id=session.id,
                role=msg_data["role"],
                content=msg_data["content"],
                status="complete",
                citations=msg_data.get("citations", []),
                artifact_id=msg_data.get("artifact_id", art_id if msg_data["role"] == "assistant" else None),
                created_at=msg_created,
                updated_at=msg_created,
            )
            db.add(message)

        created_sessions.append(session.id)

    await db.commit()
    logger.info(f"[SEED] Successfully seeded {len(created_sessions)} demo conversations.")
    return {"status": "success", "sessions_created": len(created_sessions), "session_ids": created_sessions}


async def main():
    await init_models()
    reset = "--reset" in sys.argv or "-r" in sys.argv
    session_maker = get_session_maker()
    async with session_maker() as session:
        res = await seed_demo_conversations(session, reset=reset)
        print(f"Seed complete: {res}")


if __name__ == "__main__":
    asyncio.run(main())
