import pytest


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_duplicate_username(client):
    user = {
        "username": "duplicate",
        "email": "dup1@example.com",
        "password": "password123",
    }

    # Create initial user
    await client.post("/api/users", json=user)

    # Attempt duplicate username
    response = await client.post(
        "/api/users",
        json={
            "username": "duplicate",
            "email": "dup2@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


@pytest.mark.asyncio
async def test_login_returns_token(client):
    # Create user for login test
    await client.post(
        "/api/users",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "password123",
        },
    )

    response = await client.post(
        "/api/users/token",
        data={
            "username": "login@example.com",
            "password": "password123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()