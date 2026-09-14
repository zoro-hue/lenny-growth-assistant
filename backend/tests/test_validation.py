import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_validation_empty_content(client: AsyncClient):
    session_res = await client.post("/api/sessions", json={"title": "Validation Test"})
    session_id = session_res.json()["id"]

    # Post message with empty content
    bad_payload = {
        "role": "user",
        "content": "",
    }
    res = await client.post(f"/api/sessions/{session_id}/messages", json=bad_payload)
    assert res.status_code == 422
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "errors" in data["error"]["details"]
    assert any("content" in e["field"] for e in data["error"]["details"]["errors"])


@pytest.mark.asyncio
async def test_nonexistent_session_not_found(client: AsyncClient):
    res = await client.get("/api/sessions/session-nonexistent-12345")
    assert res.status_code == 404
    data = res.json()
    assert data["error"]["code"] == "ENTITY_NOT_FOUND"
    assert "session-nonexistent-12345" in data["error"]["message"]


@pytest.mark.asyncio
async def test_artifact_crud_and_validation(client: AsyncClient):
    session_res = await client.post("/api/sessions", json={"title": "Artifact Test"})
    session_id = session_res.json()["id"]

    # 1. Create artifact with valid payload
    art_payload = {
        "sessionId": session_id,
        "title": "B2B Expansion Playbook",
        "type": "markdown",
        "content": "# B2B Expansion Playbook\n\nOperational guidelines for PLG.",
        "wordCount": 7,
        "sourceCount": 2,
    }
    create_res = await client.post("/api/artifacts", json=art_payload)
    assert create_res.status_code == 201
    art_data = create_res.json()
    art_id = art_data["id"]
    assert art_data["title"] == "B2B Expansion Playbook"
    assert art_data["allowScripts"] is False

    # 2. Update artifact title & toggle scripts
    update_res = await client.patch(
        f"/api/artifacts/{art_id}",
        json={"title": "Renamed Playbook", "allowScripts": True},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Renamed Playbook"
    assert update_res.json()["allowScripts"] is True

    # 3. Retrieve artifact
    get_res = await client.get(f"/api/artifacts/{art_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Renamed Playbook"
