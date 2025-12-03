import pytest


@pytest.mark.asyncio
async def test_create_monitor(client):
    payload = {
        "url": "http://example.com",
        "name": "example",
        "expected_status_code": 200,
        "check_interval": 60
    }

    response = await client.post("/monitors/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "example"
    assert data["expected_status_code"] == 200
    assert "id" in data


@pytest.mark.asyncio
async def test_get_monitors(client):
    response = await client.get("/monitors/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_single_monitor(client):
    create_resp = await client.post("/monitors/", json={
        "url": "http://google.com",
        "name": "google",
        "expected_status_code": 200,
        "check_interval": 60
    })

    m_id = create_resp.json()["id"]

    get_resp = await client.get(f"/monitors/{m_id}/")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == m_id


@pytest.mark.asyncio
async def test_delete_monitor(client):
    create_resp = await client.post("/monitors/", json={
        "url": "http://delete.com",
        "name": "delete-me",
        "expected_status_code": 200,
        "check_interval": 60
    })

    m_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/monitors/{m_id}/")
    assert delete_resp.status_code == 200

    get_resp = await client.get(f"/monitors/{m_id}/")
    assert get_resp.status_code == 404
