from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .message import CitationSchema


class IngestRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source: Optional[str] = Field(default="sample", description="'sample' | 'local' | 'github'")
    limit: Optional[int] = Field(default=None, ge=1, le=100, description="Max episodes to ingest")
    force_refresh: Optional[bool] = Field(default=False, alias="forceRefresh")
    chunk_size: Optional[int] = Field(default=None, ge=100, le=5000, alias="chunkSize")
    chunk_overlap: Optional[int] = Field(default=None, ge=0, le=1000, alias="chunkOverlap")


class IngestResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: str
    episodes_discovered: int = Field(alias="episodesDiscovered")
    episodes_ingested: int = Field(alias="episodesIngested")
    episodes_skipped: int = Field(alias="episodesSkipped")
    episodes_failed: int = Field(alias="episodesFailed")
    chunks_created: int = Field(alias="chunksCreated")
    duration_seconds: float = Field(alias="durationSeconds")
    details: List[Dict[str, Any]] = Field(default_factory=list)


class KnowledgeStatsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    total_episodes: int = Field(alias="totalEpisodes")
    total_chunks: int = Field(alias="totalChunks")
    embedding_model: str = Field(alias="embeddingModel")
    embedding_dimensions: int = Field(alias="embeddingDimensions")
    database_engine: str = Field(alias="databaseEngine")
    last_ingested_at: Optional[str] = Field(default=None, alias="lastIngestedAt")
    top_guests: List[Dict[str, Any]] = Field(default_factory=list, alias="topGuests")


class SearchResultItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chunk_id: str = Field(alias="chunkId")
    transcript_id: str = Field(alias="transcriptId")
    episode_number: Optional[int] = Field(default=None, alias="episodeNumber")
    episode_title: str = Field(alias="episodeTitle")
    guest: str
    guest_role: Optional[str] = Field(default=None, alias="guestRole")
    source_url: Optional[str] = Field(default=None, alias="sourceUrl")
    chunk_index: int = Field(alias="chunkIndex")
    timestamp: Optional[str] = None
    content: str
    similarity_score: float = Field(alias="similarityScore")
    citation: CitationSchema

    @property
    def similarity(self) -> float:
        return self.similarity_score


class KnowledgeSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    query: str = Field(..., min_length=1, max_length=1000)
    top_k: Optional[int] = Field(default=3, ge=1, le=20, alias="topK")
    similarity_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0, alias="similarityThreshold")


class KnowledgeSearchResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    query: str
    total_results: int = Field(alias="totalResults")
    results: List[SearchResultItem]
