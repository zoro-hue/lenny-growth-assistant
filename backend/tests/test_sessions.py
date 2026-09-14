import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_retrieve_session(client: AsyncClient):
    # 1. Create a session
    payload = {
        "title": "B2B SaaS Retention Strategy",
        "activeModelId": "openai-cloud",
    }
    response = await client.post("/api/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()
    session_id = data["id"]
    assert session_id.startswith("session-")
    assert data["title"] == "B2B SaaS Retention Strategy"
    assert data["activeModelId"] == "openai-cloud"
    assert data["messageCount"] == 0

    # 2. Retrieve the session by ID
    get_res = await client.get(f"/api/sessions/{session_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["id"] == session_id
    assert detail["title"] == "B2B SaaS Retention Strategy"
    assert detail["messages"] == []
    assert detail["artifacts"] == []


@pytest.mark.asyncio
async def test_list_and_rename_session(client: AsyncClient):
    # Create two sessions
    res1 = await client.post("/api/sessions", json={"title": "Session Alpha"})
    res2 = await client.post("/api/sessions", json={"title": "Session Beta"})
    id1 = res1.json()["id"]
    id2 = res2.json()["id"]

    # List sessions
    list_res = await client.get("/api/sessions")
    assert list_res.status_code == 200
    sessions = list_res.json()
    ids = [s["id"] for s in sessions]
    assert id1 in ids
    assert id2 in ids

    # Rename Session Alpha
    patch_res = await client.patch(f"/api/sessions/{id1}", json={"title": "Renamed Alpha"})
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Renamed Alpha"

    # Verify updated title in get
    detail_res = await client.get(f"/api/sessions/{id1}")
    assert detail_res.json()["title"] == "Renamed Alpha"


@pytest.mark.asyncio
async def test_delete_session(client: AsyncClient):
    create_res = await client.post("/api/sessions", json={"title": "To Delete"})
    session_id = create_res.json()["id"]

    # Delete
    del_res = await client.delete(f"/api/sessions/{session_id}")
    assert del_res.status_code == 204

    # Verify 404 on get
    get_res = await client.get(f"/api/sessions/{session_id}")
    assert get_res.status_code == 404
    err = get_res.json()
    assert err["error"]["code"] == "ENTITY_NOT_FOUND"
