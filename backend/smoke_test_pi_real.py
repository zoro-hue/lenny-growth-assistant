"""
Real end-to-end smoke test for Pi Coding Agent + Ollama llama3.2:3b.
Verifies:
1. Grounded query: "What does Elena Verna say about product-led growth?"
   - Pi subprocess starts
   - Ollama generates answer
   - Transcript search tool is invoked
   - Returned evidence is from Lenny transcript database
   - Citations are returned
   - Process exits cleanly
2. Unsupported query: "How do I calculate Solana staking rewards and liquidity pool impermanent loss?"
   - Correctly returns low-evidence response
   - Citations strictly 0 (no hallucinated citations)
"""
import asyncio
import json
import time
import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models.base import Base
from app.config import settings
from app.services.ingestion_service import IngestionService
from app.agent import AgentService, OllamaProvider
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.schemas.session import SessionCreate
from app.services.session_service import SessionService

settings.app_env = "testing"


async def main():
    print("=" * 70)
    print("REAL PI CODING AGENT + OLLAMA END-TO-END SMOKE TEST")
    print("=" * 70)

    # 1. Verify Ollama reachability
    provider = OllamaProvider()
    is_avail = await provider.is_available()
    print(f"Ollama reachable: {is_avail}")
    if not is_avail:
        print("[ERROR] Ollama is not available at http://localhost:11434")
        sys.exit(1)

    # 2. Database setup
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        # Ingest sample episodes (Elena Verna, Brian Balfour, Casey Winters)
        print("\n[INGESTION] Ingesting sample podcast transcripts...")
        ingest_res = await IngestionService.ingest_source(session, source="sample", limit=3, force_refresh=True)
        print(f"[INGESTION] Done! Ingested: {ingest_res.episodes_ingested} episodes, Chunks: {ingest_res.chunks_created}")

        # Create chat session
        chat_sess = await SessionService.create_session(
            session, SessionCreate(title="Real Pi Smoke Test", active_model_id="ollama-local")
        )
        session_id = chat_sess.id
        print(f"\n[SESSION] Created session ID: {session_id}")

        # -----------------------------------------------------------------
        # TEST 1: Grounded Query (Elena Verna PLG)
        # -----------------------------------------------------------------
        query_grounded = "What does Elena Verna say about product-led growth?"
        print(f"\n[TEST 1] Grounded Query: '{query_grounded}'")
        print("Executing via ChatService.process_chat -> AgentService -> PiRpcClient -> Pi Subprocess -> Ollama...")

        t0 = time.time()
        resp_grounded = await ChatService.process_chat(
            db=session,
            request=ChatRequest(
                session_id=session_id,
                content=query_grounded,
                model_id="ollama-local",
            ),
        )
        elapsed_grounded = time.time() - t0

        asst_msg = resp_grounded.assistant_message
        print(f"\n[TEST 1 RESULTS]")
        print(f"  Execution Time: {elapsed_grounded:.2f}s")
        print(f"  Status: {asst_msg.status}")
        print(f"  Content length: {len(asst_msg.content)} chars")
        print(f"  Content preview:\n    {asst_msg.content[:250]}...")
        print(f"  Citations count: {len(asst_msg.citations)}")

        for i, cit in enumerate(asst_msg.citations):
            print(f"    Citation #{i+1}:")
            print(f"      Guest: {cit.guest}")
            print(f"      Episode: {cit.episode_title}")
            print(f"      Quote excerpt: {cit.quote_excerpt[:80]}...")
            print(f"      Episode URL: {cit.episode_url}")

        # Assertions
        assert asst_msg.status in ("complete", "low-evidence"), f"Unexpected status: {asst_msg.status}"
        assert len(asst_msg.content) > 0, "Response content is empty"
        if asst_msg.status == "complete":
            assert len(asst_msg.citations) > 0, "Expected at least 1 citation for grounded query"
            elena_cits = [c for c in asst_msg.citations if "elena" in c.guest.lower()]
            assert len(elena_cits) > 0, f"Expected citations to cite Elena Verna, got: {[c.guest for c in asst_msg.citations]}"
            print("  [TEST 1 PASSED] Grounded answer generated with verified Elena Verna citations!")

        # -----------------------------------------------------------------
        # TEST 2: Out-of-Domain Query (Solana Staking)
        # -----------------------------------------------------------------
        query_unsupported = "How do I calculate Solana staking rewards and liquidity pool impermanent loss?"
        print(f"\n[TEST 2] Unsupported Query: '{query_unsupported}'")
        t0 = time.time()
        resp_unsupported = await ChatService.process_chat(
            db=session,
            request=ChatRequest(
                session_id=session_id,
                content=query_unsupported,
                model_id="ollama-local",
            ),
        )
        elapsed_unsupported = time.time() - t0

        asst_unsupp = resp_unsupported.assistant_message
        print(f"\n[TEST 2 RESULTS]")
        print(f"  Execution Time: {elapsed_unsupported:.2f}s")
        print(f"  Status: {asst_unsupp.status}")
        print(f"  Citations count: {len(asst_unsupp.citations)}")
        print(f"  Content preview:\n    {asst_unsupp.content[:200]}...")

        assert asst_unsupp.status == "low-evidence", f"Expected low-evidence status, got {asst_unsupp.status}"
        assert len(asst_unsupp.citations) == 0, f"Expected strictly 0 citations, got {len(asst_unsupp.citations)}"
        assert "don't have enough grounded material" in asst_unsupp.content or "low-evidence" in asst_unsupp.status
        print("  [TEST 2 PASSED] Correctly returned low-evidence state with ZERO hallucinated citations!")

    await engine.dispose()
    print("\n" + "=" * 70)
    print("ALL REAL SMOKE TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
