import pytest
from sqlalchemy import select
from starlette import status

from backend.app.models import User


@pytest.fixture
def user_data():
    return {
        "email": "test2@gmail.com",
        "password": "secret123",
        "full_name": "Test User"
    }


@pytest.mark.asyncio
class TestUserModel:
    async def test_create_user(self, user_data, client, async_session):
        response = await client.post('/auth/register/', json=user_data)

        user = await async_session.execute(select(User).where(User.email == "test2@gmail.com"))
        assert user
        assert response.status_code == status.HTTP_201_CREATED

    async def test_create_duplicate_user(self, user_data, client):
        response = await client.post('/auth/register/', json=user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_protected_endpoint_by_unauthorized_user(client):
    response = await client.get(url='/monitors/')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_protected_endpoint_by_authorized_user(client):
    user_login_data = {'email': 'test2@gmail.com', "password": "secret123"}
    login_response = await client.post(url='/auth/login/', json=user_login_data)

    assert login_response.status_code == status.HTTP_200_OK

    access_token = login_response.json().get('access_token')

    response = await client.get(url='/monitors/', headers={'Authorization': f'Bearer {access_token}'})

    assert response.status_code == status.HTTP_200_OK
