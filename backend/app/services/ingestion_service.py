import os
import glob
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from ..config import settings
from ..models.transcript import TranscriptMetadataModel, TranscriptChunkModel
from ..schemas.knowledge import IngestResponse
from .chunking_service import ChunkingService
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class IngestionService:
    """
    Idempotent transcript ingestion pipeline with metadata storage,
    speaker-aware chunking, and pgvector embeddings.
    """

    @classmethod
    def parse_frontmatter(cls, raw_content: str) -> Tuple[Dict[str, Any], str]:
        """Extracts YAML frontmatter metadata and body text from markdown."""
        if raw_content.startswith("---"):
            parts = raw_content.split("---", 2)
            if len(parts) >= 3:
                raw_fm = parts[1]
                body = parts[2].strip()
                meta: Dict[str, Any] = {}
                for line in raw_fm.strip().splitlines():
                    if ":" in line:
                        k, v = line.split(":", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        meta[k] = v
                return meta, body
        return {}, raw_content.strip()

    @classmethod
    async def ingest_source(
        cls,
        db: AsyncSession,
        source: str = "sample",
        limit: Optional[int] = None,
        force_refresh: bool = False,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> IngestResponse:
        """
        Executes ingestion across discovered sources.
        Idempotent: skips already ingested episodes unless force_refresh=True.
        """
        start_time = time.time()
        c_size = chunk_size or settings.chunk_size
        c_overlap = chunk_overlap or settings.chunk_overlap

        logger.info(f"[INGESTION] Starting ingestion pipeline (source={source}, force_refresh={force_refresh})")

        # Discover raw transcript documents
        discovered_docs: List[Dict[str, Any]] = []
        if source in ("sample", "local"):
            discovered_docs = cls._discover_local_files(limit)
        elif source == "github":
            discovered_docs = await cls._discover_github_files(limit)
        else:
            discovered_docs = cls._discover_local_files(limit)

        logger.info(f"[INGESTION] Discovered sources: {len(discovered_docs)} documents.")

        episodes_ingested = 0
        episodes_skipped = 0
        episodes_failed = 0
        chunks_created_total = 0
        details: List[Dict[str, Any]] = []

        for doc in discovered_docs:
            title = doc.get("title", "Untitled Episode")
            guest = doc.get("guest", "Unknown Guest")
            source_url = doc.get("source_url") or doc.get("transcript_url") or ""

            # Check idempotency: does this episode already exist?
            existing_ep = await cls._find_existing_episode(db, title, source_url)

            if existing_ep and not force_refresh:
                logger.info(f"[INGESTION] Skipped duplicate episode: '{title}' ({guest})")
                episodes_skipped += 1
                details.append({
                    "title": title,
                    "guest": guest,
                    "status": "skipped_duplicate",
                    "chunk_count": existing_ep.chunk_count,
                })
                continue

            try:
                logger.info(f"[INGESTION] Processing episode: '{title}' by {guest}")
                body_text = doc["body"]
                chunks_data = ChunkingService.chunk_transcript(
                    body_text,
                    chunk_size=c_size,
                    chunk_overlap=c_overlap,
                )

                if not chunks_data:
                    logger.warning(f"[INGESTION] No chunks generated for episode: '{title}'")
                    episodes_failed += 1
                    details.append({
                        "title": title,
                        "guest": guest,
                        "status": "failed_no_chunks",
                    })
                    continue

                # Generate embeddings for chunks
                chunk_texts = [c.content for c in chunks_data]
                embeddings = await EmbeddingService.embed_texts(chunk_texts)

                # Persist in DB
                async with db.begin_nested():
                    # If updating existing episode, remove prior chunks
                    if existing_ep:
                        await db.execute(
                            delete(TranscriptChunkModel).where(TranscriptChunkModel.transcript_id == existing_ep.id)
                        )
                        ep_record = existing_ep
                        ep_record.chunk_count = len(chunks_data)
                    else:
                        ep_record = TranscriptMetadataModel(
                            episode_number=doc.get("episode_number"),
                            episode_title=title,
                            guest=guest,
                            guest_role=doc.get("guest_role"),
                            published_date=doc.get("published_date"),
                            audio_url=doc.get("audio_url"),
                            transcript_url=source_url,
                            duration_seconds=doc.get("duration_seconds"),
                            summary=doc.get("summary"),
                            chunk_count=len(chunks_data),
                        )
                        db.add(ep_record)
                        await db.flush()

                    for idx, chunk in enumerate(chunks_data):
                        emb = embeddings[idx] if idx < len(embeddings) else None
                        chunk_record = TranscriptChunkModel(
                            transcript_id=ep_record.id,
                            episode_number=ep_record.episode_number,
                            episode_title=title,
                            guest=guest,
                            guest_role=doc.get("guest_role"),
                            source_url=source_url,
                            chunk_index=chunk.chunk_index,
                            timestamp=chunk.timestamp,
                            content=chunk.content,
                            token_count=chunk.token_count,
                            embedding=emb,
                        )
                        db.add(chunk_record)

                await db.commit()

                logger.info(
                    f"[INGESTION] Successfully ingested: '{title}' ({guest}) — {len(chunks_data)} chunks."
                )
                episodes_ingested += 1
                chunks_created_total += len(chunks_data)
                details.append({
                    "title": title,
                    "guest": guest,
                    "status": "ingested",
                    "chunk_count": len(chunks_data),
                })

            except Exception as e:
                logger.error(f"[INGESTION] Failed to ingest episode '{title}': {e}", exc_info=True)
                await db.rollback()
                episodes_failed += 1
                details.append({
                    "title": title,
                    "guest": guest,
                    "status": "failed",
                    "error": str(e),
                })

        duration = round(time.time() - start_time, 2)
        logger.info(
            f"[INGESTION] Pipeline finished in {duration}s: "
            f"{episodes_ingested} ingested, {episodes_skipped} skipped, {episodes_failed} failed, {chunks_created_total} chunks created."
        )

        return IngestResponse(
            status="success" if episodes_failed == 0 else "partial",
            episodesDiscovered=len(discovered_docs),
            episodesIngested=episodes_ingested,
            episodesSkipped=episodes_skipped,
            episodesFailed=episodes_failed,
            chunksCreated=chunks_created_total,
            durationSeconds=duration,
            details=details,
        )

    @classmethod
    async def _find_existing_episode(
        cls, db: AsyncSession, title: str, transcript_url: str
    ) -> Optional[TranscriptMetadataModel]:
        """Queries for existing episode by title or transcript_url to ensure idempotency."""
        stmt = select(TranscriptMetadataModel).where(
            (TranscriptMetadataModel.episode_title == title) |
            (TranscriptMetadataModel.transcript_url == transcript_url)
        )
        res = await db.execute(stmt)
        return res.scalars().first()

    @classmethod
    def _discover_local_files(cls, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Reads local markdown files from configured data directory."""
        data_dir = settings.transcripts_data_dir
        if not os.path.isdir(data_dir):
            logger.warning(f"[INGESTION] Transcripts data dir does not exist: {data_dir}")
            return []

        pattern = os.path.join(data_dir, "*.md")
        files = glob.glob(pattern)
        if limit:
            files = files[:limit]

        docs: List[Dict[str, Any]] = []
        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                meta, body = cls.parse_frontmatter(content)
                docs.append({
                    "title": meta.get("title") or os.path.splitext(os.path.basename(file_path))[0],
                    "guest": meta.get("guest") or "Unknown Guest",
                    "guest_role": meta.get("guest_role"),
                    "episode_number": int(meta["episode_number"]) if meta.get("episode_number") else None,
                    "published_date": cls._parse_date(meta.get("published_date")),
                    "transcript_url": meta.get("transcript_url") or f"https://www.lennyspodcast.com/{os.path.basename(file_path)}",
                    "audio_url": meta.get("audio_url"),
                    "duration_seconds": int(meta["duration_seconds"]) if meta.get("duration_seconds") else None,
                    "summary": meta.get("summary"),
                    "body": body,
                })
            except Exception as ex:
                logger.error(f"[INGESTION] Failed to parse local file {file_path}: {ex}")

        return docs

    @classmethod
    async def _discover_github_files(cls, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetches episodes from LennysNewsletter public repository."""
        index_url = "https://raw.githubusercontent.com/LennysNewsletter/lennys-newsletterpodcastdata/main/index.json"
        docs: List[Dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(index_url)
                if r.status_code != 200:
                    logger.error(f"GitHub index fetch returned status {r.status_code}")
                    return []
                data = r.json()
                podcasts = data.get("podcasts", [])
                if limit:
                    podcasts = podcasts[:limit]

                for p in podcasts:
                    filename = p.get("filename")
                    if not filename:
                        continue
                    file_url = f"https://raw.githubusercontent.com/LennysNewsletter/lennys-newsletterpodcastdata/main/{filename}"
                    resp = await client.get(file_url)
                    if resp.status_code == 200:
                        meta, body = cls.parse_frontmatter(resp.text)
                        docs.append({
                            "title": p.get("title", meta.get("title", "Lenny's Podcast")),
                            "guest": p.get("guest", meta.get("guest", "Unknown")),
                            "guest_role": meta.get("guest_role"),
                            "episode_number": None,
                            "published_date": cls._parse_date(p.get("date")),
                            "transcript_url": p.get("post_url"),
                            "audio_url": None,
                            "duration_seconds": None,
                            "summary": p.get("description"),
                            "body": body,
                        })
        except Exception as e:
            logger.error(f"[INGESTION] Failed to discover from GitHub: {e}")

        return docs

    @staticmethod
    def _parse_date(val: Optional[str]) -> Optional[datetime]:
        if not val:
            return None
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                pass
        return None
