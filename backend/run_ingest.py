#!/usr/bin/env python
"""
Lenny Growth Assistant — Knowledge Base CLI Ingestion Script
Usage:
    python run_ingest.py [--sample] [--limit N] [--force] [--github] [--stats]
"""
import sys
import asyncio
import argparse
import logging

from app.database import get_session_maker, init_models, check_database_health
from app.services.ingestion_service import IngestionService
from app.models.transcript import TranscriptMetadataModel, TranscriptChunkModel
from sqlalchemy import select, func

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ingest_cli")


async def print_stats():
    session_maker = get_session_maker()
    async with session_maker() as db:
        ep_count = await db.scalar(select(func.count()).select_from(TranscriptMetadataModel)) or 0
        chk_count = await db.scalar(select(func.count()).select_from(TranscriptChunkModel)) or 0
        bind = db.bind or getattr(db, "_bind", None)
        dialect = bind.dialect.name if bind else "unknown"

        print("\n" + "=" * 55)
        print("  THE LENNY GROWTH ASSISTANT — KNOWLEDGE BASE STATS")
        print("=" * 55)
        print(f"  Database Dialect : {dialect}")
        print(f"  Total Episodes   : {ep_count}")
        print(f"  Total Chunks     : {chk_count}")
        print("=" * 55 + "\n")


async def main():
    parser = argparse.ArgumentParser(description="Ingest Lenny's Podcast transcripts into the knowledge base.")
    parser.add_argument("--source", choices=["sample", "local", "github"], default="sample", help="Transcript source")
    parser.add_argument("--github", action="store_true", help="Shorthand for --source github")
    parser.add_argument("--sample", action="store_true", help="Shorthand for --source sample")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of episodes to process")
    parser.add_argument("--force", action="store_true", help="Force refresh existing episodes and re-chunk")
    parser.add_argument("--stats", action="store_true", help="Show knowledge base statistics and exit")
    args = parser.parse_args()

    # Verify tables
    await init_models()

    if args.stats:
        await print_stats()
        return

    source = "github" if args.github else ("sample" if args.sample else args.source)

    print("\n" + "=" * 65)
    print(f"  STARTING TRANSCRIPT INGESTION (Source: {source.upper()})")
    print("=" * 65)

    session_maker = get_session_maker()
    async with session_maker() as db:
        res = await IngestionService.ingest_source(
            db=db,
            source=source,
            limit=args.limit,
            force_refresh=args.force,
        )

        print("\n" + "-" * 65)
        print("  INGESTION SUMMARY")
        print("-" * 65)
        print(f"  Status               : {res.status.upper()}")
        print(f"  Episodes Discovered  : {res.episodes_discovered}")
        print(f"  Episodes Ingested    : {res.episodes_ingested}")
        print(f"  Episodes Skipped     : {res.episodes_skipped}")
        print(f"  Episodes Failed      : {res.episodes_failed}")
        print(f"  Total Chunks Created : {res.chunks_created}")
        print(f"  Duration             : {res.duration_seconds}s")
        print("-" * 65)

        if res.details:
            print("\n  Processed Episodes:")
            for d in res.details:
                chk = f"({d.get('chunk_count', 0)} chunks)" if 'chunk_count' in d else ""
                print(f"   • [{d.get('status').upper()}] {d.get('guest')} — {d.get('title')} {chk}")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
