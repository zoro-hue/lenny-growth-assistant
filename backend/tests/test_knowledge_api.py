import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_knowledge_api_flow(client: AsyncClient):
    # 1. Check stats on empty DB
    res_stats = await client.get("/api/knowledge/stats")
    assert res_stats.status_code == 200
    stats_data = res_stats.json()
    assert stats_data["totalEpisodes"] == 0
    assert stats_data["totalChunks"] == 0

    # 2. Trigger ingestion via API
    res_ingest = await client.post(
        "/api/knowledge/ingest",
        json={"source": "sample", "limit": 2, "forceRefresh": True},
    )
    assert res_ingest.status_code == 200
    ingest_data = res_ingest.json()
    assert ingest_data["status"] == "success"
    assert ingest_data["episodesIngested"] == 2
    assert ingest_data["chunksCreated"] > 0

    # 3. Check stats after ingestion
    res_stats2 = await client.get("/api/knowledge/stats")
    assert res_stats2.status_code == 200
    stats_data2 = res_stats2.json()
    assert stats_data2["totalEpisodes"] == 2
    assert stats_data2["totalChunks"] == ingest_data["chunksCreated"]
    assert len(stats_data2["topGuests"]) > 0

    # 4. Search knowledge base via API
    res_search = await client.post(
        "/api/knowledge/search",
        json={"query": "retention curves and growth loops", "topK": 2},
    )
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert search_data["totalResults"] > 0
    first = search_data["results"][0]
    assert "citation" in first
    assert first["citation"]["guest"] in ("Casey Winters", "Elena Verna")
    assert first["similarityScore"] > 0.10
