import pytest


# ---------------------------------------------------
# Test: Create a new user
# ---------------------------------------------------
@pytest.mark.asyncio
async def test_create_user(client):
    """
    Verify that a new user can be successfully created.
    """
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


# ---------------------------------------------------
# Test: Duplicate username is rejected
# ---------------------------------------------------
@pytest.mark.asyncio
async def test_duplicate_username(client):
    """
    Ensure that creating a user with an existing username
    returns HTTP 400.
    """
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


# ---------------------------------------------------
# Test: Login returns JWT token
# ---------------------------------------------------
@pytest.mark.asyncio
async def test_login_returns_token(client):
    """
    Verify that a registered user can log in
    and receives an access token.
    """
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


# ---------------------------------------------------
# Test: User can delete their own account
# ---------------------------------------------------
@pytest.mark.asyncio
async def test_delete_user_success(client):
    """
    A user should be able to delete their own account.
    Expected result: 204 No Content
    """
    # Create user
    create = await client.post(
        "/api/users",
        json={
            "username": "deleteuser",
            "email": "delete@example.com",
            "password": "password123",
        },
    )

    user_id = create.json()["id"]

    # Login to get token
    login = await client.post(
        "/api/users/token",
        data={
            "username": "delete@example.com",
            "password": "password123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # Delete own account
    response = await client.delete(
        f"/api/users/{user_id}",
        headers=headers,
    )

    assert response.status_code == 204

    # Confirm user is gone
    get_response = await client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 404


# ---------------------------------------------------
# Test: User cannot delete another user's account
# ---------------------------------------------------
@pytest.mark.asyncio
async def test_delete_user_forbidden(client):
    """
    A user should NOT be able to delete another user's account.
    Expected result: 403 Forbidden
    """
    # First user
    user1 = await client.post(
        "/api/users",
        json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "password123",
        },
    )

    user1_id = user1.json()["id"]

    # Second user
    await client.post(
        "/api/users",
        json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
        },
    )

    login2 = await client.post(
        "/api/users/token",
        data={
            "username": "user2@example.com",
            "password": "password123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    # Second user tries to delete first user
    response = await client.delete(
        f"/api/users/{user1_id}",
        headers=headers2,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorised to delete this post"


# ---------------------------------------------------
# Test: Deleting non-existent user returns 404
# ---------------------------------------------------
@pytest.mark.asyncio
async def test_delete_user_not_found(client):
    """
    Attempting to delete another user (or non-existent user)
    should return 403 due to authorization check happening first.
    """
    # Create and login user
    await client.post(
        "/api/users",
        json={
            "username": "temp",
            "email": "temp@example.com",
            "password": "password123",
        },
    )

    login = await client.post(
        "/api/users/token",
        data={
            "username": "temp@example.com",
            "password": "password123",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # Try deleting user ID that doesn't exist
    response = await client.delete(
        "/api/users/9999",
        headers=headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorised to delete this post"