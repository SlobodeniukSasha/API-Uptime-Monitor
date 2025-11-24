# import pytest
#
#
# def test_create_user(client):
#     response = client.post(
#         "/users/",
#         json={"email": "test@example.com", "name": "Test User"}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["email"] == "test@example.com"
#     assert "id" in data
#
#
# def test_create_duplicate_user(client):
#     # Создаем первого пользователя
#     client.post("/users/", json={"email": "duplicate@example.com", "name": "Test"})
#
#     # Пытаемся создать второго с таким же email
#     response = client.post(
#         "/users/",
#         json={"email": "duplicate@example.com", "name": "Test2"}
#     )
#     assert response.status_code == 400
#     assert "already registered" in response.json()["detail"]
#
#
# def test_get_users(client):
#     # Создаем тестовых пользователей
#     client.post("/users/", json={"email": "user1@test.com", "name": "User1"})
#     client.post("/users/", json={"email": "user2@test.com", "name": "User2"})
#
#     response = client.get("/users/")
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) >= 2