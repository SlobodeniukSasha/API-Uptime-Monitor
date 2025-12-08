import pytest
import pytest_asyncio
from starlette import status


@pytest_asyncio.fixture
def user_data():
    return {
        "email": "test@gmail.com",
        "password": "secret123",
        "full_name": "Test User"
    }


@pytest_asyncio.fixture
async def authenticated_client(client, user_data):
    await client.post("/auth/register/", json=user_data)

    user_login_data = {'email': 'test@gmail.com', "password": "secret123"}

    response = await client.post("/auth/login/", json=user_login_data)
    assert response.status_code == status.HTTP_200_OK

    access_token = response.json().get('access_token')
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client


@pytest.mark.asyncio
async def test_create_monitor(client, authenticated_client):
    payload = {
        "url": "http://example.com",
        "name": "example",
        "expected_status_code": 200,
        "check_interval": 60
    }

    response = await client.post("/monitors/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "example"
    assert data["expected_status_code"] == 200
    assert "id" in data


@pytest.mark.asyncio
async def test_get_monitors(client, authenticated_client):
    response = await client.get("/monitors/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_single_monitor(client, authenticated_client):
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
async def test_delete_monitor(client, authenticated_client):
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
